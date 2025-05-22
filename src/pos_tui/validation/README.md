# First-Principles Validation Framework

This directory contains a validation framework for the POS application that follows a first-principles approach without relying on external testing frameworks.

## Core Philosophy

The validation framework is built on these key principles:

1. **Self-Validation** - Features should validate their own correctness
2. **Introspection** - Examining system state directly rather than through abstractions
3. **Simulation** - Validating UI components by simulating their lifecycle and events
4. **Documentation** - Capturing and storing validation results for future reference

## Getting Started

### Running Validations

```bash
# Run all validation protocols
python -m src.pos_tui.validation.run

# List available protocols
python -m src.pos_tui.validation.run --list

# Run specific protocols
python -m src.pos_tui.validation.run item_editing edit_modal
```

### Available Validation Protocols

- `item_editing` - Validates item editing, deletion, and optimistic UI functionality
- `edit_modal` - Validates the EditItemModal component
- `item_table` - Validates the ItemTable component

### Validation Results

Results are displayed in the console and saved to JSON files in `data/validation_results/`.

## Directory Structure

- `__init__.py` - Core validation framework
- `run.py` - Validation runner with command-line interface
- `introspect.py` - Database and system state inspection utilities
- `item_management.py` - Validation protocols for item management features
- `ui_components.py` - Validation protocols for UI components

## Adding New Validation Protocols

To create a new validation protocol:

1. Create a new subclass of `ValidationProtocol` in the appropriate module
2. Implement the `_run_validation()` method with validation logic
3. Register the protocol in `run.py`
4. Document the protocol in `docs/validation_protocols.md`

Example:

```python
from src.pos_tui.validation import ValidationProtocol

class MyFeatureValidation(ValidationProtocol):
    def __init__(self):
        super().__init__("my_feature")
    
    def _run_validation(self) -> None:
        # Implement validation logic
        self.result.add_pass("Feature works correctly")
        
        # If something doesn't work:
        # self.result.add_fail("Feature failed to...")
        
        # Add warnings or notes
        self.result.add_warning("Consider optimizing...")
        self.result.add_note("Created temporary resources...")
```

## Utilities

### Database Introspection

Use `introspect.py` to examine database state:

```python
from src.pos_tui.validation.introspect import dump_database_state

# Dump database state
before_state = dump_database_state("path/to/database.db")

# Perform some operation
perform_operation()

# Dump state again
after_state = dump_database_state("path/to/database.db")

# Compare states
from src.pos_tui.validation.introspect import compare_database_states
is_identical, differences = compare_database_states(before_state, after_state)
```

### UI Component Simulation

Use `UIComponentSimulator` to validate UI components:

```python
from src.pos_tui.validation.ui_components import UIComponentSimulator
from src.pos_tui.widgets.my_widget import MyWidget

# Create simulator
simulator = UIComponentSimulator(MyWidget, param1="value1")

# Get component instance
widget = simulator.instantiate()

# Simulate lifecycle events
simulator.simulate_mount()

# Simulate other events
simulator.simulate_event("button_pressed", button_id="submit")
```

## Documentation

For more details, see:
- `docs/validation_protocols.md` - Detailed validation protocols
- `AGENTS.md` - Development workflow with validation
- `docs/checklist.md` - Implementation tracking with validation status 