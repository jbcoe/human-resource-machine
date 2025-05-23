from xyz.human_resource_machine.interpreter import (
    BumpPlus,
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
    Inbox(),
    CopyTo("x"),
    Comment("Is < 10?"),
    Subtract("10"),
    JumpIfNegative("Write Units"),
    Comment("Is < 100?"),
    Subtract("100"),
    JumpIfNegative("Tens"),

    ### HUNDREDS
    Comment("Hundreds Initialization"),
    CopyFrom("0"),
    CopyTo("digit"),
    BumpPlus("digit"),
    CopyFrom("x"),
    Subtract("100"),
    Comment("Hundreds: Get hundreds digit"),
    Label("Loop in Hundreds"),
      Subtract("100"),
      JumpIfNegative("Write Hundreds"),
      CopyTo("x"),
      BumpPlus("digit"),
      CopyFrom("x"),
      Jump("Loop in Hundreds"),
    Label("Write Hundreds"),
    CopyFrom("digit"),
    Outbox(),

    ### TENS
    Label("Tens"),
    Comment("Tens Initialization"),
    CopyFrom("0"),
    CopyTo("digit"),
    CopyFrom("x"),
    Comment("Tens: Get tens digit"),
    Label("Loop in Tens"),
      Subtract("10"),
      JumpIfNegative("Write Tens"),
      CopyTo("x"),
      BumpPlus("digit"),
      CopyFrom("x"),
      Jump("Loop in Tens"),
    Label("Write Tens"),
    CopyFrom("digit"),
    Outbox(),

    ### UNITS
    Label("Write Units"),
    CopyFrom("x"),
    Outbox(),
    Jump("BEGIN"),
]
# fmt: on
