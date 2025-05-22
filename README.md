# Personal Operating System (POS)

A terminal-based personal task and knowledge management system built with Python and the Textual framework (v3.2.0).

## Overview

POS is designed to help track work items, goals, and thoughts through an interactive Terminal User Interface (TUI). The application provides a structured way to manage personal information, link related items, and visualize relationships between different pieces of knowledge.

## Core Features

- Create and manage work items through a form-based interface
- Link items with semantic relationship types 
- Visualize thought hierarchies and evolution
- Filter and search across your knowledge base
- Navigate efficiently using keyboard shortcuts and command palette

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Launch the application: `python main.py`

## Project Structure

- `src/` - Core application code 
- `data/` - Database and storage location
- `docs/` - Documentation including PROJECT_SCOPE.md

## Project Status

POS is currently using Textual 3.2.0 for its interface (v0.4.0), with the legacy CLI functionality deprecated.

## Documentation

For detailed information about the project's scope and implementation strategy, see [Project Scope](docs/PROJECT_SCOPE.md).

## Validation Runner

Run built-in validation protocols from the command line:

```bash
python -m src.pos_tui.validation.run --all
```

Use `--list` to display protocols or `--protocol <name>` to run one.
