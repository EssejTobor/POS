"""
Validation protocol for Item Management features.

This module provides validation scripts for item creation, editing, and deletion.
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


class ItemEditingValidation(ValidationProtocol):
    """Validation protocol for item editing functionality."""
    
    def __init__(self):
        super().__init__("item_editing")
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
                goal="test",
                title=item_data["title"],
                description=item_data["description"],
                item_type=item_data["item_type"],
                priority=item_data["priority"],
            )
            ws.update_item(item.id, status=item_data["status"])
            item_ids.append(item.id)
        
        # Create some links if the method is available
        if hasattr(ws, "add_link") and len(item_ids) >= 2:
            ws.add_link(item_ids[0], item_ids[1], "references")
        
        self.result.add_note(f"Created temporary database at {temp_db_file.name} with {len(item_ids)} items")
        return temp_db_file.name
    
    def _run_validation(self) -> None:
        """Run validation for item editing."""
        try:
            # Create a temporary database
            self.temp_db = self._setup_test_db()
            
            # 1. Validate edit operation
            self._validate_edit_operation()
            
            # 2. Validate delete operation
            self._validate_delete_operation()
            
            # 3. Validate optimistic UI updates (simulated)
            self._validate_optimistic_updates()
        finally:
            # Clean up temporary database
            if self.temp_db and os.path.exists(self.temp_db):
                os.unlink(self.temp_db)
                self.result.add_note(f"Removed temporary database at {self.temp_db}")
    
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
        
        ws.update_item(
            item_id,
            title=new_title,
            status=new_status.value,
        )
        
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
        
        item_id = next(iter(ws.items.keys()))
        original_item = WorkItem.from_dict(ws.items[item_id].to_dict())
        
        # 1. Capture state before modification
        before_state = dump_database_state(self.temp_db)
        
        # 2. Simulate modifying the UI optimistically
        # (This would be updating the DataTable cells directly in the real app)
        self.result.add_note("Simulating optimistic UI update...")
        
        # 3. Prepare update data
        update_title = f"Optimistic: {original_item.title}"

        # 4. In the real app, we'd update the UI immediately and then
        # initiate an async task to update the database. Here we'll just
        # call the update directly since we can't test UI components.
        ws.update_item(
            item_id,
            title=update_title,
            priority=Priority.HI.value,
        )
        
        # 5. Verify the change persisted to the database
        updated_item = ws.items[item_id]
        after_state = dump_database_state(self.temp_db)
        
        if updated_item.title == update_title:
            self.result.add_pass("Database update for optimistic UI change succeeded")
        else:
            self.result.add_fail(
                f"Database update failed. Expected title '{update_title}', got '{updated_item.title}'"
            )
        
        # 6. Simulate undo operation
        # In the real app, this would be triggered by a button in a toast notification
        ws.update_item(
            item_id,
            title=original_item.title,
            priority=original_item.priority.value,
        )
        
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
    # Run item editing validation
    item_editing = ItemEditingValidation()
    item_editing.validate()


if __name__ == "__main__":
    run_all_validations() 