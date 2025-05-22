# Personal Operating System (POS)

A terminal-based personal task and knowledge management system built with Python and the Textual framework.

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

## Running Validation Protocols

The project includes a self-validating framework to verify feature behavior. You can run all available validations or target specific protocols using the console script:

```bash
# Run every protocol
python -m src.pos_tui.validation.run

# Run a subset of protocols
python -m src.pos_tui.validation.run item_editing edit_modal
```

Results are written to `data/validation_results/` in JSON format. See [docs/validation_protocols.md](docs/validation_protocols.md) for details.

## Project Structure

- `src/` - Core application code 
- `data/` - Database and storage location
- `docs/` - Documentation including PROJECT_SCOPE.md

## Project Status

POS is currently transitioning to a Textual-first interface (v0.2.0), with the legacy CLI functionality being deprecated.

## Documentation

For detailed information about the project's scope and implementation strategy, see [Project Scope](docs/PROJECT_SCOPE.md).
