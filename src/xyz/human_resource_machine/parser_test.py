"""Tests for the Human-Resource-Machine-like language parser."""

from textwrap import dedent

import pytest

from xyz.human_resource_machine.interpreter import (
    Add,
    BumpMinus,
    BumpPlus,
    Comment,
    CopyFrom,
    CopyTo,
    Inbox,
    Instruction,
    Jump,
    JumpIfNegative,
    JumpIfZero,
    Label,
    Outbox,
    Subtract,
)
from xyz.human_resource_machine.parser import Parser


def test_parse_simple_code():
    """Test parsing a simple code snippet."""
    source = dedent("""\
    # This is a comment
    BEGIN:
    INBOX
    OUTBOX
    JUMP BEGIN
    """)
    parser = Parser(source)
    instructions = parser.parse()

    assert len(instructions) == 5
    assert isinstance(instructions[0], Comment)
    assert instructions[0].text == "This is a comment"
    assert isinstance(instructions[1], Label)
    assert instructions[1].label == "BEGIN"
    assert isinstance(instructions[2], Inbox)
    assert isinstance(instructions[3], Outbox)
    assert isinstance(instructions[4], Jump)
    assert instructions[4].label == "BEGIN"


@pytest.mark.parametrize(
    "source, instruction, register, is_indirect",
    [
        ("COPYTO A", CopyTo, "A", False),
        ("COPYTO [A]", CopyTo, "A", True),
        ("COPYFROM B", CopyFrom, "B", False),
        ("COPYFROM [B]", CopyFrom, "B", True),
        ("ADD C", Add, "C", False),
        ("ADD [C]", Add, "C", True),
        ("SUB D", Subtract, "D", False),
        ("SUB [D]", Subtract, "D", True),
        ("BUMPUP E", BumpPlus, "E", False),
        ("BUMPUP [E]", BumpPlus, "E", True),
        ("BUMPDN F", BumpMinus, "F", False),
        ("BUMPDN [F]", BumpMinus, "F", True),
    ],
)
def test_parse_code_with_registers(
    source: str,
    instruction: Instruction,
    register: str,
    is_indirect: bool,
):
    """Test parsing code with direct and indirect registers."""

    parser = Parser(source)
    instructions = parser.parse()

    assert len(instructions) == 1
    assert isinstance(instructions[0], instruction)
    assert instructions[0].register == register
    assert instructions[0].indirect == is_indirect


@pytest.mark.parametrize(
    "source, instruction, label",
    [
        ("JUMP START", Jump, "START"),
        ("JUMPZ ZERO", JumpIfZero, "ZERO"),
        ("JUMPN NEGATIVE", JumpIfNegative, "NEGATIVE"),
    ],
)
def test_parse_jumps(source: str, instruction: Instruction, label: str):
    """Test parsing jump instructions."""
    parser = Parser(source)
    instructions = parser.parse()

    assert len(instructions) == 1
    assert isinstance(instructions[0], instruction)
    assert instructions[0].label == label
