"""A lexer for a Human Resource Machine-like language."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TokenKind(StrEnum):
    """Enumeration of token kinds."""

    ARGUMENT = "ARGUMENT"
    COMMENT = "COMMENT"
    INSTRUCTION = "INSTRUCTION"
    LABEL = "LABEL"


@dataclass(frozen=True)
class Token:
    """A token in the Human Resource Machine-like language."""

    kind: TokenKind
    value: str | int
    line: int


class Instruction(StrEnum):
    """Enumeration of keywords in the Human Resource Machine-like language."""

    INBOX = "INBOX"
    OUTBOX = "OUTBOX"
    COPYFROM = "COPYFROM"
    COPYTO = "COPYTO"
    ADD = "ADD"
    SUB = "SUB"
    BUMPUP = "BUMPUP"
    BUMPDN = "BUMPDN"
    JUMP = "JUMP"
    JUMPZ = "JUMPZ"
    JUMPN = "JUMPN"


class Lexer:
    """A lexer for a Human Resource Machine-like language."""

    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> list[Token]:
        """Tokenize the entire source code."""
        tokens = []
        for line_number, line in enumerate(self.source.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            elif line.startswith("#"):
                tokens.append(Token(TokenKind.COMMENT, line[1:].strip(), line_number))
                continue

            instruction, *args = line.split()

            if instruction in Instruction.__members__:
                tokens.append(Token(TokenKind.INSTRUCTION, instruction, line_number))
                for arg in args:
                    tokens.append(Token(TokenKind.ARGUMENT, arg, line_number))
                continue

            if instruction.endswith(":"):
                tokens.append(Token(TokenKind.LABEL, instruction[:-1], line_number))
                continue
            raise ValueError(f"Failed to parse line {line_number}: {line}")

        return tokens
