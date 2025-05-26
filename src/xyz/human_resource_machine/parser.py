"""A parser for a Human Resource Machine-like language."""

import xyz.human_resource_machine.interpreter as interpreter
import xyz.human_resource_machine.lexer as lexer


class Parser:
    """A parser for a Human Resource Machine-like language."""

    def __init__(self, source: str):
        """Initialize the parser with the source code."""
        self.lexer = lexer.Lexer(source)
        self.tokens = self.lexer.tokenize()
        self.current_token_index = 0

    def _parse_argument(self) -> str:
        """Parse a single argument token into an interpreter argument."""
        token = self.token
        if token is None or token.kind != lexer.TokenKind.ARGUMENT:
            raise ValueError(f"Expected argument, but got {token}.")
        return token.value

    def _parse_register(self) -> tuple[str, bool]:
        """Parse a register token into an interpreter register."""
        token = self.token
        if token is None or token.kind != lexer.TokenKind.ARGUMENT:
            raise ValueError(f"Expected argument, but got {token}.")
        register = token.value
        if register.startswith("[") and register.endswith("]"):
            return register[1:-1], True
        return register, False

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
                self.step()  # Move to the next token for the argument
                register, indirect = self._parse_register()
                return interpreter.CopyFrom(register, indirect)
            case lexer.Instruction.COPYTO:
                self.step()  # Move to the next token for the argument
                register, indirect = self._parse_register()
                return interpreter.CopyTo(register, indirect)
            case lexer.Instruction.ADD:
                self.step()  # Move to the next token for the argument
                register, indirect = self._parse_register()
                return interpreter.Add(register, indirect)
            case lexer.Instruction.SUB:
                self.step()  # Move to the next token for the argument
                register, indirect = self._parse_register()
                return interpreter.Subtract(register, indirect)
            case lexer.Instruction.BUMPUP:
                self.step()  # Move to the next token for the argument
                register, indirect = self._parse_register()
                return interpreter.BumpPlus(register, indirect)
            case lexer.Instruction.BUMPDN:
                self.step()  # Move to the next token for the argument
                register, indirect = self._parse_register()
                return interpreter.BumpMinus(register, indirect)
            case lexer.Instruction.JUMP:
                self.step()
                label = self._parse_argument()
                return interpreter.Jump(label)
            case lexer.Instruction.JUMPZ:
                self.step()
                label = self._parse_argument()
                return interpreter.JumpIfZero(label)
            case lexer.Instruction.JUMPN:
                self.step()
                label = self._parse_argument()
                return interpreter.JumpIfNegative(label)
            case _:
                raise ValueError(f"Unknown instruction: {token.value}")

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
