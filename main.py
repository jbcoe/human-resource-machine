import typing


Value = typing.Union[int, str]


class Comment:
    def __init__(self, text: str):
        self.text = text


class Inbox:
    pass


class Outbox:
    pass


class Add:
    def __init__(self, register: Value, indirect: bool = False):
        self.register = register
        self.indirect = indirect


class Subtract:
    def __init__(self, register: Value, indirect: bool = False):
        self.register = register
        self.indirect = indirect


class CopyTo:
    def __init__(self, register: Value, indirect: bool = False):
        self.register = register
        self.indirect = indirect


class CopyFrom:
    def __init__(self, register: Value, indirect: bool = False):
        self.register = register
        self.indirect = indirect


class JumpTarget:
    def __init__(self, label: str):
        self.label = label


class Jump:
    def __init__(self, label: str):
        self.label = label


class JumpIfZero:
    def __init__(self, label: str):
        self.label = label


class JumpIfNegative:
    def __init__(self, label: str):
        self.label = label


class BumpPlus:
    def __init__(self, register: Value, indirect: bool = False):
        self.register = register
        self.indirect = indirect


class BumpMinus:
    def __init__(self, register: Value, indirect: bool = False):
        self.register = register
        self.indirect = indirect


Instruction = typing.Union[
    Comment,
    Inbox,
    Outbox,
    Add,
    Subtract,
    CopyTo,
    CopyFrom,
    JumpTarget,
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
                case JumpTarget() | Comment():
                    pass
                case _:
                    self.instruction_count += 1

        jumps: dict[str, int] = {}
        for index, instruction in enumerate(self.instructions):
            match instruction:
                case JumpTarget():
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
                case JumpTarget() | Comment():
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
        JumpTarget("BEGIN"),
        Inbox(),
        CopyTo(12),
        CopyFrom(12, indirect=True),
        Outbox(),
        Jump("BEGIN"),
    ]
    interpreter.execute_program([6, 2, 0, 3, 4])
    for value in interpreter.output:
        print(value)
    print("Execution count:", interpreter.executions)
    print("Instruction count:", interpreter.instruction_count)


if __name__ == "__main__":
    main()
