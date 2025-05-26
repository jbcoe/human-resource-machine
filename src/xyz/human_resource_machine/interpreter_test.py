"""Unit tests for the Human Resource Machine interpreter."""

import pytest

from xyz.human_resource_machine.interpreter import (
    Add,
    BumpMinus,
    BumpPlus,
    CopyFrom,
    CopyTo,
    Inbox,
    Interpreter,
    Jump,
    Label,
    Outbox,
    Subtract,
)


def test_interpreter_initialization():
    """Test the initialization of the Interpreter."""
    interpreter = Interpreter()

    assert interpreter.registers == {}
    assert interpreter.instructions == []
    assert interpreter.executions == 0
    assert interpreter.value is None


def test_step():
    """Test a single program step."""
    instructions = [Inbox(), Inbox()]
    interpreter = Interpreter(instructions=instructions, input=["boots", "cats"])

    assert interpreter.instruction_index == 0

    interpreter.step()
    assert interpreter.value == "boots"
    assert interpreter.instruction_index == 1

    interpreter.step()
    assert interpreter.value == "cats"
    assert interpreter.instruction_index == 2


def test_execution():
    """Test whole-program execution."""
    instructions = [Inbox(), Inbox()]
    interpreter = Interpreter(instructions=instructions, input=["boots", "cats"])
    interpreter.execute_program()

    assert interpreter.value == "cats"
    assert interpreter.instruction_index == 2


def test_inbox():
    """Test the Inbox instruction."""
    instructions = [Inbox()]
    input = [42]
    interpreter = Interpreter(instructions=instructions, input=input)
    interpreter.execute_program()

    assert interpreter.value == input[0]


def test_outbox():
    """Test the Outbox instruction."""
    instructions = [Inbox(), Outbox()]
    input = [42]
    interpreter = Interpreter(instructions=instructions, input=input)
    output = interpreter.execute_program()

    assert output == input


@pytest.mark.parametrize(
    "input",
    [
        (["boots", "cats", 1, 2, 3]),
    ],
)
def test_inbox_outbox(input):
    """Test Jump using Inbox and Outbox with various inputs."""
    instructions = [
        Label("BEGIN"),
        Inbox(),
        Outbox(),
        Jump("BEGIN"),
    ]
    interpreter = Interpreter(instructions=instructions, input=input)
    output = interpreter.execute_program()

    assert output == input


def test_copy_to_register():
    """Test CopyTo instruction with a register."""
    instructions = [Inbox(), CopyTo("A")]
    interpreter = Interpreter(instructions=instructions, input=[42])
    interpreter.execute_program()

    assert interpreter.register("A") == 42


def test_copy_from_register():
    """Test CopyFrom instruction with a register."""
    instructions = [
        Inbox(),
        CopyTo("A"),
        Inbox(),
        CopyFrom("A"),
    ]
    interpreter = Interpreter(instructions=instructions, input=[42, "STOP"])
    assert interpreter.register("A") is None
    interpreter.step()  # Inbox first value
    assert interpreter.value == 42
    interpreter.step()  # CopyTo "A"
    assert interpreter.register("A") == 42
    interpreter.step()  # Inbox second value
    assert interpreter.value == "STOP"
    interpreter.step()  # CopyFrom "A"
    assert interpreter.value == 42

    interpreter.execute_program()


def test_copy_from_register_with_indirect():
    """Test CopyFrom instruction with an indirect register."""
    registers = {0: 4, 4: 42}
    instructions = [
        CopyFrom(0, indirect=True),  # Reads from register 4
    ]
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.value == 42


def test_copy_to_register_with_indirect():
    """Test CopyTo instruction with an indirect register."""
    registers = {0: 4}
    instructions = [
        Inbox(),  # Reads from input
        CopyTo(0, indirect=True),  # Writes to register 4
    ]
    interpreter = Interpreter(
        input=[42], instructions=instructions, registers=registers
    )
    interpreter.execute_program()
    assert interpreter.register(4) == 42


def test_bump_plus():
    """Test BumpPlus instruction."""
    registers = {"A": 5}
    instructions = [BumpPlus("A")]
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.register("A") == 6
    assert interpreter.value == 6


def test_bump_minus():
    """Test BumpMinus instruction."""
    registers = {"A": 5}
    instructions = [BumpMinus("A")]
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.register("A") == 4
    assert interpreter.value == 4


def test_bump_plus_indirect():
    """Test BumpPlus instruction with indirection."""
    registers = {0: 4, 4: 42}
    instructions = [BumpPlus(0, indirect=True)]  # Bumps register 4
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.register(4) == 43
    assert interpreter.value == 43


def test_bump_minus_indirect():
    """Test BumpMinus instruction with indirection."""
    registers = {0: 4, 4: 42}
    instructions = [BumpMinus(0, indirect=True)]  # Bumps register 4
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.register(4) == 41
    assert interpreter.value == 41


def test_add():
    """Test Add instruction."""
    registers = {"A": 5, "B": 3}
    instructions = [CopyFrom("A"), Add("B")]
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.value == 8


def test_subtract():
    """Test Subtract instruction."""
    registers = {"A": 5, "B": 3}
    instructions = [CopyFrom("A"), Subtract("B")]
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.value == 2


def test_add_indirect():
    """Test Add instruction with indirection."""
    registers = {"A": 5, 0: 4, 4: 3}
    instructions = [CopyFrom("A"), Add(0, indirect=True)]
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.value == 8


def test_subtract_indirect():
    """Test Subtract instruction with indirection."""
    registers = {"A": 5, 0: 4, 4: 3}
    instructions = [CopyFrom("A"), Subtract(0, indirect=True)]
    interpreter = Interpreter(instructions=instructions, registers=registers)
    interpreter.execute_program()

    assert interpreter.value == 2
