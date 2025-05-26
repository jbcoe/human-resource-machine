"""Tests for the Human-Resource-Machine-like language parser."""

from textwrap import dedent

from xyz.human_resource_machine.interpreter import (
    Comment,
    Inbox,
    Jump,
    JumpIfNegative,
    JumpIfZero,
    Label,
    Outbox,
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


def test_parse_code_with_indirect_registers():
    """Test parsing code with indirect registers."""
    source = dedent("""\
    COPYTO [A]
    COPYFROM B
    ADD [C]
    SUB D
    BUMPUP [E]
    BUMPDN F
    """)
    parser = Parser(source)
    instructions = parser.parse()

    assert len(instructions) == 6
    assert instructions[0].register == "A"
    assert instructions[0].indirect is True

    assert instructions[1].register == "B"
    assert instructions[1].indirect is False

    assert instructions[2].register == "C"
    assert instructions[2].indirect is True

    assert instructions[3].register == "D"
    assert instructions[3].indirect is False

    assert instructions[4].register == "E"
    assert instructions[4].indirect is True

    assert instructions[5].register == "F"
    assert instructions[5].indirect is False


def test_parse_jumps():
    """Test parsing jump instructions."""
    # This code is nonsensical, but tests the parser's ability to handle jumps.
    source = dedent("""\
    JUMP START
    JUMPZ ZERO
    JUMPN NEGATIVE
    """)
    parser = Parser(source)
    instructions = parser.parse()

    assert len(instructions) == 3
    assert isinstance(instructions[0], Jump)
    assert instructions[0].label == "START"

    assert isinstance(instructions[1], JumpIfZero)
    assert instructions[1].label == "ZERO"

    assert isinstance(instructions[2], JumpIfNegative)
    assert instructions[2].label == "NEGATIVE"
