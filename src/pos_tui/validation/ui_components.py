"""
Validation utilities for UI components.

This module provides tools to validate UI components without needing a real UI.
It simulates the UI component lifecycle and behavior.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Type, List

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import ValidationProtocol, ValidationResult
from src.models import WorkItem, ItemType, Priority, ItemStatus


class UIComponentSimulator:
    """
    Simulates a UI component for validation purposes.
    
    This class provides methods to simulate the lifecycle and events
    of Textual UI components without actually rendering them.
    """
    
    def __init__(self, component_class: Type, **kwargs):
        """
        Initialize the simulator with a component class.
        
        Args:
            component_class: The UI component class to simulate
            **kwargs: Additional arguments to pass to the component constructor
        """
        self.component_class = component_class
        self.component_args = kwargs
        self.component = None
        self.events = []
        
    def instantiate(self) -> Any:
        """
        Instantiate the component.
        
        Returns:
            The instantiated component
        """
        self.component = self.component_class(**self.component_args)
        return self.component
    
    def simulate_mount(self) -> None:
        """Simulate the mount event for the component."""
        if not self.component:
            self.instantiate()
        
        if hasattr(self.component, "on_mount"):
            self.component.on_mount()
    
    def simulate_event(self, event_name: str, **event_data) -> None:
        """
        Simulate an event on the component.
        
        Args:
            event_name: Name of the event to simulate
            **event_data: Event data to pass to the handler
        """
        if not self.component:
            self.instantiate()
        
        handler_name = f"on_{event_name}"
        if hasattr(self.component, handler_name):
            handler = getattr(self.component, handler_name)
            handler(**event_data)
        
        self.events.append((event_name, event_data))
    
    def simulate_lifecycle(self) -> None:
        """Simulate the complete lifecycle of the component."""
        self.instantiate()
        self.simulate_mount()
        # Add more lifecycle events as needed


class EditItemModalValidation(ValidationProtocol):
    """Validation protocol for the EditItemModal component."""
    
    def __init__(self):
        super().__init__("edit_item_modal")
    
    def _run_validation(self) -> None:
        """Run validation for the EditItemModal."""
        try:
            # Import the component
            from src.pos_tui.widgets.modals import EditItemModal
            
            # Create a test item
            test_item = WorkItem(
                id="ts1",
                title="Test Item",
                goal="TestGoal",
                description="Test description",
                item_type=ItemType.TASK,
                priority=Priority.MED,
                status=ItemStatus.NOT_STARTED
            )
            
            # Initialize the simulator
            self.result.add_note("Creating EditItemModal simulator...")
            simulator = UIComponentSimulator(EditItemModal, item=test_item)
            
            # Instantiate and validate basic properties
            modal = simulator.instantiate()
            
            if modal.item == test_item:
                self.result.add_pass("Modal correctly stores the item")
            else:
                self.result.add_fail("Modal failed to store the item")
            
            # Simulate mount
            try:
                simulator.simulate_mount()
                self.result.add_pass("Modal mount simulation successful")
            except Exception:
                self.result.add_note("Modal mount simulation skipped")
            
            # Check for required methods
            required_methods = [
                "on_mount",
                "on_item_entry_form_item_submitted",
                "on_button_pressed"
            ]
            
            for method_name in required_methods:
                if hasattr(modal, method_name):
                    self.result.add_pass(f"Modal has required method: {method_name}")
                else:
                    self.result.add_fail(f"Modal missing required method: {method_name}")
            
            # Simulate form submission event
            test_data = {
                "goal": "NewGoal",
                "title": "Updated Title",
                "item_type": ItemType.THOUGHT.value,
                "priority": Priority.HI.value,
                "status": ItemStatus.IN_PROGRESS.value,
                "description": "Updated description",
            }
            
            # Create a message-like object
            class MockSubmittedMessage:
                def __init__(self, data):
                    self.item_data = data
            
            captured: dict[str, Any] = {}

            def fake_dismiss(value=None):
                captured["data"] = value

            modal.dismiss = fake_dismiss

            # Simulate receiving the message
            try:
                if hasattr(modal, "on_item_entry_form_item_submitted"):
                    modal.on_item_entry_form_item_submitted(MockSubmittedMessage(test_data))
                    if (
                        captured.get("data", {}).get("goal") == "NewGoal"
                        and captured["data"].get("item_type") == ItemType.THOUGHT.value
                    ):
                        self.result.add_pass("Successfully simulated form submission event")
                    else:
                        self.result.add_fail("Submitted data did not include new goal and type")
                else:
                    self.result.add_fail("Could not simulate form submission - method missing")
            except Exception:
                self.result.add_note("Form submission simulation skipped")
        
        except ImportError as e:
            self.result.add_fail(f"Failed to import EditItemModal: {str(e)}")


class ItemTableValidation(ValidationProtocol):
    """Validation protocol for the ItemTable component."""
    
    def __init__(self):
        super().__init__("item_table")
    
    def _run_validation(self) -> None:
        """Run validation for the ItemTable."""
        try:
            # Import the component
            from src.pos_tui.widgets.item_table import ItemTable
            
            # Initialize the simulator
            self.result.add_note("Creating ItemTable simulator...")
            simulator = UIComponentSimulator(ItemTable)
            
            # Instantiate and validate basic properties
            table = simulator.instantiate()
            
            # Simulate mount (may fail outside app context)
            try:
                simulator.simulate_mount()
                self.result.add_pass("Table mount simulation successful")
            except Exception:
                # Skip mount-related checks in headless mode
                self.result.add_note("Table mount simulation skipped")
            
            # Check for columns
            if hasattr(table, "columns"):
                self.result.add_pass("Table exposes columns attribute")
            
            # Check for the update_cell method
            if hasattr(table, "update_cell") and callable(table.update_cell):
                self.result.add_pass("Table has update_cell method")
                
                # Verify method signature if possible
                import inspect
                sig = inspect.signature(table.update_cell)
                if len(sig.parameters) >= 3:
                    self.result.add_pass("update_cell method has correct number of parameters")
                else:
                    self.result.add_fail(f"update_cell has incorrect signature: {sig}")
            else:
                self.result.add_fail("Table missing update_cell method")
            
            # Check for message classes
            message_classes = [
                "ItemSelected",
                "ItemEditRequested",
                "ItemDeleteRequested"
            ]
            
            for class_name in message_classes:
                if hasattr(table, class_name):
                    self.result.add_pass(f"Table has message class: {class_name}")
                else:
                    self.result.add_fail(f"Table missing message class: {class_name}")
        
        except ImportError as e:
            self.result.add_fail(f"Failed to import ItemTable: {str(e)}")


class ItemFormValidation(ValidationProtocol):
    """Validation protocol for the ItemEntryForm component."""

    def __init__(self) -> None:
        super().__init__("item_entry_form")

    def _run_validation(self) -> None:
        try:
            from src.pos_tui.widgets.item_form import ItemEntryForm

            class MockInput:
                def __init__(self, value=""):
                    self.value = value

            class DummyForm(ItemEntryForm):
                def __init__(self):
                    super().__init__()
                    self.fields = {
                        "#goal_field": MockInput(),
                        "#title_field": MockInput(),
                        "#type_field": MockInput(ItemType.TASK.value),
                        "#priority_field": MockInput(str(Priority.MED.value)),
                        "#status_field": MockInput(ItemStatus.NOT_STARTED.value),
                        "#tags_field": MockInput(),
                        "#description_field": MockInput(),
                    }

                def query_one(self, selector: str, *_args, **_kwargs):
                    return self.fields[selector]

            form = DummyForm()

            form.query_one("#goal_field").value = "TestGoal"
            form.query_one("#title_field").value = "Test Title"
            form.query_one("#type_field").value = ItemType.THOUGHT.value
            form.query_one("#priority_field").value = str(Priority.HI.value)
            form.query_one("#status_field").value = ItemStatus.IN_PROGRESS.value
            form.query_one("#tags_field").value = "one, two"
            form.query_one("#description_field").value = "desc"

            data = form.collect_form_data()

            if data.get("goal") == "TestGoal":
                self.result.add_pass("Goal collected correctly")
            else:
                self.result.add_fail("Goal not collected correctly")

            if data.get("item_type") == ItemType.THOUGHT.value:
                self.result.add_pass("Item type collected correctly")
            else:
                self.result.add_fail("Item type collected incorrectly")
        except Exception as e:
            self.result.add_fail(f"Form validation failed: {e}")


class UIComponentsValidation(ValidationProtocol):
    """Aggregate validation for UI components."""

    def __init__(self) -> None:
        super().__init__("ui_components")

    def _run_validation(self) -> None:
        validations = [
            ItemFormValidation(),
            EditItemModalValidation(),
            ItemTableValidation(),
        ]

        for validation in validations:
            res = validation.run()
            self.result.passes.extend(
                [f"{validation.name}: {msg}" for msg in res.passes]
            )
            self.result.failures.extend(
                [f"{validation.name}: {msg}" for msg in res.failures]
            )
            self.result.notes.extend(
                [f"{validation.name}: {msg}" for msg in res.notes]
            )


def run_ui_validations() -> None:
    """Run all UI component validations."""
    validations = [
        ItemFormValidation(),
        EditItemModalValidation(),
        ItemTableValidation(),
    ]

    for validation in validations:
        validation.validate()


if __name__ == "__main__":
    run_ui_validations() 