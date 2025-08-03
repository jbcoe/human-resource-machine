"""Unit tests for the DotGenerator class."""

import os

from xyz.human_resource_machine.dot_generator import DotGenerator
from xyz.human_resource_machine.interpreter import Inbox, Outbox
from xyz.human_resource_machine.parser import Program


def test_generate_dot_file_basic():
    """
    Test that a basic DOT file is generated correctly.
    """
    # Create a simple AST for testing
    # Equivalent to:
    # INBOX
    # OUTBOX
    program_ast = Program(statements=[Inbox(), Outbox()])

    output_dir = "temp_dot_files"
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, "test_program.dot")

    try:
        generator = DotGenerator(program_ast)
        with open(output_file_path, "w") as f:
            f.write(generator.generate_dot())

        with open(output_file_path, "r") as f:
            content = f.read()
            assert "digraph G {" in content
            assert "INBOX" in content
            assert "OUTBOX" in content
            assert "}" in content

    finally:
        # Clean up the generated file and directory
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        if os.path.exists(output_dir):
            os.rmdir(output_dir)
