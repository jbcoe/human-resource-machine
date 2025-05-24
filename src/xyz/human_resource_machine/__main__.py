import os
import sys
from typing import Any
from xyz.human_resource_machine.interpreter import Interpreter, Value

import argparse
import importlib.util


def _load_level(level: str) -> Any:
    file_path = os.path.join(os.path.dirname(__file__), "challenges", f"{level}.py")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Module path {file_path} not found.")

    module_name = f"xyz.human_resource_machine.challenges.{level}"

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    assert spec is not None, f"Level {level} not found"
    module = importlib.util.module_from_spec(spec)
    assert module is not None, f"Module {module_name} cannot be loaded."
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


def main():
    parser = argparse.ArgumentParser(description="Human Resource Machine Interpreter")
    parser.add_argument("level", type=str, help="Level to execute")
    args = parser.parse_args()

    level = _load_level(args.level)

    interpreter = Interpreter()

    interpreter.registers = level.REGISTERS
    interpreter.instructions = level.INSTRUCTIONS
    input: list[Value] = level.INPUT

    interpreter.execute_program(input)
    print(interpreter.to_str(), "\n")
    print("Registers:", interpreter.registers)
    print("Input: ", input)
    print("Output:", ", ".join(str(x) for x in interpreter.output))
    print("Execution count:", interpreter.executions)
    print("Instruction count:", interpreter.instruction_count)


if __name__ == "__main__":
    main()
