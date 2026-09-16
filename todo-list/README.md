# To-Do List CLI

A small persistent command-line to-do list built with Python. It stores tasks in a local JSON file, so the list survives between commands without requiring a database or external service.

## Features

- Add tasks with input validation
- List all, pending, or completed tasks
- Mark tasks as completed
- Delete tasks
- Atomic JSON-file writes to reduce the risk of corrupting the task file
- Automated tests for core behavior and failure cases
- Configurable data-file location through `TODO_LIST_DATA_FILE`

## Requirements

- Python 3.11 or newer

The application has no runtime third-party dependencies.

## Setup

From the `todo-list` directory:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\\.venv\\Scripts\\Activate.ps1
```

Windows Command Prompt:

```cmd
.venv\\Scripts\\activate.bat
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install the project and test dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

## Usage

Add a task:

```bash
todo add "Finish Python project"
```

List every task:

```bash
todo list
```

List only pending or completed tasks:

```bash
todo list --status pending
todo list --status completed
```

Mark a task complete using its ID:

```bash
todo done TASK_ID
```

Delete a task:

```bash
todo delete TASK_ID
```

By default, tasks are stored at `~/.todo-list/tasks.json`. To use another location, set `TODO_LIST_DATA_FILE` before running the command.

PowerShell:

```powershell
$env:TODO_LIST_DATA_FILE = "$PWD\\tasks.json"
```

Command Prompt:

```cmd
set TODO_LIST_DATA_FILE=%CD%\\tasks.json
```

Linux/macOS:

```bash
export TODO_LIST_DATA_FILE="$PWD/tasks.json"
```

## Architecture

The application is split into small layers:

- `models.py` defines the task data model and serialization rules.
- `storage.py` owns JSON persistence and atomic file replacement.
- `service.py` contains task-management rules without CLI concerns.
- `cli.py` handles command-line parsing, output, and process-level errors.

This keeps business behavior testable without invoking the command line and makes the persistence layer replaceable if the project later needs a database.

## Project structure

```text
todo-list/
├── .gitignore
├── README.md
├── pyproject.toml
├── src/
│   └── todo_list/
│       ├── __init__.py
│       ├── cli.py
│       ├── models.py
│       ├── service.py
│       └── storage.py
└── tests/
    ├── test_service.py
    └── test_storage.py
```

## Tests

Run the complete test suite with:

```bash
python -m pytest
```

The tests cover task creation and validation, completion, deletion, filtering, missing-task errors, corrupt storage, and persistence round trips.

## License

MIT
