"""Tests for the Human-Resource-Machine-like language parser."""

import textwrap
import typing

import pytest

import xyz.human_resource_machine.interpreter as hrm_interpreter
import xyz.human_resource_machine.parser as hrm_parser


def test_parse_simple_code():
    """Test parsing a simple code snippet."""
    source = textwrap.dedent("""\
    # This is a comment
    BEGIN:
    INBOX
    OUTBOX
    JUMP BEGIN
    """)
    parser = hrm_parser.Parser(source)
    instructions = parser.parse().statements

    assert len(instructions) == 5
    instr0: typing.Any = instructions[0]
    instr1: typing.Any = instructions[1]
    instr2: typing.Any = instructions[2]
    instr3: typing.Any = instructions[3]
    instr4: typing.Any = instructions[4]

    assert isinstance(instr0, hrm_interpreter.Comment)
    assert instr0.text == "This is a comment"
    assert isinstance(instr1, hrm_interpreter.Label)
    assert instr1.label == "BEGIN"
    assert isinstance(instr2, hrm_interpreter.Inbox)
    assert isinstance(instr3, hrm_interpreter.Outbox)
    assert isinstance(instr4, hrm_interpreter.Jump)
    assert instr4.label == "BEGIN"


@pytest.mark.parametrize(
    "source, instruction, register, is_indirect",
    [
        ("COPYTO A", hrm_interpreter.CopyTo, "A", False),
        ("COPYTO [A]", hrm_interpreter.CopyTo, "A", True),
        ("COPYFROM B", hrm_interpreter.CopyFrom, "B", False),
        ("COPYFROM [B]", hrm_interpreter.CopyFrom, "B", True),
        ("ADD C", hrm_interpreter.Add, "C", False),
        ("ADD [C]", hrm_interpreter.Add, "C", True),
        ("SUB D", hrm_interpreter.Subtract, "D", False),
        ("SUB [D]", hrm_interpreter.Subtract, "D", True),
        ("BUMPUP E", hrm_interpreter.BumpPlus, "E", False),
        ("BUMPUP [E]", hrm_interpreter.BumpPlus, "E", True),
        ("BUMPDN F", hrm_interpreter.BumpMinus, "F", False),
        ("BUMPDN [F]", hrm_interpreter.BumpMinus, "F", True),
    ],
)
def test_parse_code_with_registers(
    source: str,
    instruction: typing.Type[hrm_interpreter.Instruction],
    register: str,
    is_indirect: bool,
):
    """Test parsing code with direct and indirect registers."""

    parser = hrm_parser.Parser(source)
    instructions = parser.parse().statements

    assert len(instructions) == 1
    instr = instructions[0]
    assert isinstance(instr, instruction)

    # Narrow the static type for the checker using explicit casts.
    if instruction is hrm_interpreter.CopyTo:
        concrete = typing.cast(hrm_interpreter.CopyTo, instr)
    elif instruction is hrm_interpreter.CopyFrom:
        concrete = typing.cast(hrm_interpreter.CopyFrom, instr)
    elif instruction is hrm_interpreter.Add:
        concrete = typing.cast(hrm_interpreter.Add, instr)
    elif instruction is hrm_interpreter.Subtract:
        concrete = typing.cast(hrm_interpreter.Subtract, instr)
    elif instruction is hrm_interpreter.BumpPlus:
        concrete = typing.cast(hrm_interpreter.BumpPlus, instr)
    elif instruction is hrm_interpreter.BumpMinus:
        concrete = typing.cast(hrm_interpreter.BumpMinus, instr)
    else:
        concrete = typing.cast(typing.Any, instr)

    assert concrete.register == register
    assert concrete.indirect == is_indirect


@pytest.mark.parametrize(
    "source, instruction, label",
    [
        ("JUMP START", hrm_interpreter.Jump, "START"),
        ("JUMPZ ZERO", hrm_interpreter.JumpIfZero, "ZERO"),
        ("JUMPN NEGATIVE", hrm_interpreter.JumpIfNegative, "NEGATIVE"),
    ],
)
def test_parse_jumps(
    source: str, instruction: typing.Type[hrm_interpreter.Instruction], label: str
):
    """Test parsing jump instructions."""
    parser = hrm_parser.Parser(source)
    instructions = parser.parse().statements

    assert len(instructions) == 1
    instr = instructions[0]
    assert isinstance(instr, instruction)

    if instruction is hrm_interpreter.Jump:
        concrete = typing.cast(hrm_interpreter.Jump, instr)
    elif instruction is hrm_interpreter.JumpIfZero:
        concrete = typing.cast(hrm_interpreter.JumpIfZero, instr)
    elif instruction is hrm_interpreter.JumpIfNegative:
        concrete = typing.cast(hrm_interpreter.JumpIfNegative, instr)
    else:
        concrete = typing.cast(typing.Any, instr)

    assert concrete.label == label
