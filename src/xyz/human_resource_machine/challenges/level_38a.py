from xyz.human_resource_machine.interpreter import (
    Add,
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
    ### INITIALIZATION
    CopyFrom("10"),
    Add("100"),
    CopyTo("110"),

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
    Comment("Unrolled loop in 100s"),
      # 1
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 1"),
      CopyTo("x"),
      # 2
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 2"),
      CopyTo("x"),
      # 3
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 3"),
      CopyTo("x"),
      # 4
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 4"),
      CopyTo("x"),
      # 5
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 5"),
      CopyTo("x"),
      # 6
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 6"),
      CopyTo("x"),
      # 7
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 7"),
      CopyTo("x"),
      # 8
      Subtract("100"),
      JumpIfNegative("Write Hundreds: 8"),
      CopyTo("x"),
      # 9
      # No check and jump, just flow down.

    Label("Write Hundreds: 9"),
    BumpPlus("digit"),
    Label("Write Hundreds: 8"),
    BumpPlus("digit"),
    Label("Write Hundreds: 7"),
    BumpPlus("digit"),
    Label("Write Hundreds: 6"),
    BumpPlus("digit"),
    Label("Write Hundreds: 5"),
    BumpPlus("digit"),
    Label("Write Hundreds: 4"),
    BumpPlus("digit"),
    Label("Write Hundreds: 3"),
    BumpPlus("digit"),
    Label("Write Hundreds: 2"),
    BumpPlus("digit"),
    Label("Write Hundreds: 1"),
    # No BumpPlus as we bumped earlier.
    Outbox(),

    ### TENS
    Label("Tens"),
    Comment("Tens Initialization"),
    CopyFrom("0"),
    CopyTo("digit"),
    CopyFrom("x"),
    Comment("Tens: Get tens digit"),
    Comment("Unrolled loop in 10s"),
      # 0
      Subtract("10"),
      JumpIfNegative("Write Tens: 0"),
      CopyTo("x"),
      # 1
      Subtract("10"),
      JumpIfNegative("Write Tens: 1"),
      CopyTo("x"),
      # 2
      Subtract("10"),
      JumpIfNegative("Write Tens: 2"),
      CopyTo("x"),
      # 3
      Subtract("10"),
      JumpIfNegative("Write Tens: 3"),
      CopyTo("x"),
      # 4
      Subtract("10"),
      JumpIfNegative("Write Tens: 4"),
      CopyTo("x"),
      # 5
      Subtract("10"),
      JumpIfNegative("Write Tens: 5"),
      CopyTo("x"),
      # 6
      Subtract("10"),
      JumpIfNegative("Write Tens: 6"),
      CopyTo("x"),
      # 7
      Subtract("10"),
      JumpIfNegative("Write Tens: 7"),
      CopyTo("x"),
      # 8
      Subtract("10"),
      JumpIfNegative("Write Tens: 8"),
      CopyTo("x"),
      # 9
      # No check and jump, just flow down.

    BumpPlus("digit"),
    Label("Write Tens: 8"),
    BumpPlus("digit"),
    Label("Write Tens: 7"),
    BumpPlus("digit"),
    Label("Write Tens: 6"),
    BumpPlus("digit"),
    Label("Write Tens: 5"),
    BumpPlus("digit"),
    Label("Write Tens: 4"),
    BumpPlus("digit"),
    Label("Write Tens: 3"),
    BumpPlus("digit"),
    Label("Write Tens: 2"),
    BumpPlus("digit"),
    Label("Write Tens: 1"),
    BumpPlus("digit"),
    Label("Write Tens: 0"),
    Outbox(),

    ### UNITS
    Label("Write Units"),
    CopyFrom("x"),
    Outbox(),
    Jump("BEGIN"),
]
# fmt: on
