import os
import sys
import tempfile
import unittest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import Database
from src.models import ItemStatus, ItemType, Priority, WorkItem
from src.storage import WorkSystem


class TestThoughtItem(unittest.TestCase):
    """Tests for the new THOUGHT item type functionality"""

    def setUp(self):
        """Set up a new database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db = Database(self.temp_db.name)
        self.work_system = WorkSystem(self.temp_db.name)

    def tearDown(self):
        """Clean up after each test"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)

    def test_create_thought_item(self):
        """Test creating a thought item directly"""
        # Create a thought item directly
        thought = WorkItem(
            id="test-thought-1",
            title="Test Thought",
            goal="TestGoal",
            item_type=ItemType.THOUGHT,
            description="This is a test thought",
            priority=Priority.MED,
            status=ItemStatus.NOT_STARTED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Add it to the database
        self.db.add_item(thought)

        # Retrieve it and verify
        retrieved = self.db.get_item("test-thought-1")
        self.assertIsNotNone(retrieved, "Thought item should be retrievable")
        self.assertEqual(
            retrieved.item_type, ItemType.THOUGHT, "Item type should be THOUGHT"
        )
        self.assertEqual(
            retrieved.item_type.value, "th", "Item type value should be 'th'"
        )

    def test_add_thought_via_worksystem(self):
        """Test adding a thought item via WorkSystem"""
        # Add a thought item via the WorkSystem
        thought = self.work_system.add_item(
            goal="TestGoal",
            title="WorkSystem Thought",
            item_type=ItemType.THOUGHT,
            description="This is a thought added through WorkSystem",
        )

        # Verify the item was created correctly
        self.assertEqual(
            thought.item_type, ItemType.THOUGHT, "Item type should be THOUGHT"
        )

        # Check the ID generation
        self.assertTrue("th" in thought.id, "Thought ID should contain 'th'")

        # Retrieve it from the database directly
        retrieved = self.db.get_item(thought.id)
        self.assertIsNotNone(
            retrieved, "Thought item should be retrievable from database"
        )
        self.assertEqual(
            retrieved.item_type,
            ItemType.THOUGHT,
            "Retrieved item type should be THOUGHT",
        )

    def test_filter_thoughts(self):
        """Test filtering for thought items"""
        # Add a thought item and a regular task
        thought = self.work_system.add_item(
            goal="TestGoal",
            title="Filter Test Thought",
            item_type=ItemType.THOUGHT,
            description="This is a thought for testing filters",
        )

        self.work_system.add_item(
            goal="TestGoal",
            title="Filter Test Task",
            item_type=ItemType.TASK,
            description="This is a task for testing filters",
        )

        # Get all items of type THOUGHT
        thoughts = self.db.get_items_by_type(ItemType.THOUGHT)

        # Verify only the thought item is returned
        self.assertEqual(len(thoughts), 1, "Should find exactly one thought item")
        self.assertEqual(thoughts[0].id, thought.id, "The thought ID should match")
        self.assertEqual(
            thoughts[0].item_type, ItemType.THOUGHT, "Item type should be THOUGHT"
        )

        # Verify filtering via WorkSystem also works
        ws_thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        self.assertEqual(
            len(ws_thoughts), 1, "WorkSystem should find exactly one thought item"
        )
        self.assertEqual(ws_thoughts[0].id, thought.id, "The thought ID should match")


if __name__ == "__main__":
    unittest.main()
