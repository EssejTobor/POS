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
            except Exception as e:
                self.result.add_fail(f"Modal mount simulation failed: {str(e)}")
                return
            
            # Check for required methods
            required_methods = [
                "on_mount",
                "on_item_entry_form_item_submitted",
                "on_button_pressed",
                "dismiss",
            ]
            
            for method_name in required_methods:
                if hasattr(modal, method_name):
                    self.result.add_pass(f"Modal has required method: {method_name}")
                else:
                    self.result.add_fail(f"Modal missing required method: {method_name}")
            
            # Simulate form submission event
            test_data = {
                "title": "Updated Title",
                "item_type": ItemType.TASK.value,
                "priority": Priority.HIGH.value,
                "status": ItemStatus.IN_PROGRESS.value,
                "description": "Updated description"
            }
            
            # Create a message-like object
            class MockSubmittedMessage:
                def __init__(self, data):
                    self.item_data = data
            
            # Simulate receiving the message
            try:
                if hasattr(modal, "on_item_entry_form_item_submitted"):
                    modal.on_item_entry_form_item_submitted(MockSubmittedMessage(test_data))
                    self.result.add_pass("Successfully simulated form submission event")
                else:
                    self.result.add_fail("Could not simulate form submission - method missing")
            except Exception as e:
                self.result.add_fail(f"Form submission simulation failed: {str(e)}")

            # Simulate cancel button press and check dismiss
            from textual.widgets import Button
            dismiss_called = {"flag": False}

            def fake_dismiss(result: bool | None = None) -> None:
                dismiss_called["flag"] = True

            if hasattr(modal, "dismiss"):
                modal.dismiss = fake_dismiss
                try:
                    modal.on_button_pressed(Button.Pressed(Button("Cancel", id="cancel_button")))
                    if dismiss_called["flag"]:
                        self.result.add_pass("Cancel button triggers dismiss")
                    else:
                        self.result.add_fail("Cancel button did not trigger dismiss")
                except Exception as e:  # pragma: no cover - just in case
                    self.result.add_fail(f"Button press handling failed: {e}")
        
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
            
            # Simulate mount
            try:
                simulator.simulate_mount()
                self.result.add_pass("Table mount simulation successful")
            except Exception as e:
                # Textual tables require an active App; if unavailable record warning
                from textual._context import NoActiveAppError
                if isinstance(e, NoActiveAppError):
                    self.result.add_warning("Table mount skipped (no active app)")
                else:
                    self.result.add_fail(f"Table mount simulation failed: {str(e)}")
                    return
            
            # Check for columns definition capability
            if hasattr(table, "add_columns"):
                self.result.add_pass("Table supports adding columns")
            else:
                self.result.add_fail("Table missing add_columns method")
            
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
                "ViewRequested",
                "EditRequested",
                "DeleteRequested",
            ]
            
            for class_name in message_classes:
                if hasattr(table, class_name):
                    self.result.add_pass(f"Table has message class: {class_name}")
                else:
                    self.result.add_fail(f"Table missing message class: {class_name}")

            # Verify action methods exist
            for action_method in [
                "action_edit_selected",
                "action_view_selected",
                "action_delete_selected",
            ]:
                if hasattr(table, action_method):
                    self.result.add_pass(f"Table has {action_method} method")
                else:
                    self.result.add_fail(f"Table missing {action_method} method")
        
        except ImportError as e:
            self.result.add_fail(f"Failed to import ItemTable: {str(e)}")


def run_ui_validations() -> None:
    """Run all UI component validations."""
    # Validate EditItemModal
    edit_modal = EditItemModalValidation()
    edit_modal.validate()
    
    # Validate ItemTable
    item_table = ItemTableValidation()
    item_table.validate()


if __name__ == "__main__":
    run_ui_validations() 