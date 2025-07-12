mod interpreter;
mod lexer;
mod parser;

use clap::Parser;
use log::info;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::Path;

use interpreter::{Interpreter, Value};
use parser::Parser as HRMParser;

#[derive(Debug, Deserialize, Serialize)]
struct Level {
    source: String,
    input: Option<String>,
    registers: HashMap<String, String>,
    #[serde(rename = "speed-challenge")]
    speed_challenge: i32,
    #[serde(rename = "size-challenge")]
    size_challenge: i32,
}

impl Level {
    fn from_yaml(path: &Path) -> Result<Self, Box<dyn std::error::Error>> {
        let content = fs::read_to_string(path)?;
        let level: Level = serde_yaml::from_str(&content)?;
        Ok(level)
    }

    fn get_input(&self) -> Vec<Value> {
        self.input
            .as_ref()
            .map(|input| {
                input
                    .lines()
                    .filter(|line| !line.is_empty())
                    .map(int_or_str)
                    .collect()
            })
            .unwrap_or_default()
    }

    fn get_registers(&self) -> HashMap<Value, Value> {
        self.registers
            .iter()
            .map(|(k, v)| (int_or_str(k), int_or_str(v)))
            .collect()
    }
}

fn int_or_str(value: &str) -> Value {
    value
        .parse::<i32>()
        .map(Value::Int)
        .unwrap_or_else(|_| Value::String(value.to_string()))
}

#[derive(Parser)]
#[command(name = "hrm")]
#[command(about = "Human Resource Machine Interpreter")]
struct Args {
    /// Level to execute
    path: String,

    /// Enable debug logging
    #[arg(long)]
    debug_logging: bool,

    /// Output the program in dotfile format to the specified path
    #[arg(long)]
    dotfile: Option<String>,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();

    if args.debug_logging {
        env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("debug")).init();
    } else {
        env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();
    }

    info!("Starting Human Resource Machine Interpreter");

    let path = if Path::new(&args.path).is_absolute() {
        args.path.clone()
    } else {
        format!("src/xyz/human_resource_machine/challenges/{}", args.path)
    };

    let level = Level::from_yaml(Path::new(&path))?;

    let mut parser = HRMParser::new(&level.source);
    let instructions = parser.parse()?;

    let mut interpreter = Interpreter::new(level.get_registers(), instructions, level.get_input());

    let output = interpreter.execute_program()?;

    println!("{}\n", interpreter.to_string());
    println!("Input: {}", interpreter.input_string());
    println!("Output: {}", value_vec_to_string(&output));
    println!("Registers used: {}", interpreter.registers_len());
    println!(
        "Execution count: {} target: {}",
        interpreter.executions(),
        level.speed_challenge
    );
    println!(
        "Size challenge: {} target: {}",
        interpreter.instruction_count(),
        level.size_challenge
    );

    if let Some(dotfile_path) = args.dotfile {
        fs::write(&dotfile_path, interpreter.to_dot())?;
        println!("Dotfile written to {}", dotfile_path);
    }

    Ok(())
}

fn value_vec_to_string(values: &[Value]) -> String {
    values
        .iter()
        .map(|v| match v {
            Value::Int(i) => i.to_string(),
            Value::String(s) => s.clone(),
        })
        .collect::<Vec<_>>()
        .join(", ")
}
