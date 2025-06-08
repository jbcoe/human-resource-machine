import logging
import typing
from dataclasses import dataclass

logger = logging.getLogger(__name__)

Value = typing.Union[int, str]


def int_or_str(value: str) -> Value:
    """Convert a string to an int if possible, otherwise return the string."""
    try:
        return int(value)
    except ValueError:
        return value


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
        logger.debug("Instruction %d: %s", self._instruction_index, instruction)
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

    def to_dot(self) -> str:
        """Return the program instructions in dotfile format."""
        lines: list[str] = ["digraph G {"]
        node_map: dict[int, str] = {}
        # First pass: define nodes and labels for actual instructions
        idx_counter = 0
        for i, instruction in enumerate(self.instructions):
            match instruction:
                case Comment():
                    # Comments are not nodes in the graph
                    pass
                case Label() as label_instr:
                    # Labels point to the next actual instruction
                    node_map[i] = f'"{label_instr.label}"'
                    lines.append(f"  {node_map[i]} [shape=plaintext];")
                case _:
                    node_id = f"instr_{idx_counter}"
                    node_map[i] = node_id
                    # Sanitize instruction string for dot format
                    instr_str = str(instruction).replace(
                        '"', '\\"'
                    )  # Corrected sanitization
                    shape = "box"
                    if isinstance(instruction, (Jump, JumpIfZero, JumpIfNegative)):
                        shape = "diamond"
                    lines.append(
                        f'  {node_id} [shape={shape}, label="{idx_counter}: {instr_str}"];'
                    )
                    idx_counter += 1

        # Second pass: define edges
        for i, instruction in enumerate(self.instructions):
            if i not in node_map:  # Skip comments
                continue

            current_node_id = node_map[i]

            # Determine the actual next instruction index, skipping comments
            actual_next_instr_idx = i + 1
            while actual_next_instr_idx < len(self.instructions) and isinstance(
                self.instructions[actual_next_instr_idx], Comment
            ):
                actual_next_instr_idx += 1

            # Default sequential flow (if not a jump or label that only points elsewhere)
            if not isinstance(instruction, (Jump, JumpIfZero, JumpIfNegative, Label)):
                if (
                    actual_next_instr_idx < len(self.instructions)
                    and actual_next_instr_idx in node_map
                ):
                    lines.append(
                        f"  {current_node_id} -> {node_map[actual_next_instr_idx]};"
                    )
            elif isinstance(
                instruction, Label
            ):  # Labels should point to the next instruction
                if (
                    actual_next_instr_idx < len(self.instructions)
                    and actual_next_instr_idx in node_map
                ):
                    lines.append(
                        f"  {current_node_id} -> {node_map[actual_next_instr_idx]};"
                    )

            match instruction:
                case Jump() as jump_instr:
                    target_idx = self._jumps.get(jump_instr.label)
                    if target_idx is not None and target_idx in node_map:
                        lines.append(f"  {current_node_id} -> {node_map[target_idx]};")
                case JumpIfZero() as jump_if_zero_instr:
                    target_idx = self._jumps.get(jump_if_zero_instr.label)
                    if target_idx is not None and target_idx in node_map:
                        lines.append(
                            f'  {current_node_id} -> {node_map[target_idx]} [label="if zero"];'
                        )
                    # Edge for not jumping (sequential)
                    if (
                        actual_next_instr_idx < len(self.instructions)
                        and actual_next_instr_idx in node_map
                    ):
                        lines.append(
                            f'  {current_node_id} -> {node_map[actual_next_instr_idx]} [label="not zero"];'
                        )
                case JumpIfNegative() as jump_if_negative_instr:
                    target_idx = self._jumps.get(jump_if_negative_instr.label)
                    if target_idx is not None and target_idx in node_map:
                        lines.append(
                            f'  {current_node_id} -> {node_map[target_idx]} [label="if negative"];'
                        )
                    # Edge for not jumping (sequential)
                    if (
                        actual_next_instr_idx < len(self.instructions)
                        and actual_next_instr_idx in node_map
                    ):
                        lines.append(
                            f'  {current_node_id} -> {node_map[actual_next_instr_idx]} [label="not negative"];'
                        )
                # For other instructions like Inbox, Outbox, Add, Subtract, CopyTo, CopyFrom, BumpPlus, BumpMinus,
                # the default sequential link is already added above if they are not jumps or labels.
                # No special edge logic needed here for them beyond the default.
                case _:
                    pass

        lines.append("}")
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
