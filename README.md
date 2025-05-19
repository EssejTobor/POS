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

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pos.git
cd pos
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Usage

After installation, you can run the application using:

```bash
pos
```

Or run it directly using:

```bash
python run.py
```

### Textual UI

Install the optional [Textual](https://textual.textualize.io) library to use the
interactive TUI:

```bash
pip install textual
```

Launch the interface with:

```bash
tui
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
├── requirements.txt
├── setup.py         # Package configuration
└── run.py          # Main entry point
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 