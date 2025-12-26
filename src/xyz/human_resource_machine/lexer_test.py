"""Tests for the Human-Resource-Machine-like language lexer."""

import textwrap

import xyz.human_resource_machine.lexer as hrm_lexer


def test_tokenize_simple_code():
    """Test tokenizing a simple code snippet."""
    source = textwrap.dedent("""\
    # This is a comment
    BEGIN:
    INBOX
    OUTBOX
    JUMP BEGIN
    """)
    lexer = hrm_lexer.Lexer(source)
    tokens = lexer.tokenize()

    assert len(tokens) == 6
    assert tokens[0] == hrm_lexer.Token(hrm_lexer.TokenKind.COMMENT, "This is a comment", 1)
    assert tokens[1] == hrm_lexer.Token(hrm_lexer.TokenKind.LABEL, "BEGIN", 2)
    assert tokens[2] == hrm_lexer.Token(hrm_lexer.TokenKind.INSTRUCTION, "INBOX", 3)
    assert tokens[3] == hrm_lexer.Token(hrm_lexer.TokenKind.INSTRUCTION, "OUTBOX", 4)
    assert tokens[4] == hrm_lexer.Token(hrm_lexer.TokenKind.INSTRUCTION, "JUMP", 5)
    assert tokens[5] == hrm_lexer.Token(hrm_lexer.TokenKind.ARGUMENT, "BEGIN", 5)
