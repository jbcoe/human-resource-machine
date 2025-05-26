"""Tests for the Human-Resource-Machine-like language parser."""

from textwrap import dedent

from xyz.human_resource_machine.interpreter import Comment, Inbox, Jump, Label, Outbox
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
