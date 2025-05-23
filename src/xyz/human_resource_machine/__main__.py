from xyz.human_resource_machine.interpreter import (
    Interpreter,
    Label,
    Inbox,
    Outbox,
    CopyTo,
    CopyFrom,
    Jump,
)


def main():
    interpreter = Interpreter()
    interpreter.registers = {
        0: "N",
        1: "K",
        2: "A",
        3: "E",
        4: "R",
        5: "D",
        6: "O",
        7: "L",
        8: "Y",
        9: "J",
        12: 8,
    }
    interpreter.instructions = [
        Label("BEGIN"),
        Inbox(),
        CopyTo(12),
        CopyFrom(12, indirect=True),
        Outbox(),
        Jump("BEGIN"),
    ]
    input = [6, 2, 0, 3, 4]
    interpreter.execute_program(input)
    print(interpreter.to_str(), "\n")
    print("Registers:", interpreter.registers)
    print("Input: ", input)
    print("Output:", ", ".join(interpreter.output))
    print("Execution count:", interpreter.executions)
    print("Instruction count:", interpreter.instruction_count)


if __name__ == "__main__":
    main()
