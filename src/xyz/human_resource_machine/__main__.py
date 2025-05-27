from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass

import yaml

import xyz.human_resource_machine.parser as parser
from xyz.human_resource_machine.interpreter import (
    Interpreter,
    Value,
    int_or_str,
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

        with open(path) as i:
            data = yaml.safe_load(i)

        return Level(
            source=data["source"],
            input=[int_or_str(x) for x in data.get("input", "").splitlines() if x],
            registers={
                int_or_str(k): int_or_str(v) for k, v in data["registers"].items()
            },
            speed_challenge=data["speed-challenge"],
            size_challenge=data["size-challenge"],
        )


def main():
    arg_parser = argparse.ArgumentParser(
        description="Human Resource Machine Interpreter"
    )
    arg_parser.add_argument(
        "path",
        type=str,
        help="Level to execute",
    )
    arg_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    arg_parser.add_argument(
        "--logging_format",
        type=str,
        default="%(levelname)s | %(asctime)s | %(name)s | %(filename)s:%(lineno)s | %(message)s",
        help="Format for logging output",
    )
    arg_parser.add_argument(
        "--logging_datefmt",
        type=str,
        default="%Y-%m-%d %H:%M:%S %Z",
        help="Date format for logging output",
    )
    args = arg_parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format=args.logging_format,
        datefmt=args.logging_datefmt,
    )
    logging.info("Starting Human Resource Machine Interpreter")

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
