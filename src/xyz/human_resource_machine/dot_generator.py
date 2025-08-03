from typing import Any, Dict, List

from .interpreter import (
    Add,
    BumpMinus,
    BumpPlus,
    Comment,
    CopyFrom,
    CopyTo,
    Inbox,
    Jump,
    JumpIfNegative,
    JumpIfZero,
    Label,
    Outbox,
    Subtract,
)
from .parser import Program


class DotGenerator:
    def __init__(self, program: Program):
        self.program = program
        self.dot_lines: List[str] = []
        self.node_counter = 0
        self.label_to_node: Dict[str, str] = {}
        self.statement_to_node: Dict[Any, str] = {}

    def _new_node_id(self) -> str:
        self.node_counter += 1
        return f"node_{self.node_counter}"

    def generate_dot(self) -> str:
        self.dot_lines.append("digraph G {")
        self.dot_lines.append("  rankdir=TB;")
        self.dot_lines.append("  node [shape=box];")

        current_node_id: str | None = None
        # First pass: Create nodes for each statement and connect sequential flow
        for i, statement in enumerate(self.program.statements):
            node_id = self._new_node_id()
            self.statement_to_node[statement] = node_id

            if isinstance(statement, Comment):
                # Comments are not part of the control flow graph
                continue
            elif isinstance(statement, Label):
                # Labels are represented as ellipses
                self.dot_lines.append(
                    f'  {node_id} [label="{statement.label}:", shape=ellipse];'
                )
                self.label_to_node[statement.label] = (
                    node_id  # Store label node ID for jumps
                )
                current_node_id = node_id  # Labels are part of sequential flow
            elif isinstance(statement, Jump):
                # Jumps are represented as diamonds
                self.dot_lines.append(
                    f'  {node_id} [label="jump {statement.label}", shape=diamond];'
                )
                if current_node_id:
                    self.dot_lines.append(f"  {current_node_id} -> {node_id};")
                current_node_id = node_id
            elif isinstance(statement, (JumpIfZero, JumpIfNegative)):
                # Conditional jumps are represented as diamonds
                self.dot_lines.append(
                    f'  {node_id} [label="{statement.label}", shape=diamond];'
                )
                if current_node_id:
                    self.dot_lines.append(f"  {current_node_id} -> {node_id};")
                current_node_id = node_id
            elif isinstance(
                statement,
                (Inbox, Outbox, Add, Subtract, CopyTo, CopyFrom, BumpPlus, BumpMinus),
            ):
                # Other instructions are represented as boxes
                label = statement.__class__.__name__.upper()
                if hasattr(statement, "register") and statement.register is not None:
                    label += f" {statement.register}"
                self.dot_lines.append(f'  {node_id} [label="{label}"];')
                if current_node_id:
                    self.dot_lines.append(f"  {current_node_id} -> {node_id};")
                current_node_id = node_id

        # Second pass: Connect jumps and conditional jumps to their target labels
        for i, statement in enumerate(self.program.statements):
            if isinstance(statement, Jump):
                jump_node_id = self.statement_to_node[statement]
                if statement.label in self.label_to_node:
                    target_node_id = self.label_to_node[statement.label]
                    self.dot_lines.append(
                        f"  {jump_node_id} -> {target_node_id} [label='jump'];"
                    )
            elif isinstance(statement, (JumpIfZero, JumpIfNegative)):
                cond_jump_node_id = self.statement_to_node[statement]
                if statement.label in self.label_to_node:
                    target_node_id = self.label_to_node[statement.label]
                    self.dot_lines.append(
                        f"  {cond_jump_node_id} -> {target_node_id} [label='true'];"
                    )

                # Add edge to the next *executable* statement for the 'false' case
                next_executable_statement = None
                for j in range(i + 1, len(self.program.statements)):
                    s = self.program.statements[j]
                    if not isinstance(s, (Comment, Label)):
                        next_executable_statement = s
                        break

                if (
                    next_executable_statement
                    and next_executable_statement in self.statement_to_node
                ):
                    next_node_id = self.statement_to_node[next_executable_statement]
                    self.dot_lines.append(
                        f"  {cond_jump_node_id} -> {next_node_id} [label='false'];"
                    )

        self.dot_lines.append("}")
        return "\n".join(self.dot_lines)
