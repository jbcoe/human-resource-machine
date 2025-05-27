from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

import yaml

import xyz.human_resource_machine.parser as parser
from xyz.human_resource_machine.interpreter import (
    Interpreter,
    Value,
)


@dataclass
class Level:
    """A class representing a level in the Human Resource Machine game."""

    source: str
    input: list[Value]
    registers: dict[Value, Value]
    speed_challenge: int
    size_challenge: int

    @staticmethod
    def from_yaml(path: str) -> Level:
        """Load a level from a YAML file."""

        def _as_int_or_str(value: str) -> int | str:
            """Convert a string to an int if possible, otherwise return the string."""
            try:
                return int(value)
            except ValueError:
                return value

        with open(path) as i:
            data = yaml.safe_load(i)

        return Level(
            source=data["source"],
            input=[_as_int_or_str(x) for x in data.get("input", "").splitlines() if x],
            registers={
                _as_int_or_str(k): _as_int_or_str(v)
                for k, v in data["registers"].items()
            },
            speed_challenge=data["speed-challenge"],
            size_challenge=data["size-challenge"],
        )


def main():
    arg_parser = argparse.ArgumentParser(
        description="Human Resource Machine Interpreter"
    )
    arg_parser.add_argument("path", type=str, help="Level to execute")
    args = arg_parser.parse_args()

    if not os.path.isabs(args.path):
        args.path = os.path.join(os.path.dirname(__file__), "challenges", args.path)
    level = Level.from_yaml(args.path)

    interpreter = Interpreter(
        instructions=parser.Parser(level.source).parse(),
        registers=level.registers,
        input=level.input,
    )
    output = interpreter.execute_program()
    print(interpreter.to_str(), "\n")
    print("Input: ", ", ".join(str(x) for x in interpreter._input))
    print("Output:", ", ".join(str(x) for x in output))
    print("Registers used:", len(interpreter.registers))

    print(
        f"Execution count: {interpreter.executions} target: {level.speed_challenge}",
    )
    print(
        f"Size challenge: {interpreter.instruction_count} "
        f"target: {level.size_challenge}",
    )


if __name__ == "__main__":
    main()
