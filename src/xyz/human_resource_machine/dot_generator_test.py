"""Unit tests for the DotGenerator class."""

import textwrap

import pytest

from xyz.human_resource_machine.dot_generator import DotGenerator
from xyz.human_resource_machine.parser import Parser


@pytest.mark.parametrize(
    "source, expected",
    [
        pytest.param(
            textwrap.dedent("""\
            INBOX
            OUTBOX
        """),
            textwrap.dedent("""\
            digraph G {
              rankdir=TB;
              node [shape=box];
              node_1 [label="INBOX"];
              node_2 [label="OUTBOX"];
              node_1 -> node_2;
            }"""),
            id="basic_inbox_outbox",
        ),
    ],
)
def test_generate_dot_file_basic(source: str, expected: str):
    """
    Test that a basic DOT file is generated correctly.
    """
    # Create a simple AST for testing
    # Equivalent to:
    # INBOX
    # OUTBOX
    parser = Parser(
        textwrap.dedent("""\
            INBOX
            OUTBOX
        """)
    )
    program = parser.parse()

    generator = DotGenerator(program)
    content = generator.generate_dot()

    assert content == textwrap.dedent("""\
            digraph G {
              rankdir=TB;
              node [shape=box];
              node_1 [label="INBOX"];
              node_2 [label="OUTBOX"];
              node_1 -> node_2;
            }""")
