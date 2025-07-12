use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum TokenKind {
    Argument,
    Comment,
    Instruction,
    Label,
}

impl fmt::Display for TokenKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TokenKind::Argument => write!(f, "ARGUMENT"),
            TokenKind::Comment => write!(f, "COMMENT"),
            TokenKind::Instruction => write!(f, "INSTRUCTION"),
            TokenKind::Label => write!(f, "LABEL"),
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct Token {
    pub kind: TokenKind,
    pub value: String,
    pub line: usize,
}

impl Token {
    pub fn new(kind: TokenKind, value: String, line: usize) -> Self {
        Self { kind, value, line }
    }
}

impl fmt::Display for Token {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Token({}, '{}', {})", self.kind, self.value, self.line)
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum InstructionType {
    Inbox,
    Outbox,
    CopyFrom,
    CopyTo,
    Add,
    Sub,
    BumpUp,
    BumpDn,
    Jump,
    JumpZ,
    JumpN,
}

impl InstructionType {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_uppercase().as_str() {
            "INBOX" => Some(InstructionType::Inbox),
            "OUTBOX" => Some(InstructionType::Outbox),
            "COPYFROM" => Some(InstructionType::CopyFrom),
            "COPYTO" => Some(InstructionType::CopyTo),
            "ADD" => Some(InstructionType::Add),
            "SUB" => Some(InstructionType::Sub),
            "BUMPUP" => Some(InstructionType::BumpUp),
            "BUMPDN" => Some(InstructionType::BumpDn),
            "JUMP" => Some(InstructionType::Jump),
            "JUMPZ" => Some(InstructionType::JumpZ),
            "JUMPN" => Some(InstructionType::JumpN),
            _ => None,
        }
    }
}

pub struct Lexer {
    source: String,
}

impl Lexer {
    pub fn new(source: &str) -> Self {
        Self {
            source: source.to_string(),
        }
    }

    pub fn tokenize(&self) -> Result<Vec<Token>, String> {
        let mut tokens = Vec::new();

        for (line_number, line) in self.source.lines().enumerate() {
            let line_number = line_number + 1;
            let line = line.trim();

            if line.is_empty() {
                continue;
            }

            if line.starts_with('#') {
                tokens.push(Token::new(
                    TokenKind::Comment,
                    line[1..].trim().to_string(),
                    line_number,
                ));
                continue;
            }

            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.is_empty() {
                continue;
            }

            let first_part = parts[0];
            let remaining_parts = &parts[1..];

            if let Some(_instruction_type) = InstructionType::from_str(first_part) {
                tokens.push(Token::new(
                    TokenKind::Instruction,
                    first_part.to_string(),
                    line_number,
                ));
                for arg in remaining_parts {
                    tokens.push(Token::new(
                        TokenKind::Argument,
                        arg.to_string(),
                        line_number,
                    ));
                }
                continue;
            }

            if first_part.ends_with(':') {
                tokens.push(Token::new(
                    TokenKind::Label,
                    first_part[..first_part.len() - 1].to_string(),
                    line_number,
                ));
                continue;
            }

            return Err(format!("Failed to parse line {}: {}", line_number, line));
        }

        Ok(tokens)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tokenize_simple_code() {
        let source = r#"# This is a comment
BEGIN:
INBOX
OUTBOX
JUMP BEGIN"#;

        let lexer = Lexer::new(source);
        let tokens = lexer.tokenize().unwrap();

        assert_eq!(tokens.len(), 6);
        assert_eq!(
            tokens[0],
            Token::new(TokenKind::Comment, "This is a comment".to_string(), 1)
        );
        assert_eq!(
            tokens[1],
            Token::new(TokenKind::Label, "BEGIN".to_string(), 2)
        );
        assert_eq!(
            tokens[2],
            Token::new(TokenKind::Instruction, "INBOX".to_string(), 3)
        );
        assert_eq!(
            tokens[3],
            Token::new(TokenKind::Instruction, "OUTBOX".to_string(), 4)
        );
        assert_eq!(
            tokens[4],
            Token::new(TokenKind::Instruction, "JUMP".to_string(), 5)
        );
        assert_eq!(
            tokens[5],
            Token::new(TokenKind::Argument, "BEGIN".to_string(), 5)
        );
    }
}
