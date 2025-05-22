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
from src.storage import WorkSystem


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


class ItemFormModalValidation(ValidationProtocol):
    """Validation protocol for the ItemFormModal component."""
    
    def __init__(self):
        super().__init__("item_form_modal")
    
    def _run_validation(self) -> None:
        """Run validation for the ItemFormModal."""
        try:
            # Import the component
            from src.pos_tui.widgets.item_form_modal import ItemFormModal
            from textual.widgets import Input
            ws = WorkSystem(":memory:")
            
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
            self.result.add_note("Creating ItemFormModal simulator...")
            simulator = UIComponentSimulator(ItemFormModal, item=test_item, work_system=ws)
            
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

            # Dirty state should start False
            if hasattr(modal, "dirty") and not modal.dirty:
                self.result.add_pass("Modal starts clean")
            else:
                self.result.add_fail("Modal should start with dirty=False")

            # Check for required methods
            required_methods = [
                "_update_dirty",
                "_attempt_close",
                "on_item_entry_form_save_result",
                "on_item_entry_form_cancelled",
            ]
            
            for method_name in required_methods:
                if hasattr(modal, method_name):
                    self.result.add_pass(f"Modal has required method: {method_name}")
                else:
                    self.result.add_fail(f"Modal missing required method: {method_name}")

            
            # Skipping form submission simulation since the modal delegates
            # handling to the embedded form widget
        
        except ImportError as e:
            self.result.add_fail(f"Failed to import ItemFormModal: {str(e)}")


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
                self.result.add_fail(f"Table mount simulation failed: {str(e)}")
                return
            
            # Check for columns
            if hasattr(table, "columns") and len(table.columns) >= 6:
                self.result.add_pass("Table has expected columns")
            else:
                self.result.add_fail("Table missing expected columns")
            
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


def run_ui_validations() -> None:
    """Run all UI component validations."""
    # Validate ItemFormModal
    form_modal = ItemFormModalValidation()
    form_modal.validate()
    
    # Validate ItemTable
    item_table = ItemTableValidation()
    item_table.validate()


if __name__ == "__main__":
    run_ui_validations() 