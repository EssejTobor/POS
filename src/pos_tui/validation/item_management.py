"""Validation protocol for item management features.

This module provides validation scripts for item creation, editing, deletion,
and optimistic update behaviour.  It uses a temporary database so the
validation can run without side effects on the real data store.
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import ValidationProtocol, ValidationResult
from src.pos_tui.validation.introspect import dump_database_state, compare_database_states
from src.models import ItemType, Priority, ItemStatus, WorkItem
from src.storage import WorkSystem


class ItemManagementValidation(ValidationProtocol):
    """Validation protocol for item creation and editing functionality."""
    
    def __init__(self):
        # keep protocol name stable for backward compatibility
        super().__init__("item_management")
        self.temp_db = None
    
    def _setup_test_db(self) -> str:
        """Create a temporary database with test data."""
        # Create a temporary file for the database
        temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db_file.close()
        
        # Initialize work system with the temporary database
        ws = WorkSystem(temp_db_file.name)
        
        # Add test items
        test_items = [
            {
                "title": "Test Task 1",
                "description": "This is a test task",
                "item_type": ItemType.TASK,
                "priority": Priority.HI,
                "status": ItemStatus.NOT_STARTED
            },
            {
                "title": "Test Thought 1",
                "description": "This is a test thought",
                "item_type": ItemType.THOUGHT,
                "priority": Priority.MED,
                "status": ItemStatus.IN_PROGRESS
            },
            {
                "title": "Test Learning 1",
                "description": "This is a test learning item",
                "item_type": ItemType.LEARNING,
                "priority": Priority.LOW,
                "status": ItemStatus.COMPLETED
            }
        ]
        
        item_ids = []
        for item_data in test_items:
            item = ws.add_item(
                goal="validation",
                title=item_data["title"],
                item_type=item_data["item_type"],
                description=item_data["description"],
                priority=item_data["priority"],
            )
            ws.update_item(item.id, status=item_data["status"].value)
            item_ids.append(item.id)
        
        # Create some links if the method is available
        if hasattr(ws, "add_link") and len(item_ids) >= 2:
            ws.add_link(item_ids[0], item_ids[1], "references")
        
        self.result.add_note(f"Created temporary database at {temp_db_file.name} with {len(item_ids)} items")
        return temp_db_file.name

    def _run_validation(self) -> None:
        """Run validation for item creation and editing."""
        try:
            # Create a temporary database
            self.temp_db = self._setup_test_db()

            # 1. Validate create operation
            self._validate_create_operation()

            # 2. Validate edit operation
            self._validate_edit_operation()

            # 3. Validate delete operation
            self._validate_delete_operation()

            # 4. Validate optimistic UI updates (simulated)
            self._validate_optimistic_updates()
        finally:
            # Clean up temporary database
            if self.temp_db and os.path.exists(self.temp_db):
                os.unlink(self.temp_db)
                self.result.add_note(f"Removed temporary database at {self.temp_db}")

    def _validate_create_operation(self) -> None:
        """Validate basic item creation."""
        ws = WorkSystem(self.temp_db)

        before_state = dump_database_state(self.temp_db)
        count_before = len(ws.items)

        new_item = ws.add_item(
            goal="validation",
            title="New Item",
            item_type=ItemType.TASK,
            description="Created from validation",
            priority=Priority.MED,
        )
        ws.update_item(new_item.id, status=ItemStatus.IN_PROGRESS.value)

        after_state = dump_database_state(self.temp_db)

        if new_item.id in ws.items:
            self.result.add_pass("Item created and stored in WorkSystem")
        else:
            self.result.add_fail("New item missing from WorkSystem cache")

        if len(ws.items) == count_before + 1:
            self.result.add_pass("Item count increased after creation")
        else:
            self.result.add_fail("Item count did not increase after creation")

        if new_item.id in after_state.get("items", {}):
            self.result.add_pass("Database state includes new item")
        else:
            self.result.add_fail("Database state missing new item")
    
    def _validate_edit_operation(self) -> None:
        """Validate basic edit operation."""
        # Initialize work system with the temporary database
        ws = WorkSystem(self.temp_db)
        
        # Get the first item
        if not ws.items:
            self.result.add_fail("No items found in test database")
            return
        
        item_id = next(iter(ws.items.keys()))
        original_item = ws.items[item_id]
        
        # Capture original state
        original_state = dump_database_state(self.temp_db)
        
        # Edit the item
        new_title = f"Edited: {original_item.title}"
        new_status = ItemStatus.IN_PROGRESS if original_item.status != ItemStatus.IN_PROGRESS else ItemStatus.COMPLETED
        
        edit_data = {
            "title": new_title,
            "status": new_status.value
        }
        
        ws.update_item(item_id, **edit_data)
        
        # Capture updated state
        updated_state = dump_database_state(self.temp_db)
        
        # Verify changes
        updated_item = ws.items[item_id]
        
        if updated_item.title == new_title:
            self.result.add_pass(f"Item title updated successfully to '{new_title}'")
        else:
            self.result.add_fail(f"Item title not updated. Expected '{new_title}', got '{updated_item.title}'")
        
        if updated_item.status == new_status:
            self.result.add_pass(f"Item status updated successfully to '{new_status.name}'")
        else:
            self.result.add_fail(f"Item status not updated. Expected '{new_status.name}', got '{updated_item.status.name}'")
        
        # Check that other fields remain unchanged
        unchanged_fields = {
            "item_type": (original_item.item_type, updated_item.item_type),
            "description": (original_item.description, updated_item.description),
            "priority": (original_item.priority, updated_item.priority)
        }
        
        for field, (original, updated) in unchanged_fields.items():
            if original == updated:
                self.result.add_pass(f"Unmodified field '{field}' preserved correctly")
            else:
                self.result.add_fail(f"Unmodified field '{field}' changed unexpectedly from '{original}' to '{updated}'")
    
    def _validate_delete_operation(self) -> None:
        """Validate basic delete operation."""
        # Initialize work system with the temporary database
        ws = WorkSystem(self.temp_db)
        
        # Get an item to delete
        if len(ws.items) < 2:
            self.result.add_fail("Not enough items for delete validation")
            return
        
        # Use the second item to leave one for other tests
        item_id = list(ws.items.keys())[1]
        
        # Capture original state
        original_state = dump_database_state(self.temp_db)
        original_count = len(ws.items)
        
        # Delete the item
        ws.delete_item(item_id)
        
        # Capture updated state
        updated_state = dump_database_state(self.temp_db)
        updated_count = len(ws.items)
        
        # Verify deletion
        if item_id not in ws.items:
            self.result.add_pass(f"Item {item_id} deleted successfully")
        else:
            self.result.add_fail(f"Item {item_id} still exists after deletion")
        
        if updated_count == original_count - 1:
            self.result.add_pass(f"Item count decreased by 1 (from {original_count} to {updated_count})")
        else:
            self.result.add_fail(f"Item count inconsistent: {original_count} before, {updated_count} after")
    
    def _validate_optimistic_updates(self) -> None:
        """
        Validate optimistic UI updates (simulated).
        
        Note: We can't actually test the UI directly here, so we'll check the underlying
        functionality and data flow that enables optimistic updates.
        """
        # Simulate steps that would happen during optimistic UI update
        
        # Initialize work system with the temporary database
        ws = WorkSystem(self.temp_db)
        
        # Get an item to work with
        if not ws.items:
            self.result.add_fail("No items for optimistic update validation")
            return
        
        import copy
        item_id = next(iter(ws.items.keys()))
        original_item = copy.deepcopy(ws.items[item_id])  # Make a copy for later comparison
        
        # 1. Capture state before modification
        before_state = dump_database_state(self.temp_db)
        
        # 2. Simulate modifying the UI optimistically
        # (This would be updating the DataTable cells directly in the real app)
        self.result.add_note("Simulating optimistic UI update...")
        
        # 3. Prepare update data
        update_data = {
            "title": f"Optimistic: {original_item.title}",
            "priority": Priority.HI.value
        }
        
        # 4. In the real app, we'd update the UI immediately and then
        # initiate an async task to update the database. Here we'll just
        # call the update directly since we can't test UI components.
        ws.update_item(item_id, **update_data)
        
        # 5. Verify the change persisted to the database
        updated_item = ws.items[item_id]
        after_state = dump_database_state(self.temp_db)
        
        if updated_item.title == update_data["title"]:
            self.result.add_pass("Database update for optimistic UI change succeeded")
        else:
            self.result.add_fail(f"Database update failed. Expected title '{update_data['title']}', got '{updated_item.title}'")
        
        # 6. Simulate undo operation
        original_data = {
            "title": original_item.title,
            "priority": original_item.priority.value
        }
        
        # In the real app, this would be triggered by a button in a toast notification
        ws.update_item(item_id, **original_data)
        
        # Verify undo worked
        restored_item = ws.items[item_id]
        if restored_item.title == original_item.title:
            self.result.add_pass("Undo operation restored original title")
        else:
            self.result.add_fail(f"Undo operation failed. Expected title '{original_item.title}', got '{restored_item.title}'")
        
        if restored_item.priority == original_item.priority:
            self.result.add_pass("Undo operation restored original priority")
        else:
            self.result.add_fail(f"Undo operation failed. Expected priority '{original_item.priority}', got '{restored_item.priority}'")


def run_all_validations() -> None:
    """Run all item management validations."""
    validation = ItemManagementValidation()
    validation.validate()


if __name__ == "__main__":
    run_all_validations()

# Backwards compatibility
ItemEditingValidation = ItemManagementValidation
