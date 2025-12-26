"""Unit tests for the DotGenerator class using on-disk testdata.

Each test case lives under `testdata/dot_generator` as a pair:
- `<name>.hrm` contains the source program
- `<name>.dot` contains the expected DOT output (lines to assert exist)
"""

import pathlib

import pytest

import xyz.human_resource_machine.dot_generator as hrm_dot_generator
import xyz.human_resource_machine.parser as hrm_parser

TESTDATA_DIR = pathlib.Path(__file__).parent / "testdata" / "dot_generator"


def _load_cases() -> list[tuple[str, list[str], str]]:
    cases: list[tuple[str, list[str], str]] = []
    if not TESTDATA_DIR.exists():
        return cases

    for dot_path in sorted(TESTDATA_DIR.glob("*.dot")):
        name = dot_path.stem
        hrm_path = dot_path.with_suffix(".hrm")
        if not hrm_path.exists():
            continue
        source = hrm_path.read_text()
        expected_lines = [ln.rstrip() for ln in dot_path.read_text().splitlines()]
        cases.append((source, expected_lines, name))

    return cases


CASES = _load_cases()


@pytest.mark.parametrize(
    "source,expected_lines",
    [(c[0], c[1]) for c in CASES],
    ids=[c[2] for c in CASES],
)
def test_generate_dot_file(source: str, expected_lines: list[str]):
    """Test that DOT content contains expected lines from .dot file."""
    parser = hrm_parser.Parser(source)
    program = parser.parse()

    generator = hrm_dot_generator.DotGenerator(program)
    content = generator.generate_dot()

    for line in expected_lines:
        stripped_line = line.strip()
        assert stripped_line in content, (
            f"Expected line '{stripped_line}' not found in generated DOT content:\n{content}"
        )
