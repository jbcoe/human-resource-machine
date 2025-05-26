"""Unit tests for the Human Resource Machine interpreter."""

import pytest

from xyz.human_resource_machine.interpreter import (
    Inbox,
    Interpreter,
    Jump,
    Label,
    Outbox,
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
