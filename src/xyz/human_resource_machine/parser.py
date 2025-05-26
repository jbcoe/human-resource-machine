"""A parser for a Human Resource Machine-like language."""

from typing import Type

import xyz.human_resource_machine.interpreter as interpreter
import xyz.human_resource_machine.lexer as lexer


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
        if register.startswith("[") and register.endswith("]"):
            return cls(register[1:-1], True)
        return cls(register, False)

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
        assert token.kind == lexer.TokenKind.INSTRUCTION

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

    def parse(self) -> list[interpreter.Instruction]:
        """Parse the tokenized source code into a list of instructions."""
        instructions = []
        while token := self.token:
            if token.kind == lexer.TokenKind.INSTRUCTION:
                instruction = self._parse_instruction()
                instructions.append(instruction)
            elif token.kind == lexer.TokenKind.LABEL:
                instructions.append(interpreter.Label(token.value))
            elif token.kind == lexer.TokenKind.COMMENT:
                instructions.append(interpreter.Comment(token.value))
            else:
                raise ValueError(
                    f"Unknown token at index {self.current_token_index}: {token}"
                )
            self.step()

        return instructions
