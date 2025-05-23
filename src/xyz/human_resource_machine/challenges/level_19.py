from xyz.human_resource_machine.interpreter import (
    Value,
    Label,
    Inbox,
    Instruction,
    Outbox,
    CopyTo,
    CopyFrom,
    Jump,
)

REGISTERS: dict[Value, Value] = {
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

INSTRUCTIONS: list[Instruction] = [
    Label("BEGIN"),
    Inbox(),
    CopyTo(12),
    CopyFrom(12, indirect=True),
    Outbox(),
    Jump("BEGIN"),
]

INPUT: list[Value] = [6, 2, 0, 3, 4]
