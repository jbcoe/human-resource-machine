use log::debug;
use std::collections::HashMap;
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Value {
    Int(i32),
    String(String),
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Value::Int(i) => write!(f, "{}", i),
            Value::String(s) => write!(f, "{}", s),
        }
    }
}

impl Value {
    pub fn as_int(&self) -> Result<i32, String> {
        match self {
            Value::Int(i) => Ok(*i),
            Value::String(_) => Err(format!("Expected integer, got string: {}", self)),
        }
    }
}

#[derive(Debug, Clone)]
pub struct UsesRegister {
    pub register: Value,
    pub indirect: bool,
}

impl UsesRegister {
    pub fn new(register: Value) -> Self {
        Self {
            register,
            indirect: false,
        }
    }

    pub fn new_indirect(register: Value) -> Self {
        Self {
            register,
            indirect: true,
        }
    }
}

#[derive(Debug, Clone)]
pub enum Instruction {
    Comment { text: String },
    Inbox,
    Outbox,
    Add(UsesRegister),
    Subtract(UsesRegister),
    CopyTo(UsesRegister),
    CopyFrom(UsesRegister),
    BumpPlus(UsesRegister),
    BumpMinus(UsesRegister),
    Label { label: String },
    Jump { label: String },
    JumpIfZero { label: String },
    JumpIfNegative { label: String },
    AssertValueIs { value: Value },
    AssertRegisterIs { register: String, value: Value },
}

impl fmt::Display for Instruction {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Instruction::Comment { text } => write!(f, "# {}", text),
            Instruction::Inbox => write!(f, "INBOX"),
            Instruction::Outbox => write!(f, "OUTBOX"),
            Instruction::Add(reg) => {
                if reg.indirect {
                    write!(f, "ADD [{}]", reg.register)
                } else {
                    write!(f, "ADD {}", reg.register)
                }
            }
            Instruction::Subtract(reg) => {
                if reg.indirect {
                    write!(f, "SUB [{}]", reg.register)
                } else {
                    write!(f, "SUB {}", reg.register)
                }
            }
            Instruction::CopyTo(reg) => {
                if reg.indirect {
                    write!(f, "COPYTO [{}]", reg.register)
                } else {
                    write!(f, "COPYTO {}", reg.register)
                }
            }
            Instruction::CopyFrom(reg) => {
                if reg.indirect {
                    write!(f, "COPYFROM [{}]", reg.register)
                } else {
                    write!(f, "COPYFROM {}", reg.register)
                }
            }
            Instruction::BumpPlus(reg) => {
                if reg.indirect {
                    write!(f, "BUMPUP [{}]", reg.register)
                } else {
                    write!(f, "BUMPUP {}", reg.register)
                }
            }
            Instruction::BumpMinus(reg) => {
                if reg.indirect {
                    write!(f, "BUMPDN [{}]", reg.register)
                } else {
                    write!(f, "BUMPDN {}", reg.register)
                }
            }
            Instruction::Label { label } => write!(f, "LABEL: {}", label),
            Instruction::Jump { label } => write!(f, "JUMP {}", label),
            Instruction::JumpIfZero { label } => write!(f, "JUMPZ {}", label),
            Instruction::JumpIfNegative { label } => write!(f, "JUMPN {}", label),
            Instruction::AssertValueIs { value } => write!(f, "ASSERT_VALUE {}", value),
            Instruction::AssertRegisterIs { register, value } => {
                write!(f, "ASSERT_REGISTER {} {}", register, value)
            }
        }
    }
}

pub struct Interpreter {
    instructions: Vec<Instruction>,
    registers: HashMap<Value, Value>,
    instruction_count: usize,
    value: Option<Value>,
    input: Vec<Value>,
    input_index: usize,
    execution_count: usize,
    instruction_index: usize,
    output: Vec<Value>,
    jumps: HashMap<String, usize>,
}

impl Interpreter {
    pub fn new(
        registers: HashMap<Value, Value>,
        instructions: Vec<Instruction>,
        input: Vec<Value>,
    ) -> Self {
        let mut interpreter = Self {
            instructions: instructions.clone(),
            registers,
            instruction_count: 0,
            value: None,
            input,
            input_index: 0,
            execution_count: 0,
            instruction_index: 0,
            output: Vec::new(),
            jumps: HashMap::new(),
        };

        // Count actual instructions (excluding labels and comments)
        interpreter.instruction_count = instructions
            .iter()
            .filter(|instr| {
                !matches!(
                    instr,
                    Instruction::Label { .. } | Instruction::Comment { .. }
                )
            })
            .count();

        // Build jump table
        for (index, instruction) in instructions.iter().enumerate() {
            if let Instruction::Label { label } = instruction {
                interpreter.jumps.insert(label.clone(), index);
            }
        }

        interpreter
    }

    fn read_register(&self, uses_register: &UsesRegister) -> Result<Value, String> {
        if uses_register.indirect {
            let indirect_key = self
                .registers
                .get(&uses_register.register)
                .ok_or_else(|| format!("Register {:?} not found", uses_register.register))?;
            self.registers
                .get(indirect_key)
                .cloned()
                .ok_or_else(|| format!("Indirect register {:?} not found", indirect_key))
        } else {
            self.registers
                .get(&uses_register.register)
                .cloned()
                .ok_or_else(|| format!("Register {:?} not found", uses_register.register))
        }
    }

    fn write_register(&mut self, uses_register: &UsesRegister) -> Result<(), String> {
        let value = self
            .value
            .clone()
            .ok_or_else(|| "No value to write to register".to_string())?;

        if uses_register.indirect {
            let indirect_key = self
                .registers
                .get(&uses_register.register)
                .cloned()
                .ok_or_else(|| format!("Register {:?} not found", uses_register.register))?;
            self.registers.insert(indirect_key, value);
        } else {
            self.registers.insert(uses_register.register.clone(), value);
        }
        Ok(())
    }

    pub fn execute_program(&mut self) -> Result<Vec<Value>, String> {
        while self.instruction_index < self.instructions.len() {
            if let Some(output) = self.step()? {
                return Ok(output);
            }
        }
        Ok(self.output.clone())
    }

    pub fn step(&mut self) -> Result<Option<Vec<Value>>, String> {
        if self.instruction_index >= self.instructions.len() {
            return Ok(Some(self.output.clone()));
        }

        let instruction = self.instructions[self.instruction_index].clone();
        debug!("Instruction {}: {:?}", self.instruction_index, instruction);

        match instruction {
            Instruction::Inbox => {
                if self.input_index >= self.input.len() {
                    return Ok(Some(self.output.clone())); // No more input available
                }
                self.value = Some(self.input[self.input_index].clone());
                self.input_index += 1;
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::Outbox => {
                let value = self
                    .value
                    .take()
                    .ok_or_else(|| "No value to output".to_string())?;
                self.output.push(value);
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::Add(uses_register) => {
                let current_value = self
                    .value
                    .as_ref()
                    .ok_or_else(|| "No value for addition".to_string())?
                    .as_int()?;
                let argument = self.read_register(&uses_register)?.as_int()?;
                self.value = Some(Value::Int(current_value + argument));
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::Subtract(uses_register) => {
                let current_value = self
                    .value
                    .as_ref()
                    .ok_or_else(|| "No value for subtraction".to_string())?
                    .as_int()?;
                let argument = self.read_register(&uses_register)?.as_int()?;
                self.value = Some(Value::Int(current_value - argument));
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::CopyTo(uses_register) => {
                self.write_register(&uses_register)?;
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::CopyFrom(uses_register) => {
                self.value = Some(self.read_register(&uses_register)?);
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::BumpPlus(uses_register) => {
                if uses_register.indirect {
                    let indirect_key = self
                        .registers
                        .get(&uses_register.register)
                        .cloned()
                        .ok_or_else(|| {
                            format!("Register {:?} not found", uses_register.register)
                        })?;
                    let current = self
                        .registers
                        .get(&indirect_key)
                        .ok_or_else(|| format!("Indirect register {:?} not found", indirect_key))?
                        .as_int()?;
                    let new_value = Value::Int(current + 1);
                    self.registers.insert(indirect_key, new_value.clone());
                    self.value = Some(new_value);
                } else {
                    let current = self
                        .registers
                        .get(&uses_register.register)
                        .ok_or_else(|| format!("Register {:?} not found", uses_register.register))?
                        .as_int()?;
                    let new_value = Value::Int(current + 1);
                    self.registers
                        .insert(uses_register.register.clone(), new_value.clone());
                    self.value = Some(new_value);
                }
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::BumpMinus(uses_register) => {
                if uses_register.indirect {
                    let indirect_key = self
                        .registers
                        .get(&uses_register.register)
                        .cloned()
                        .ok_or_else(|| {
                            format!("Register {:?} not found", uses_register.register)
                        })?;
                    let current = self
                        .registers
                        .get(&indirect_key)
                        .ok_or_else(|| format!("Indirect register {:?} not found", indirect_key))?
                        .as_int()?;
                    let new_value = Value::Int(current - 1);
                    self.registers.insert(indirect_key, new_value.clone());
                    self.value = Some(new_value);
                } else {
                    let current = self
                        .registers
                        .get(&uses_register.register)
                        .ok_or_else(|| format!("Register {:?} not found", uses_register.register))?
                        .as_int()?;
                    let new_value = Value::Int(current - 1);
                    self.registers
                        .insert(uses_register.register.clone(), new_value.clone());
                    self.value = Some(new_value);
                }
                self.instruction_index += 1;
                self.execution_count += 1;
            }
            Instruction::Label { .. } | Instruction::Comment { .. } => {
                self.instruction_index += 1;
                // No execution count increment for comments or labels
            }
            Instruction::Jump { label } => {
                self.instruction_index = *self
                    .jumps
                    .get(&label)
                    .ok_or_else(|| format!("Label '{}' not found", label))?;
                self.execution_count += 1;
            }
            Instruction::JumpIfZero { label } => {
                let should_jump = match &self.value {
                    Some(Value::Int(0)) => true,
                    Some(Value::String(s)) if s == "0" => true,
                    _ => false,
                };

                if should_jump {
                    self.instruction_index = *self
                        .jumps
                        .get(&label)
                        .ok_or_else(|| format!("Label '{}' not found", label))?;
                } else {
                    self.instruction_index += 1;
                }
                self.execution_count += 1;
            }
            Instruction::JumpIfNegative { label } => {
                let should_jump = match &self.value {
                    Some(Value::Int(i)) if *i < 0 => true,
                    Some(Value::String(s)) => s.parse::<i32>().map(|i| i < 0).unwrap_or(false),
                    _ => false,
                };

                if should_jump {
                    self.instruction_index = *self
                        .jumps
                        .get(&label)
                        .ok_or_else(|| format!("Label '{}' not found", label))?;
                } else {
                    self.instruction_index += 1;
                }
                self.execution_count += 1;
            }
            Instruction::AssertValueIs { value } => {
                if self.value.as_ref() != Some(&value) {
                    return Err(format!(
                        "Assertion failed: expected {:?}, got {:?}",
                        value, self.value
                    ));
                }
                self.instruction_index += 1;
            }
            Instruction::AssertRegisterIs { register, value } => {
                let register_key = Value::String(register);
                let actual = self.registers.get(&register_key);
                if actual != Some(&value) {
                    return Err(format!(
                        "Assertion failed: expected register '{}' to be {:?}, got {:?}",
                        register_key, value, actual
                    ));
                }
                self.instruction_index += 1;
            }
        }

        Ok(None)
    }

    pub fn to_string(&self) -> String {
        let mut lines = Vec::new();
        let mut index = 1;

        for instruction in &self.instructions {
            match instruction {
                Instruction::AssertValueIs { .. } | Instruction::AssertRegisterIs { .. } => {
                    continue
                }
                Instruction::Comment { text } => {
                    lines.push(format!("\"{}\"", text));
                }
                Instruction::Label { label } => {
                    lines.push(format!("LABEL: {}", label));
                }
                _ => {
                    lines.push(format!("{}: {}", index, instruction));
                    index += 1;
                }
            }
        }

        lines.join("\n")
    }

    pub fn to_dot(&self) -> String {
        let mut lines = vec!["digraph G {".to_string()];
        let mut node_map = HashMap::new();
        let mut idx_counter = 0;

        // First pass: define nodes and labels for actual instructions
        for (i, instruction) in self.instructions.iter().enumerate() {
            match instruction {
                Instruction::Comment { .. } => {
                    // Comments are not nodes in the graph
                }
                Instruction::Label { label } => {
                    let node_id = format!("\"{}\"", label);
                    node_map.insert(i, node_id.clone());
                    lines.push(format!("  {} [shape=plaintext];", node_id));
                }
                _ => {
                    let node_id = format!("instr_{}", idx_counter);
                    node_map.insert(i, node_id.clone());
                    let instr_str = instruction.to_string();
                    let shape = match instruction {
                        Instruction::Jump { .. }
                        | Instruction::JumpIfZero { .. }
                        | Instruction::JumpIfNegative { .. } => "diamond",
                        _ => "box",
                    };
                    lines.push(format!(
                        "  {} [shape={}, label=\"{}: {}\"];",
                        node_id, shape, idx_counter, instr_str
                    ));
                    idx_counter += 1;
                }
            }
        }

        // Second pass: define edges
        for (i, instruction) in self.instructions.iter().enumerate() {
            if !node_map.contains_key(&i) {
                continue; // Skip comments
            }

            let current_node_id = &node_map[&i];

            // Find next instruction index, skipping comments
            let mut next_instr_idx = i + 1;
            while next_instr_idx < self.instructions.len()
                && matches!(
                    self.instructions[next_instr_idx],
                    Instruction::Comment { .. }
                )
            {
                next_instr_idx += 1;
            }

            let next_node_exists =
                next_instr_idx < self.instructions.len() && node_map.contains_key(&next_instr_idx);
            let next_node_id = node_map.get(&next_instr_idx);

            match instruction {
                Instruction::Jump { label } => {
                    if let Some(target_idx) = self.jumps.get(label) {
                        if let Some(target_node) = node_map.get(target_idx) {
                            lines.push(format!("  {} -> {};", current_node_id, target_node));
                        }
                    }
                }
                Instruction::JumpIfZero { label } => {
                    if let Some(target_idx) = self.jumps.get(label) {
                        if let Some(target_node) = node_map.get(target_idx) {
                            lines.push(format!(
                                "  {} -> {} [label=\"if zero\"];",
                                current_node_id, target_node
                            ));
                        }
                    }
                    if next_node_exists {
                        if let Some(next_node) = next_node_id {
                            lines.push(format!(
                                "  {} -> {} [label=\"not zero\"];",
                                current_node_id, next_node
                            ));
                        }
                    }
                }
                Instruction::JumpIfNegative { label } => {
                    if let Some(target_idx) = self.jumps.get(label) {
                        if let Some(target_node) = node_map.get(target_idx) {
                            lines.push(format!(
                                "  {} -> {} [label=\"if negative\"];",
                                current_node_id, target_node
                            ));
                        }
                    }
                    if next_node_exists {
                        if let Some(next_node) = next_node_id {
                            lines.push(format!(
                                "  {} -> {} [label=\"not negative\"];",
                                current_node_id, next_node
                            ));
                        }
                    }
                }
                Instruction::Label { .. } => {
                    // Labels point to the next actual instruction
                    if next_node_exists {
                        if let Some(next_node) = next_node_id {
                            lines.push(format!("  {} -> {};", current_node_id, next_node));
                        }
                    }
                }
                Instruction::Comment { .. } => {
                    // Comments are already skipped
                }
                _ => {
                    // Default sequential flow for other instructions
                    if next_node_exists {
                        if let Some(next_node) = next_node_id {
                            lines.push(format!("  {} -> {};", current_node_id, next_node));
                        }
                    }
                }
            }
        }

        lines.push("}".to_string());
        lines.join("\n")
    }

    pub fn executions(&self) -> usize {
        self.execution_count
    }

    pub fn instruction_count(&self) -> usize {
        self.instruction_count
    }

    pub fn registers_len(&self) -> usize {
        self.registers.len()
    }

    pub fn input_string(&self) -> String {
        self.input
            .iter()
            .map(|v| v.to_string())
            .collect::<Vec<_>>()
            .join(", ")
    }
}
