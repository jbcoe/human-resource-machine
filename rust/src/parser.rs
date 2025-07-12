use crate::interpreter::{Instruction, UsesRegister, Value};
use crate::lexer::{InstructionType, Lexer, Token, TokenKind};

pub struct Parser {
    tokens: Vec<Token>,
    current_token_index: usize,
}

impl Parser {
    pub fn new(source: &str) -> Self {
        let lexer = Lexer::new(source);
        let tokens = lexer.tokenize().unwrap_or_else(|_| Vec::new());
        Self {
            tokens,
            current_token_index: 0,
        }
    }

    fn current_token(&self) -> Option<&Token> {
        self.tokens.get(self.current_token_index)
    }

    fn step(&mut self) {
        self.current_token_index += 1;
    }

    fn int_or_str(value: &str) -> Value {
        value
            .parse::<i32>()
            .map(Value::Int)
            .unwrap_or_else(|_| Value::String(value.to_string()))
    }

    fn parse_with_register_arg(
        &mut self,
        instruction_type: InstructionType,
    ) -> Result<Instruction, String> {
        if self.current_token().map(|t| &t.kind) != Some(&TokenKind::Instruction) {
            return Err(format!(
                "Expected instruction, but got {:?}",
                self.current_token()
            ));
        }

        self.step();
        let token = self
            .current_token()
            .ok_or("Expected argument after instruction")?;

        if token.kind != TokenKind::Argument {
            return Err(format!("Expected argument, but got {:?}", token));
        }

        let register_str = &token.value;
        let (register, indirect) = if register_str.starts_with('[') && register_str.ends_with(']') {
            let inner = &register_str[1..register_str.len() - 1];
            (Self::int_or_str(inner), true)
        } else {
            (Self::int_or_str(register_str), false)
        };

        let uses_register = if indirect {
            UsesRegister::new_indirect(register)
        } else {
            UsesRegister::new(register)
        };

        Ok(match instruction_type {
            InstructionType::CopyFrom => Instruction::CopyFrom(uses_register),
            InstructionType::CopyTo => Instruction::CopyTo(uses_register),
            InstructionType::Add => Instruction::Add(uses_register),
            InstructionType::Sub => Instruction::Subtract(uses_register),
            InstructionType::BumpUp => Instruction::BumpPlus(uses_register),
            InstructionType::BumpDn => Instruction::BumpMinus(uses_register),
            _ => {
                return Err(format!(
                    "Instruction type {:?} does not use registers",
                    instruction_type
                ))
            }
        })
    }

    fn parse_with_label_arg(
        &mut self,
        instruction_type: InstructionType,
    ) -> Result<Instruction, String> {
        if self.current_token().map(|t| &t.kind) != Some(&TokenKind::Instruction) {
            return Err(format!(
                "Expected instruction, but got {:?}",
                self.current_token()
            ));
        }

        self.step();
        let token = self
            .current_token()
            .ok_or("Expected argument after instruction")?;

        if token.kind != TokenKind::Argument {
            return Err(format!("Expected argument, but got {:?}", token));
        }

        let label = token.value.clone();

        Ok(match instruction_type {
            InstructionType::Jump => Instruction::Jump { label },
            InstructionType::JumpZ => Instruction::JumpIfZero { label },
            InstructionType::JumpN => Instruction::JumpIfNegative { label },
            _ => {
                return Err(format!(
                    "Instruction type {:?} does not use labels",
                    instruction_type
                ))
            }
        })
    }

    fn parse_instruction(&mut self) -> Result<Instruction, String> {
        let token = self.current_token().ok_or("Expected token")?;

        if token.kind != TokenKind::Instruction {
            return Err(format!("Expected instruction, got {:?}", token.kind));
        }

        let instruction_type = InstructionType::from_str(&token.value)
            .ok_or_else(|| format!("Unknown instruction: {}", token.value))?;

        match instruction_type {
            InstructionType::Inbox => Ok(Instruction::Inbox),
            InstructionType::Outbox => Ok(Instruction::Outbox),
            InstructionType::CopyFrom
            | InstructionType::CopyTo
            | InstructionType::Add
            | InstructionType::Sub
            | InstructionType::BumpUp
            | InstructionType::BumpDn => self.parse_with_register_arg(instruction_type),
            InstructionType::Jump | InstructionType::JumpZ | InstructionType::JumpN => {
                self.parse_with_label_arg(instruction_type)
            }
        }
    }

    pub fn parse(&mut self) -> Result<Vec<Instruction>, String> {
        let mut instructions = Vec::new();

        while let Some(token) = self.current_token() {
            match token.kind {
                TokenKind::Instruction => {
                    let instruction = self.parse_instruction()?;
                    instructions.push(instruction);
                }
                TokenKind::Label => {
                    instructions.push(Instruction::Label {
                        label: token.value.clone(),
                    });
                }
                TokenKind::Comment => {
                    instructions.push(Instruction::Comment {
                        text: token.value.clone(),
                    });
                }
                TokenKind::Argument => {
                    return Err(format!("Unexpected argument token: {:?}", token));
                }
            }
            self.step();
        }

        Ok(instructions)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_code() {
        let source = r#"# This is a comment
BEGIN:
INBOX
OUTBOX
JUMP BEGIN"#;

        let mut parser = Parser::new(source);
        let instructions = parser.parse().unwrap();

        assert_eq!(instructions.len(), 5);

        match &instructions[0] {
            Instruction::Comment { text } => assert_eq!(text, "This is a comment"),
            _ => panic!("Expected comment instruction"),
        }

        match &instructions[1] {
            Instruction::Label { label } => assert_eq!(label, "BEGIN"),
            _ => panic!("Expected label instruction"),
        }

        assert!(matches!(instructions[2], Instruction::Inbox));
        assert!(matches!(instructions[3], Instruction::Outbox));

        match &instructions[4] {
            Instruction::Jump { label } => assert_eq!(label, "BEGIN"),
            _ => panic!("Expected jump instruction"),
        }
    }

    #[test]
    fn test_parse_code_with_registers() {
        let test_cases = vec![
            ("COPYTO A", "CopyTo", "A", false),
            ("COPYTO [A]", "CopyTo", "A", true),
            ("COPYFROM B", "CopyFrom", "B", false),
            ("COPYFROM [B]", "CopyFrom", "B", true),
            ("ADD C", "Add", "C", false),
            ("ADD [C]", "Add", "C", true),
            ("SUB D", "Subtract", "D", false),
            ("SUB [D]", "Subtract", "D", true),
            ("BUMPUP E", "BumpPlus", "E", false),
            ("BUMPUP [E]", "BumpPlus", "E", true),
            ("BUMPDN F", "BumpMinus", "F", false),
            ("BUMPDN [F]", "BumpMinus", "F", true),
        ];

        for (source, expected_type, register, is_indirect) in test_cases {
            let mut parser = Parser::new(source);
            let instructions = parser.parse().unwrap();

            assert_eq!(instructions.len(), 1);

            let expected_register = Value::String(register.to_string());

            match &instructions[0] {
                Instruction::CopyTo(uses_register) if expected_type == "CopyTo" => {
                    assert_eq!(uses_register.register, expected_register);
                    assert_eq!(uses_register.indirect, is_indirect);
                }
                Instruction::CopyFrom(uses_register) if expected_type == "CopyFrom" => {
                    assert_eq!(uses_register.register, expected_register);
                    assert_eq!(uses_register.indirect, is_indirect);
                }
                Instruction::Add(uses_register) if expected_type == "Add" => {
                    assert_eq!(uses_register.register, expected_register);
                    assert_eq!(uses_register.indirect, is_indirect);
                }
                Instruction::Subtract(uses_register) if expected_type == "Subtract" => {
                    assert_eq!(uses_register.register, expected_register);
                    assert_eq!(uses_register.indirect, is_indirect);
                }
                Instruction::BumpPlus(uses_register) if expected_type == "BumpPlus" => {
                    assert_eq!(uses_register.register, expected_register);
                    assert_eq!(uses_register.indirect, is_indirect);
                }
                Instruction::BumpMinus(uses_register) if expected_type == "BumpMinus" => {
                    assert_eq!(uses_register.register, expected_register);
                    assert_eq!(uses_register.indirect, is_indirect);
                }
                _ => panic!(
                    "Unexpected instruction type for {}: {:?}",
                    source, instructions[0]
                ),
            }
        }
    }

    #[test]
    fn test_parse_jumps() {
        let test_cases = vec![
            ("JUMP START", "Jump", "START"),
            ("JUMPZ ZERO", "JumpIfZero", "ZERO"),
            ("JUMPN NEGATIVE", "JumpIfNegative", "NEGATIVE"),
        ];

        for (source, expected_type, label) in test_cases {
            let mut parser = Parser::new(source);
            let instructions = parser.parse().unwrap();

            assert_eq!(instructions.len(), 1);

            match &instructions[0] {
                Instruction::Jump { label: l } if expected_type == "Jump" => {
                    assert_eq!(l, label);
                }
                Instruction::JumpIfZero { label: l } if expected_type == "JumpIfZero" => {
                    assert_eq!(l, label);
                }
                Instruction::JumpIfNegative { label: l } if expected_type == "JumpIfNegative" => {
                    assert_eq!(l, label);
                }
                _ => panic!(
                    "Unexpected instruction type for {}: {:?}",
                    source, instructions[0]
                ),
            }
        }
    }
}
