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
    def __init__(self, instructions: list[Instruction] | None = None):
        self.instructions: list[Instruction] = instructions or []
        self._value: int | None = None
        self._registers: dict[Value, Value] = {}
        self._instruction_index: int = 0
        self._input_index: int = 0
        self._output: list[Value] = []

    def execute_program(self, input: list[Value]) -> None:
        self.__init__(self.instructions)

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
                case Outbox():
                    if self._value is None:
                        raise ValueError("No value to output")
                    self._output.append(self._value)
                    self._value = None
                    self._instruction_index += 1
                case Add() as add_:
                    if add_.indirect:
                        argument: Value = self._registers[
                            self._registers[add_.register]
                        ]
                    else:
                        argument = self._registers[add_.register]
                    self._value += argument
                    self._instruction_index += 1
                case Subtract() as subtract_:
                    if subtract_.indirect:
                        argument: Value = self._registers[
                            self._registers[subtract_.register]
                        ]
                    else:
                        argument = self._registers[subtract_.register]
                    self._value += argument
                    self._instruction_index += 1
                case CopyTo() as copy_to:
                    if copy_to.indirect:
                        self._registers[self._registers[copy_to.register]] = self._value
                    else:
                        self._registers[copy_to.register] = self._value
                    self._instruction_index += 1
                case CopyFrom() as copy_from:
                    if copy_from.indirect:
                        argument: Value = self._registers[
                            self._registers[copy_from.register]
                        ]
                    else:
                        argument = self._registers[copy_from.register, 0]
                    self._value = argument
                    self._instruction_index += 1
                case JumpTarget() | Comment():
                    self._instruction_index += 1
                case Jump() as jump:
                    self._instruction_index = jumps[jump.label]
                case JumpIfZero() as jump:
                    if self._value == 0:
                        self._instruction_index = jumps[jump.label]
                    else:
                        self._instruction_index += 1
                case JumpIfNegative() as jump:
                    if self._value < 0:
                        self._instruction_index = jumps[jump.label]
                    else:
                        self._instruction_index += 1
                case BumpPlus() as bump_plus:
                    if bump_plus.indirect:
                        self._registers[self._registers[bump_plus.register]] += 1
                        self._value = self._registers[
                            self._registers[bump_plus.register]
                        ]
                    else:
                        self._registers[bump_plus.register] += 1
                        self._value = self._registers[bump_plus.register]
                    self._instruction_index += 1
                case BumpMinus() as bump_minus:
                    if bump_minus.indirect:
                        self._registers[self._registers[bump_minus.register]] -= 1
                        self._value = self._registers[
                            self._registers[bump_minus.register]
                        ]
                    else:
                        self._registers[bump_minus.register] -= 1
                        self._value = self._registers[bump_minus.register]
                    self._instruction_index += 1

    @property
    def output(self) -> list[Value]:
        return self._output.copy()


def main():
    interpreter = Interpreter()
    interpreter.instructions = [
        JumpTarget("BEGIN"),
        Inbox(),
        CopyTo(0),
        Inbox(),
        Add(0),
        Outbox(),
        Jump("BEGIN"),
    ]
    interpreter.execute_program([1, 20, 3, -4, 100, 5])
    for value in interpreter.output:
        print(value)


if __name__ == "__main__":
    main()
