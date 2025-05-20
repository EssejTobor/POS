import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import Database
from src.models import ItemStatus, ItemType, Priority, WorkItem


class TestItemTags(unittest.TestCase):
    """Tests for the item_tags table and helper methods."""

    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db = Database(self.temp_db.name)

        self.item = WorkItem(
            id="TEST-1",
            title="Test Item",
            goal="TestGoal",
            item_type=ItemType.TASK,
            description="Desc",
            priority=Priority.MED,
            status=ItemStatus.NOT_STARTED,
        )
        self.db.add_item(self.item)

    def tearDown(self) -> None:
        self.temp_db.close()
        os.unlink(self.temp_db.name)

    def test_tag_crud(self) -> None:
        self.assertTrue(self.db.add_tag(self.item.id, "alpha"))
        self.assertFalse(self.db.add_tag(self.item.id, "alpha"))
        self.assertIn("alpha", self.db.get_tags(self.item.id))
        self.assertTrue(self.db.remove_tag(self.item.id, "alpha"))
        self.assertEqual(self.db.get_tags(self.item.id), [])

    def test_get_items_by_tag(self) -> None:
        other = WorkItem(
            id="TEST-2",
            title="Other",
            goal="TestGoal",
            item_type=ItemType.TASK,
            description="Desc",
            priority=Priority.LOW,
            status=ItemStatus.NOT_STARTED,
        )
        self.db.add_item(other)

        self.db.add_tag(self.item.id, "common")
        self.db.add_tag(other.id, "common")

        items = self.db.get_items_by_tag("common")
        ids = {i.id for i in items}
        self.assertEqual(ids, {self.item.id, other.id})

    def test_get_items_by_filters_tag_only(self) -> None:
        other = WorkItem(
            id="TEST-3",
            title="Other",
            goal="TestGoal",
            item_type=ItemType.TASK,
            description="Desc",
            priority=Priority.LOW,
            status=ItemStatus.NOT_STARTED,
        )
        self.db.add_item(other)

        self.db.add_tag(self.item.id, "special")
        self.db.add_tag(other.id, "special")

        items = self.db.get_items_by_filters(tag="special")
        ids = {i.id for i in items}
        self.assertEqual(ids, {self.item.id, other.id})


if __name__ == "__main__":
    unittest.main()
