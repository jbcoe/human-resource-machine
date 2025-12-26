"""A parser for a Human Resource Machine-like language."""

import typing
from dataclasses import dataclass

import xyz.human_resource_machine.interpreter as hrm_interpreter
import xyz.human_resource_machine.lexer as hrm_lexer


@dataclass(frozen=True, slots=True)
class Program:
    statements: typing.List[hrm_interpreter.Instruction]


class Parser:
    """A parser for a Human Resource Machine-like language."""

    def __init__(self, source: str):
        """Initialize the parser with the source code."""
        self.lexer = hrm_lexer.Lexer(source)
        self.tokens = self.lexer.tokenize()
        self.current_token_index = 0

    def _parse_with_register_arg(
        self, cls: typing.Type[hrm_interpreter.Instruction]
    ) -> hrm_interpreter.Instruction:
        """Parse a register token into an interpreter register."""

        if self.token is None or self.token.kind != hrm_lexer.TokenKind.INSTRUCTION:
            raise ValueError(f"Expected instruction, but got {self.token}.")
        self.step()
        token = self.token
        if token is None or token.kind != hrm_lexer.TokenKind.ARGUMENT:
            raise ValueError(f"Expected argument, but got {token}.")
        register = token.value
        # Token.value can be `str | int` according to the lexer type; coerce to
        # str before doing string operations and slicing so the type checker
        # can reason about it.
        reg_str = str(register)
        if reg_str.startswith("[") and reg_str.endswith("]"):
            return cls(hrm_interpreter.int_or_str(reg_str[1:-1]), True)
        return cls(hrm_interpreter.int_or_str(reg_str), False)

    def _parse_with_label_arg(
        self, cls: typing.Type[hrm_interpreter.Instruction]
    ) -> hrm_interpreter.Instruction:
        """Parse a label token into an interpreter label."""
        if self.token is None or self.token.kind != hrm_lexer.TokenKind.INSTRUCTION:
            raise ValueError(f"Expected instruction, but got {self.token}.")
        self.step()
        token = self.token
        if token is None or token.kind != hrm_lexer.TokenKind.ARGUMENT:
            raise ValueError(f"Expected argument, but got {token}.")
        label = token.value
        return cls(label)

    def _parse_instruction(self) -> hrm_interpreter.Instruction:
        """Parse one or more tokens into an interpreter instruction."""
        token = self.token
        # Narrow the type for the type checker: ensure token is not None and is
        # an INSTRUCTION token before accessing `token.value` below.
        assert token is not None and token.kind == hrm_lexer.TokenKind.INSTRUCTION

        match token.value:
            case hrm_lexer.Instruction.INBOX:
                return hrm_interpreter.Inbox()
            case hrm_lexer.Instruction.OUTBOX:
                return hrm_interpreter.Outbox()
            case hrm_lexer.Instruction.COPYFROM:
                return self._parse_with_register_arg(hrm_interpreter.CopyFrom)
            case hrm_lexer.Instruction.COPYTO:
                return self._parse_with_register_arg(hrm_interpreter.CopyTo)
            case hrm_lexer.Instruction.ADD:
                return self._parse_with_register_arg(hrm_interpreter.Add)
            case hrm_lexer.Instruction.SUB:
                return self._parse_with_register_arg(hrm_interpreter.Subtract)
            case hrm_lexer.Instruction.BUMPUP:
                return self._parse_with_register_arg(hrm_interpreter.BumpPlus)
            case hrm_lexer.Instruction.BUMPDN:
                return self._parse_with_register_arg(hrm_interpreter.BumpMinus)
            case hrm_lexer.Instruction.JUMP:
                return self._parse_with_label_arg(hrm_interpreter.Jump)
            case hrm_lexer.Instruction.JUMPZ:
                return self._parse_with_label_arg(hrm_interpreter.JumpIfZero)
            case hrm_lexer.Instruction.JUMPN:
                return self._parse_with_label_arg(hrm_interpreter.JumpIfNegative)
            case _:
                raise ValueError(
                    f"Unknown instruction at line {getattr(token, 'line', self.current_token_index)}: {token.value}"
                )

    @property
    def token(self) -> hrm_lexer.Token | None:
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
            if token.kind == hrm_lexer.TokenKind.INSTRUCTION:
                instruction = self._parse_instruction()
                instructions.append(instruction)
            elif token.kind == hrm_lexer.TokenKind.LABEL:
                instructions.append(hrm_interpreter.Label(str(token.value)))
            elif token.kind == hrm_lexer.TokenKind.COMMENT:
                instructions.append(hrm_interpreter.Comment(str(token.value)))
            else:
                raise ValueError(
                    f"Unknown token at index {self.current_token_index}: {token}"
                )
            self.step()

        return Program(statements=instructions)
