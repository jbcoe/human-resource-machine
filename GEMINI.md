# Instructions for Gemini when working with the PyFun repository

## Package Management and Virtual Environments

This repository uses uv for managing dependencies and virtual environments.

If you need to add a dependency, use the following command:

```bash
uv add <PACKAGE_NAME>
```

**Important:** Do not use `pip` or `venv` for managing dependencies or virtual
environments in this repository.

## Pre-commit Checks

All changes must pass pre-commit checks before being committed.

To run the checks, use the following command:

```bash
uv run pre-commit run --all-files
```

## Python Tests

After any edits, all Python tests must be run and must pass. Run the tests from
the repository root using the following command:

```bash
uv sync --all-packages ; uv run pytest .
```

**Important:** Tests MUST pass after every change. Do not modify tests, without
explicit user approval, to make them pass.

## Code Comments

Comments should not be used to talk to the user. Comments must be minimal and
should explain *why* things are being done, not *what* is being done. Rely on
clear and descriptive naming to communicate *what* is happening in the code.

## Docstrings and Type Hints

All new methods must have docstrings that detail what a function does, its
arguments, and its return values/types.

All new methods must have type hints. Type hints can be checked using the
following command from the repository root:

```bash
uvx run mypy .
```

## Conversation and API References

During any conversation, it is important to consider corner cases.

Any references to APIs must be accompanied by supporting links and
documentation. Do not speculate about APIs; always use references
(code or documentation).
