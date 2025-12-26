"""A parser for a Human Resource Machine-like language."""

from dataclasses import dataclass
from typing import List, Type

import xyz.human_resource_machine.interpreter as interpreter
import xyz.human_resource_machine.lexer as lexer
from xyz.human_resource_machine.interpreter import int_or_str


@dataclass(frozen=True, slots=True)
class Program:
    statements: List[interpreter.Instruction]


class Parser:
    """A parser for a Human Resource Machine-like language."""

    def __init__(self, source: str):
        """Initialize the parser with the source code."""
        self.lexer = lexer.Lexer(source)
        self.tokens = self.lexer.tokenize()
        self.current_token_index = 0

    def _parse_with_register_arg(
        self, cls: Type[interpreter.Instruction]
    ) -> interpreter.Instruction:
        """Parse a register token into an interpreter register."""

        if self.token is None or self.token.kind != lexer.TokenKind.INSTRUCTION:
            raise ValueError(f"Expected instruction, but got {self.token}.")
        self.step()
        token = self.token
        if token is None or token.kind != lexer.TokenKind.ARGUMENT:
            raise ValueError(f"Expected argument, but got {token}.")
        register = token.value
        # Token.value can be `str | int` according to the lexer type; coerce to
        # str before doing string operations and slicing so the type checker
        # can reason about it.
        reg_str = str(register)
        if reg_str.startswith("[") and reg_str.endswith("]"):
            return cls(int_or_str(reg_str[1:-1]), True)
        return cls(int_or_str(reg_str), False)

    def _parse_with_label_arg(
        self, cls: Type[interpreter.Instruction]
    ) -> interpreter.Instruction:
        """Parse a label token into an interpreter label."""
        if self.token is None or self.token.kind != lexer.TokenKind.INSTRUCTION:
            raise ValueError(f"Expected instruction, but got {self.token}.")
        self.step()
        token = self.token
        if token is None or token.kind != lexer.TokenKind.ARGUMENT:
            raise ValueError(f"Expected argument, but got {token}.")
        label = token.value
        return cls(label)

    def _parse_instruction(self) -> interpreter.Instruction:
        """Parse one or more tokens into an interpreter instruction."""
        token = self.token
        # Narrow the type for the type checker: ensure token is not None and is
        # an INSTRUCTION token before accessing `token.value` below.
        assert token is not None and token.kind == lexer.TokenKind.INSTRUCTION

        match token.value:
            case lexer.Instruction.INBOX:
                return interpreter.Inbox()
            case lexer.Instruction.OUTBOX:
                return interpreter.Outbox()
            case lexer.Instruction.COPYFROM:
                return self._parse_with_register_arg(interpreter.CopyFrom)
            case lexer.Instruction.COPYTO:
                return self._parse_with_register_arg(interpreter.CopyTo)
            case lexer.Instruction.ADD:
                return self._parse_with_register_arg(interpreter.Add)
            case lexer.Instruction.SUB:
                return self._parse_with_register_arg(interpreter.Subtract)
            case lexer.Instruction.BUMPUP:
                return self._parse_with_register_arg(interpreter.BumpPlus)
            case lexer.Instruction.BUMPDN:
                return self._parse_with_register_arg(interpreter.BumpMinus)
            case lexer.Instruction.JUMP:
                return self._parse_with_label_arg(interpreter.Jump)
            case lexer.Instruction.JUMPZ:
                return self._parse_with_label_arg(interpreter.JumpIfZero)
            case lexer.Instruction.JUMPN:
                return self._parse_with_label_arg(interpreter.JumpIfNegative)
            case _:
                raise ValueError(
                    f"Unknown instruction at line {getattr(token, 'line', self.current_token_index)}: {token.value}"
                )

    @property
    def token(self) -> lexer.Token | None:
        """Get the current token."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def step(self) -> None:
        """Advance to the next token."""
        self.current_token_index += 1

    def parse(self) -> Program:
        """Parse the tokenized source code into a list of instructions."""
        instructions = []
        while token := self.token:
            if token.kind == lexer.TokenKind.INSTRUCTION:
                instruction = self._parse_instruction()
                instructions.append(instruction)
            elif token.kind == lexer.TokenKind.LABEL:
                instructions.append(interpreter.Label(str(token.value)))
            elif token.kind == lexer.TokenKind.COMMENT:
                instructions.append(interpreter.Comment(str(token.value)))
            else:
                raise ValueError(
                    f"Unknown token at index {self.current_token_index}: {token}"
                )
            self.step()

        return Program(statements=instructions)
