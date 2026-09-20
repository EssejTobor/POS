# Personal Organization System (POS)

A command-line interface (CLI) tool for managing work items, tasks, and personal organization.

## Features

- Create and manage work items with titles, descriptions, and goals
- Organize items by priority and status
- Track progress and completion of tasks
- Backup and restore functionality
- Export data to JSON format
- Command-line interface with rich text formatting

## Installation

Use Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/).
`pyproject.toml` and `uv.lock` are the dependency source of truth.
`.python-version` selects the 3.13 family; the interpreter patch version is not pinned.

1. Clone the repository:
```bash
git clone https://github.com/EssejTobor/POS.git
cd POS
```

2. Install the project and development tools into `.venv`:
```bash
uv sync --locked --all-groups --all-extras
```

This installs the editable `pos` package and its CLI entry point. Textual is an
optional `tui` extra for future work; installing it does not add a working TUI.
No database server, credentials, or external services are required.

## Usage

After installation, you can run the application using:

```bash
uv run --locked pos
```

Or run it directly using:

```bash
uv run --locked python run.py
```

## Project Structure

```
pos/                      # Root project directory
├── src/                 # Source code directory
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── database.py     # Database operations
│   ├── display.py      # Display formatting
│   └── ...
├── tests/              # Test directory
│   ├── __init__.py
│   └── ...
├── data/              # Data directory
│   ├── db/           # Database files
│   └── backups/      # Backup files
├── docs/             # Documentation
├── .venv/            # Virtual environment (not in source control)
├── .gitignore
├── README.md
├── pyproject.toml   # Package and development dependencies
├── uv.lock          # Resolved dependency versions
└── run.py          # Main entry point
```

## Development

See [Codex Cloud environment setup](docs/codex-environment.md) for container
settings, validation commands, and the current test baseline.

When intentionally changing dependencies, edit `pyproject.toml`, run `uv lock`,
and review both files together. Routine setup uses `--locked` so it fails rather
than silently changing the resolved environment. Ruff and mypy are available
through `uv run --locked`; existing code is not guaranteed to pass them.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

This could also be known as the “piece of shit” (POS) application. I was trying to build from first principles to understand all the friction involved in manually tracking self-help habits. So I started from scratch — raw files, no frameworks, no guardrails — just to feel the pain. And...it was unbearable, but insightful.

I intended to implement a full textual interface (still broken), and while I’ve mostly abandoned this, I’d genuinely be happy to collaborate if you find any part of it interesting.


1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
