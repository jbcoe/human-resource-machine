import typing
from dataclasses import dataclass

Value = typing.Union[int, str]


@dataclass(frozen=True, slots=True)
class _UsesRegister:
    register: Value
    indirect: bool = False


@dataclass(frozen=True, slots=True)
class Comment:
    text: str


@dataclass(frozen=True, slots=True)
class Inbox:
    pass


@dataclass(frozen=True, slots=True)
class Outbox:
    pass


@dataclass(frozen=True, slots=True)
class Add(_UsesRegister):
    pass


@dataclass(frozen=True, slots=True)
class Subtract(_UsesRegister):
    pass


@dataclass(frozen=True, slots=True)
class CopyTo(_UsesRegister):
    pass


@dataclass(frozen=True, slots=True)
class CopyFrom(_UsesRegister):
    pass


@dataclass(frozen=True, slots=True)
class BumpPlus(_UsesRegister):
    pass


@dataclass(frozen=True, slots=True)
class BumpMinus(_UsesRegister):
    pass


@dataclass(frozen=True, slots=True)
class Label:
    label: str


@dataclass(frozen=True, slots=True)
class Jump:
    label: str


@dataclass(frozen=True, slots=True)
class JumpIfZero:
    label: str


@dataclass(frozen=True, slots=True)
class JumpIfNegative:
    label: str


@dataclass(frozen=True, slots=True)
class AssertValueIs:
    """This instruction does not exist in the original game, but is useful for testing."""

    value: Value


@dataclass(frozen=True, slots=True)
class AssertRegisterIs:
    """This instruction does not exist in the original game, but is useful for testing."""

    register: str
    value: Value


Instruction = typing.Union[
    Comment,
    Inbox,
    Outbox,
    Add,
    Subtract,
    CopyTo,
    CopyFrom,
    BumpPlus,
    BumpMinus,
    Label,
    Jump,
    JumpIfZero,
    JumpIfNegative,
    AssertValueIs,
]


class Interpreter:
    def __init__(
        self,
        *,
        registers: dict[Value, Value] | None = None,
        instructions: list[Instruction] | None = None,
        input: list[Value] | None = None,
    ):
        self.instructions = [] if instructions is None else instructions.copy()
        self.registers = {} if registers is None else registers.copy()
        self.instruction_count: int = 0
        self._value: int | None = None
        self._input = [] if input is None else input
        self._input_index: int = 0
        self._execution_count: int = 0
        self._instruction_index: int = 0
        self._output: list[Value] = []

        self.instruction_count = 0
        for instruction in self.instructions:
            match instruction:
                case Label() | Comment():
                    pass
                case _:
                    self.instruction_count += 1

        self._jumps: dict[str, int] = {}
        for index, instruction in enumerate(self.instructions):
            match instruction:
                case Label():
                    self._jumps[instruction.label] = index
                case _:
                    pass

    def _read_register(self, instruction: _UsesRegister) -> Value:
        """Read the value from the register, handling indirect addressing."""
        if instruction.indirect:
            return self.registers[self.registers[instruction.register]]
        return self.registers[instruction.register]

    def _write_register(self, instruction: _UsesRegister) -> None:
        """Write the value to the register, handling indirect addressing."""
        if instruction.indirect:
            self.registers[self.registers[instruction.register]] = self._value
        else:
            self.registers[instruction.register] = self._value

    def execute_program(self) -> list[Value]:
        """Execute all the instructions in the program until completion."""
        while self._instruction_index < len(self.instructions):
            return_value = self.step()
            if return_value is not None:
                return return_value
        return self.output

    def step(self) -> list[Value] | None:
        """Execute the next instruction in the program."""
        instruction = self.instructions[self._instruction_index]
        match instruction:
            case Inbox():
                if self._input_index >= len(self._input):
                    return self.output  # No more input available.
                self._value = self._input[self._input_index]
                self._input_index += 1
                self._instruction_index += 1
                self._execution_count += 1
            case Outbox():
                if self._value is None:
                    raise ValueError("No value to output")
                self._output.append(self._value)
                self._value = None
                self._instruction_index += 1
                self._execution_count += 1
            case Add() as add_:
                if not isinstance(self._value, int):
                    raise ValueError(
                        f"Value {self._value} must be an integer for addition"
                    )
                argument = self._read_register(add_)
                if not isinstance(argument, int):
                    raise ValueError(
                        f"Argument {argument} must be an integer for addition"
                    )
                self._value += argument
                self._instruction_index += 1
                self._execution_count += 1
            case Subtract() as subtract_:
                if not isinstance(self._value, int):
                    raise ValueError(
                        f"Value {self._value} must be an integer for subtraction"
                    )
                argument = self._read_register(subtract_)
                if not isinstance(argument, int):
                    raise ValueError(
                        f"Argument {argument} must be an integer for subtraction"
                    )
                self._value -= argument
                self._instruction_index += 1
                self._execution_count += 1
            case CopyTo() as copy_to:
                self._write_register(copy_to)
                self._instruction_index += 1
                self._execution_count += 1
            case CopyFrom() as copy_from:
                register_value = self._read_register(copy_from)
                self._value = register_value
                self._instruction_index += 1
                self._execution_count += 1
            case BumpPlus() as bump_plus:
                if bump_plus.indirect:
                    self.registers[self.registers[bump_plus.register]] += 1
                    self._value = self.registers[self.registers[bump_plus.register]]
                else:
                    self.registers[bump_plus.register] += 1
                    self._value = self.registers[bump_plus.register]
                self._instruction_index += 1
                self._execution_count += 1
            case BumpMinus() as bump_minus:
                if bump_minus.indirect:
                    self.registers[self.registers[bump_minus.register]] -= 1
                    self._value = self.registers[self.registers[bump_minus.register]]
                else:
                    self.registers[bump_minus.register] -= 1
                    self._value = self.registers[bump_minus.register]
                self._instruction_index += 1
                self._execution_count += 1
            case Label() | Comment():
                self._instruction_index += 1
                # No execution count increment for comments or jump targets.
            case Jump() as jump:
                self._instruction_index = self._jumps[jump.label]
                self._execution_count += 1
            case JumpIfZero() as jump:
                if self._value == 0:
                    self._instruction_index = self._jumps[jump.label]
                else:
                    self._instruction_index += 1
                self._execution_count += 1
            case JumpIfNegative() as jump:
                if self._value < 0:
                    self._instruction_index = self._jumps[jump.label]
                else:
                    self._instruction_index += 1
                self._execution_count += 1
            case AssertValueIs() as assert_value:
                if self._value != assert_value.value:
                    raise ValueError(
                        f"Assertion failed: expected {assert_value.value}, got {self._value}"
                    )
                self._instruction_index += 1
            case AssertRegisterIs() as assert_register:
                if self.registers[assert_register.register] != assert_register.value:
                    raise ValueError(
                        f"Assertion failed: expected register '{assert_register.register}' to be {assert_register.value}, got {self.registers[assert_register.register]}"
                    )
                self._instruction_index += 1

    def to_str(self) -> str:
        lines: list[str] = []
        index: int = 1

        for instruction in self.instructions:
            match instruction:
                case AssertValueIs() | AssertRegisterIs():
                    continue
                case Comment() as comment:
                    lines.append(f'"{comment.text}"')
                case Label() as label:
                    lines.append(f"LABEL: {label.label}")
                case _ as instruction:
                    lines.append(f"{index}: {instruction}")
                    index += 1
        return "\n".join(lines)

    @property
    def value(self) -> Value | None:
        return self._value

    def register(self, value: Value) -> Value | None:
        return self.registers.get(value)

    @property
    def output(self) -> list[Value]:
        return self._output.copy()

    @property
    def executions(self) -> int:
        return self._execution_count

    @property
    def instruction_index(self) -> int:
        return self._instruction_index
