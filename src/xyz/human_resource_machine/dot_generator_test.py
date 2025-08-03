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
