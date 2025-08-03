"""Unit tests for the DotGenerator class."""

import textwrap

import pytest

from xyz.human_resource_machine.dot_generator import DotGenerator
from xyz.human_resource_machine.parser import Parser


@pytest.mark.parametrize(
    "source, expected_lines",
    [
        pytest.param(
            textwrap.dedent("""
            INBOX
            OUTBOX
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="INBOX"];',
                '  node_2 [label="OUTBOX"];',
                "  node_1 -> node_2;",
                "}",
            ],
            id="basic_inbox_outbox",
        ),
        pytest.param(
            textwrap.dedent("""
            INBOX
            COPYTO 0
            OUTBOX
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="INBOX"];',
                '  node_2 [label="COPYTO 0"];',
                '  node_3 [label="OUTBOX"];',
                "  node_1 -> node_2;",
                "  node_2 -> node_3;",
                "}",
            ],
            id="simple_copyto",
        ),
        pytest.param(
            textwrap.dedent("""
            BEGIN:
            INBOX
            OUTBOX
            JUMP BEGIN
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="BEGIN:", shape=ellipse];',
                '  node_2 [label="INBOX"];',
                '  node_3 [label="OUTBOX"];',
                '  node_4 [label="jump BEGIN", shape=diamond];',
                "  node_1 -> node_2;",
                "  node_2 -> node_3;",
                "  node_3 -> node_4;",
                "  node_4 -> node_1 [label='jump'];",
                "}",
            ],
            id="loop_with_jump",
        ),
        pytest.param(
            textwrap.dedent("""
            INBOX
            JUMPZ END
            OUTBOX
            END:
            OUTBOX
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="INBOX"];',
                '  node_2 [label="END", shape=diamond];',
                '  node_3 [label="OUTBOX"];',
                '  node_4 [label="END:", shape=ellipse];',
                '  node_5 [label="OUTBOX"];',
                "  node_1 -> node_2;",
                "  node_2 -> node_3;",
                "  node_4 -> node_5;",
                "  node_2 -> node_4 [label='true'];",
                "  node_2 -> node_5 [label='false'];",
                "}",
            ],
            id="conditional_jump_zero",
        ),
        pytest.param(
            textwrap.dedent("""
            INBOX
            ADD 5
            SUB 3
            OUTBOX
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="INBOX"];',
                '  node_2 [label="ADD 5"];',
                '  node_3 [label="SUBTRACT 3"];',
                '  node_4 [label="OUTBOX"];',
                "  node_1 -> node_2;",
                "  node_2 -> node_3;",
                "  node_3 -> node_4;",
                "}",
            ],
            id="arithmetic_operations",
        ),
        pytest.param(
            textwrap.dedent("""
            INBOX
            COPYFROM [0]
            COPYTO [1]
            OUTBOX
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="INBOX"];',
                '  node_2 [label="COPYFROM 0"];',
                '  node_3 [label="COPYTO 1"];',
                '  node_4 [label="OUTBOX"];',
                "  node_1 -> node_2;",
                "  node_2 -> node_3;",
                "  node_3 -> node_4;",
                "}",
            ],
            id="indirect_addressing",
        ),
        pytest.param(
            textwrap.dedent("""
            INBOX
            BUMPUP 2
            JUMPN NEGATIVE
            OUTBOX
            JUMP END
            NEGATIVE:
            BUMPUP 2
            OUTBOX
            END:
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="INBOX"];',
                '  node_2 [label="BUMPPLUS 2"];',
                '  node_3 [label="NEGATIVE", shape=diamond];',
                '  node_4 [label="OUTBOX"];',
                '  node_5 [label="jump END", shape=diamond];',
                '  node_6 [label="NEGATIVE:", shape=ellipse];',
                '  node_7 [label="BUMPPLUS 2"];',
                '  node_8 [label="OUTBOX"];',
                '  node_9 [label="END:", shape=ellipse];',
                "  node_1 -> node_2;",
                "  node_2 -> node_3;",
                "  node_3 -> node_4;",
                "  node_4 -> node_5;",
                "  node_6 -> node_7;",
                "  node_7 -> node_8;",
                "  node_3 -> node_6 [label='true'];",
                "  node_3 -> node_8 [label='false'];",
                "  node_5 -> node_9 [label='jump'];",
                "}",
            ],
            id="complex_conditional_flow",
        ),
        pytest.param(
            textwrap.dedent("""
            INBOX
            BUMPDN [A]
            COPYTO B
            OUTBOX
        """),
            [
                "digraph G {",
                "  rankdir=TB;",
                "  node [shape=box];",
                '  node_1 [label="INBOX"];',
                '  node_2 [label="BUMPMINUS A"];',
                '  node_3 [label="COPYTO B"];',
                '  node_4 [label="OUTBOX"];',
                "  node_1 -> node_2;",
                "  node_2 -> node_3;",
                "  node_3 -> node_4;",
                "}",
            ],
            id="bump_down_operation",
        ),
    ],
)
def test_generate_dot_file(source: str, expected_lines: list[str]):
    """
    Test that a basic DOT file is generated correctly.
    """
    parser = Parser(source)
    program = parser.parse()

    generator = DotGenerator(program)
    content = generator.generate_dot()

    for line in expected_lines:
        stripped_line = line.strip()
        assert stripped_line in content, (
            f"Expected line '{stripped_line}' not found in generated DOT content:\n{content}"
        )
