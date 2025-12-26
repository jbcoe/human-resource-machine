"""Tests for the Human-Resource-Machine-like language parser."""

from textwrap import dedent
from typing import Any, Type, cast

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
    instructions = parser.parse().statements

    assert len(instructions) == 5
    instr0: Any = instructions[0]
    instr1: Any = instructions[1]
    instr2: Any = instructions[2]
    instr3: Any = instructions[3]
    instr4: Any = instructions[4]

    assert isinstance(instr0, Comment)
    assert instr0.text == "This is a comment"
    assert isinstance(instr1, Label)
    assert instr1.label == "BEGIN"
    assert isinstance(instr2, Inbox)
    assert isinstance(instr3, Outbox)
    assert isinstance(instr4, Jump)
    assert instr4.label == "BEGIN"


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
    instruction: Type[Instruction],
    register: str,
    is_indirect: bool,
):
    """Test parsing code with direct and indirect registers."""

    parser = Parser(source)
    instructions = parser.parse().statements

    assert len(instructions) == 1
    instr = instructions[0]
    assert isinstance(instr, instruction)

    # Narrow the static type for the checker using explicit casts.
    if instruction is CopyTo:
        concrete = cast(CopyTo, instr)
    elif instruction is CopyFrom:
        concrete = cast(CopyFrom, instr)
    elif instruction is Add:
        concrete = cast(Add, instr)
    elif instruction is Subtract:
        concrete = cast(Subtract, instr)
    elif instruction is BumpPlus:
        concrete = cast(BumpPlus, instr)
    elif instruction is BumpMinus:
        concrete = cast(BumpMinus, instr)
    else:
        concrete = cast(Any, instr)

    assert concrete.register == register
    assert concrete.indirect == is_indirect


@pytest.mark.parametrize(
    "source, instruction, label",
    [
        ("JUMP START", Jump, "START"),
        ("JUMPZ ZERO", JumpIfZero, "ZERO"),
        ("JUMPN NEGATIVE", JumpIfNegative, "NEGATIVE"),
    ],
)
def test_parse_jumps(source: str, instruction: Type[Instruction], label: str):
    """Test parsing jump instructions."""
    parser = Parser(source)
    instructions = parser.parse().statements

    assert len(instructions) == 1
    instr = instructions[0]
    assert isinstance(instr, instruction)

    if instruction is Jump:
        concrete = cast(Jump, instr)
    elif instruction is JumpIfZero:
        concrete = cast(JumpIfZero, instr)
    elif instruction is JumpIfNegative:
        concrete = cast(JumpIfNegative, instr)
    else:
        concrete = cast(Any, instr)

    assert concrete.label == label
