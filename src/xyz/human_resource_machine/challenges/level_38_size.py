from xyz.human_resource_machine.interpreter import (
    BumpPlus,
    JumpIfZero,
    Value,
    Label,
    Inbox,
    Instruction,
    Outbox,
    CopyTo,
    CopyFrom,
    Jump,
    Comment,
    JumpIfNegative,
    Subtract,
)

NAME = "Digit Exploder"

REGISTERS: dict[Value, Value] = {
    "0": 0,
    "10": 10,
    "100": 100,
}

INPUT: list[Value] = [1, 982, 39, 235]

SIZE_CHALLENGE = 30

SPEED_CHALLENGE = 165

# fmt: off
INSTRUCTIONS: list[Instruction] = [
    ### BEGIN
    Label("BEGIN"),
    CopyFrom("10"),
    CopyTo("big digit"),
    Inbox(),
    CopyTo("x"),
    Comment("Is < 10?"),
    Subtract("10"),
    JumpIfNegative("Write Units"),
    Comment("Is < 100?"),
    Subtract("100"),
    JumpIfNegative("Write tens"),
    CopyFrom("100"),
    CopyTo("big digit"),
    Jump("Write hundreds"),

    ### Big Digit
    Label("Write tens"),
    CopyFrom("10"),
    CopyTo("big digit"),

    Label("Write hundreds"),
    CopyFrom("0"),
    CopyTo("digit"),
    CopyFrom("x"),
    Comment("Get big digit"),
    Label("Loop in big digit"),
      Subtract("big digit"),
      JumpIfNegative("Write big digit"),
      CopyTo("x"),
      BumpPlus("digit"),
      CopyFrom("x"),
      Jump("Loop in big digit"),
    Label("Write big digit"),
    CopyFrom("digit"),
    Outbox(),

    CopyFrom("100"),
    Subtract("big digit"),
    JumpIfZero("Write tens"),

    ### UNITS
    Label("Write Units"),
    CopyFrom("x"),
    Outbox(),
    Jump("BEGIN"),
]
# fmt: on
