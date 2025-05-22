from dataclasses import dataclass
import typing


Value = typing.Union[int, str]


@dataclass(frozen=True)
class Comment:
    text: str


@dataclass(frozen=True)
class Inbox:
    pass


@dataclass(frozen=True)
class Outbox:
    pass


@dataclass(frozen=True)
class Add:
    register: Value
    indirect: bool = False


@dataclass(frozen=True)
class Subtract:
    register: Value
    indirect: bool = False


@dataclass(frozen=True)
class CopyTo:
    register: Value
    indirect: bool = False


@dataclass(frozen=True)
class CopyFrom:
    register: Value
    indirect: bool = False


@dataclass(frozen=True)
class Label:
    label: str


@dataclass(frozen=True)
class Jump:
    label: str


@dataclass(frozen=True)
class JumpIfZero:
    label: str


@dataclass(frozen=True)
class JumpIfNegative:
    label: str


@dataclass(frozen=True)
class BumpPlus:
    register: Value
    indirect: bool = False


@dataclass(frozen=True)
class BumpMinus:
    register: Value
    indirect: bool = False


Instruction = typing.Union[
    Comment,
    Inbox,
    Outbox,
    Add,
    Subtract,
    CopyTo,
    CopyFrom,
    Label,
    Jump,
    JumpIfZero,
    JumpIfNegative,
    BumpPlus,
    BumpMinus,
]


class Interpreter:
    def __init__(
        self,
        *,
        registers: dict[Value, Value] | None = None,
        instructions: list[Instruction] | None = None,
    ):
        self.instructions: list[Instruction] = instructions or []
        self.registers = registers or {}
        self.instruction_count: int = 0
        self._value: int | None = None
        self._instruction_index: int = 0
        self._input_index: int = 0
        self._output: list[Value] = []
        self._execution_count: int = 0

    def execute_program(self, input: list[Value]) -> None:
        self.__init__(instructions=self.instructions, registers=self.registers)

        self.instruction_count = 0
        for instruction in self.instructions:
            match instruction:
                case Label() | Comment():
                    pass
                case _:
                    self.instruction_count += 1

        jumps: dict[str, int] = {}
        for index, instruction in enumerate(self.instructions):
            match instruction:
                case Label():
                    jumps[instruction.label] = index
                case _:
                    pass

        while self._instruction_index < len(self.instructions):
            instruction = self.instructions[self._instruction_index]
            match instruction:
                case Inbox():
                    if self._input_index >= len(input):
                        return  # No more input available.
                    self._value = input[self._input_index]
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
                    if add_.indirect:
                        argument: Value = self.registers[self.registers[add_.register]]
                    else:
                        argument = self.registers[add_.register]
                    self._value += argument
                    self._instruction_index += 1
                    self._execution_count += 1
                case Subtract() as subtract_:
                    if subtract_.indirect:
                        argument: Value = self.registers[
                            self.registers[subtract_.register]
                        ]
                    else:
                        argument = self.registers[subtract_.register]
                    self._value -= argument
                    self._instruction_index += 1
                    self._execution_count += 1
                case CopyTo() as copy_to:
                    if copy_to.indirect:
                        self.registers[self.registers[copy_to.register]] = self._value
                    else:
                        self.registers[copy_to.register] = self._value
                    self._instruction_index += 1
                    self._execution_count += 1
                case CopyFrom() as copy_from:
                    if copy_from.indirect:
                        argument: Value = self.registers[
                            self.registers[copy_from.register]
                        ]
                    else:
                        argument = self.registers[copy_from.register]
                    self._value = argument
                    self._instruction_index += 1
                    self._execution_count += 1
                case Label() | Comment():
                    self._instruction_index += 1
                    # No execution count increment for comments or jump targets.
                case Jump() as jump:
                    self._instruction_index = jumps[jump.label]
                    self._execution_count += 1
                case JumpIfZero() as jump:
                    if self._value == 0:
                        self._instruction_index = jumps[jump.label]
                    else:
                        self._instruction_index += 1
                    self._execution_count += 1
                case JumpIfNegative() as jump:
                    if self._value < 0:
                        self._instruction_index = jumps[jump.label]
                    else:
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
                        self._value = self.registers[
                            self.registers[bump_minus.register]
                        ]
                    else:
                        self.registers[bump_minus.register] -= 1
                        self._value = self.registers[bump_minus.register]
                    self._instruction_index += 1
                    self._execution_count += 1

    def to_str(self) -> str:
        lines: list[str] = []
        index: int = 1

        for instruction in self.instructions:
            match instruction:
                case Comment() as comment:
                    lines.append(f"{comment.text}")
                case Label() as label:
                    lines.append(f"LABEL: {label.label}")
                case _ as instruction:
                    lines.append(f"{index}: {instruction}")
                    index += 1
        return "\n".join(lines)

    @property
    def output(self) -> list[Value]:
        return self._output.copy()

    @property
    def executions(self) -> int:
        return self._execution_count


def main():
    interpreter = Interpreter()
    interpreter.registers = {
        0: "N",
        1: "K",
        2: "A",
        3: "E",
        4: "R",
        5: "D",
        6: "O",
        7: "L",
        8: "Y",
        9: "J",
        12: 8,
    }
    interpreter.instructions = [
        Label("BEGIN"),
        Inbox(),
        CopyTo(12),
        CopyFrom(12, indirect=True),
        Outbox(),
        Jump("BEGIN"),
    ]
    input = [6, 2, 0, 3, 4]
    interpreter.execute_program(input)
    print(interpreter.to_str(),"\n")
    print("Registers:", interpreter.registers)
    print("Input: ", input)
    print("Output:", ", ".join(interpreter.output))
    print("Execution count:", interpreter.executions)
    print("Instruction count:", interpreter.instruction_count)


if __name__ == "__main__":
    main()
