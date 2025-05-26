"""Tests for the Human-Resource-Machine-like language lexer."""

from textwrap import dedent

from xyz.human_resource_machine.lexer import Lexer, Token, TokenKind


def test_tokenize_simple_code():
    """Test tokenizing a simple code snippet."""
    source = dedent("""\
    # This is a comment
    BEGIN:
    INBOX
    OUTBOX
    JUMP BEGIN
    """)
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    assert len(tokens) == 6
    assert tokens[0] == Token(TokenKind.COMMENT, "This is a comment", 1)
    assert tokens[1] == Token(TokenKind.LABEL, "BEGIN", 2)
    assert tokens[2] == Token(TokenKind.INSTRUCTION, "INBOX", 3)
    assert tokens[3] == Token(TokenKind.INSTRUCTION, "OUTBOX", 4)
    assert tokens[4] == Token(TokenKind.INSTRUCTION, "JUMP", 5)
    assert tokens[5] == Token(TokenKind.ARGUMENT, "BEGIN", 5)
