# Personal Operating System (POS)

A Textual-based TUI application for personal knowledge management and task tracking.

## Features

- **Work Item Management**: Track tasks, learning items, and research items
- **Thought Evolution Tracker**: Capture and evolve thoughts over time
- **Integration**: Link thoughts to work items and track relationships

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pos.git
cd pos
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
- Windows:
```bash
.venv\Scripts\activate
```
- macOS/Linux:
```bash
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

Or use the run script:
```bash
python run.py
```

## Project Structure

```
src/
├── __init__.py           # Package initialization
├── app.py                # Main Textual application
├── config.py             # Configuration and paths
├── database.py           # Database operations
├── migrations.py         # Schema migration system
├── models.py             # Data models (WorkItem, ThoughtNode)
├── thought_manager.py    # Business logic for thought operations
├── screens/              # Textual screens
│   ├── __init__.py       # Screen package initialization
│   ├── base_screen.py    # Base screen with common functionality
│   ├── dashboard.py      # Main dashboard screen
│   ├── error_screen.py   # Error display screen
│   ├── settings.py       # Settings and configuration screen
│   ├── thoughts.py       # Thought management screen
│   └── work_items.py     # Work item management screen
└── ui/                   # Reusable UI components
    └── __init__.py       # UI components package initialization

assets/                   # CSS and other assets
data/                     # Application data
├── db/                   # Database files
├── backups/              # Database backups
└── logs/                 # Application logs
```

## Navigation

- **Dashboard**: Overview of work items and thoughts
- **Work Items**: Manage tasks, learning items, and research items
- **Thoughts**: Track thought evolution and relationships
- **Settings**: Configure application settings

## Keyboard Shortcuts

- **q**: Quit the application
- **d**: Toggle dark mode
- **?**: Show help
- **b**: Go back to previous screen

## Development

### Adding a New Feature

1. Update the data models in `src/models.py` if needed
2. Add database operations in `src/database.py`
3. Implement business logic in appropriate manager classes
4. Create or update screens in `src/screens/`
5. Update the UI components in `src/ui/` if needed

### Running Tests

```bash
python -m unittest discover tests
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 