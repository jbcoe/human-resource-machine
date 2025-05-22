import typing


class Inbox:
    pass


class Outbox:
    pass


class Add:
    def __init__(self, register: str):
        self.register = register


class Subtract:
    def __init__(self, register: str):
        self.register = register


class CopyTo:
    def __init__(self, register: str):
        self.register = register


class CopyFrom:
    def __init__(self, register: str):
        self.register = register


class JumpTarget:
    def __init__(self, label: str):
        self.label = label

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        if not isinstance(other, JumpTarget):
            return False
        return self.label == other.label


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
    def __init__(self, register: str):
        self.register = register


class BumpMinus:
    def __init__(self, register: str):
        self.register = register


Instruction = typing.Union[
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
    def __init__(self, instructions: list[Instruction]|None = None):
        self.instructions:list[Instruction] = instructions or []
        self._value: int | None = None
        self._registers: dict[str, int | str] = {}
        self._instruction_index: int = 0
        self._input_index: int = 0
        self._output: list[int | str] = []

    def execute_program(self, input: list[int | str]) -> None:
        self.__init__(self.instructions)

        jumps: dict[JumpTarget, int] = {}
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
                        return # No more input available.
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
                    if self._value is None:
                        raise ValueError("No value to add to")
                    argument: int|str|None = self._registers.get(add_.register, 0)
                    if argument is None:
                        raise ValueError(f"Register {add_.register} has no value")
                    self._value += argument
                    self._instruction_index += 1
                case Subtract() as subtract_:
                    if self._value is None:
                        raise ValueError("No value to add to")
                    argument: int|str|None = self._registers.get(subtract_.register, 0)
                    if argument is None:
                        raise ValueError(f"Register {subtract_.register} has no value")
                    self._value -= argument
                    self._instruction_index += 1
                case CopyTo() as copy_to:
                    self._registers[copy_to.register] = self._value
                    self._instruction_index += 1
                case CopyFrom() as copy_from:
                    argument: int|str|None = self._registers.get(copy_from.register, 0)
                    if argument is None:
                        raise ValueError(f"Register {copy_from.register} has no value")
                    self._value = argument
                    self._instruction_index += 1
                case JumpTarget():
                    # This is a no-op, just a label
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
                    if bump_plus.register not in self._registers:
                         raise ValueError(f"Register {bump_plus.register} has no value")
                    self._registers[bump_plus.register] += 1
                    self._value = self._registers[bump_plus.register]
                    self._instruction_index += 1
                case BumpMinus() as bump_minus:
                    if bump_minus.register not in self._registers:
                         raise ValueError(f"Register {bump_minus.register} has no value")
                    self._registers[bump_minus.register] -= 1
                    self._value = self._registers[bump_minus.register]
                    self._instruction_index += 1

    @property
    def output(self) -> list[int | str]:
        return self._output.copy()


def main():
    interpreter = Interpreter()
    interpreter.instructions = [
        JumpTarget("BEGIN"),
        Inbox(),
        CopyTo("a"),
        Inbox(),
        Add("a"),
        Outbox(),
        Jump("BEGIN"),
    ]
    interpreter.execute_program([1, 2, 3, 4])
    for value in interpreter.output:
        print(value)


if __name__ == "__main__":
    main()
