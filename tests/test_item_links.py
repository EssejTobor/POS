import unittest
import os
import sys
import tempfile
import uuid
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import Database
from src.models import WorkItem, ItemType, ItemStatus, Priority

class TestItemLinks(unittest.TestCase):
    """Tests for the new item_links table and related functionality"""
    
    def setUp(self):
        """Set up a new database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db = Database(self.temp_db.name)
        
        # Create some test items
        self.item1 = WorkItem(
            id=f"TEST1-{uuid.uuid4().hex[:6]}",
            title="Test Item 1",
            goal="TestGoal",
            item_type=ItemType.TASK,
            description="Test description 1",
            priority=Priority.MED,
            status=ItemStatus.NOT_STARTED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.item2 = WorkItem(
            id=f"TEST2-{uuid.uuid4().hex[:6]}",
            title="Test Item 2",
            goal="TestGoal",
            item_type=ItemType.LEARNING,
            description="Test description 2",
            priority=Priority.LOW,
            status=ItemStatus.NOT_STARTED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add items to the database
        self.db.add_item(self.item1)
        self.db.add_item(self.item2)
        
    def tearDown(self):
        """Clean up after each test"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        
    def test_add_link(self):
        """Test adding a link between two items"""
        # Add a link from item1 to item2
        result = self.db.add_link(self.item1.id, self.item2.id, "references")
        self.assertTrue(result, "Link should be added successfully")
        
        # Try to add the same link again (should fail silently due to PRIMARY KEY constraint)
        result = self.db.add_link(self.item1.id, self.item2.id, "references")
        self.assertFalse(result, "Adding duplicate link should return False")
        
        # Try to add a link with non-existent source_id
        result = self.db.add_link("non-existent-id", self.item2.id)
        self.assertFalse(result, "Adding link with non-existent source should return False")
        
        # Try to add a link with non-existent target_id
        result = self.db.add_link(self.item1.id, "non-existent-id")
        self.assertFalse(result, "Adding link with non-existent target should return False")
        
    def test_remove_link(self):
        """Test removing a link between two items"""
        # First add a link
        self.db.add_link(self.item1.id, self.item2.id, "references")
        
        # Now remove it
        result = self.db.remove_link(self.item1.id, self.item2.id)
        self.assertTrue(result, "Link should be removed successfully")
        
        # Try to remove a non-existent link
        result = self.db.remove_link(self.item1.id, self.item2.id)
        self.assertFalse(result, "Removing non-existent link should return False")
        
    def test_get_links(self):
        """Test getting links for an item"""
        # Add two links: item1 -> item2 and item2 -> item1
        self.db.add_link(self.item1.id, self.item2.id, "references")
        self.db.add_link(self.item2.id, self.item1.id, "evolves-from")
        
        # Get links for item1
        links1 = self.db.get_links(self.item1.id)
        self.assertEqual(len(links1['outgoing']), 1, "Item1 should have one outgoing link")
        self.assertEqual(len(links1['incoming']), 1, "Item1 should have one incoming link")
        self.assertEqual(links1['outgoing'][0]['target_id'], self.item2.id, "Outgoing link should point to item2")
        self.assertEqual(links1['outgoing'][0]['link_type'], "references", "Link type should be 'references'")
        self.assertEqual(links1['incoming'][0]['source_id'], self.item2.id, "Incoming link should come from item2")
        self.assertEqual(links1['incoming'][0]['link_type'], "evolves-from", "Link type should be 'evolves-from'")
        
        # Get links for item2
        links2 = self.db.get_links(self.item2.id)
        self.assertEqual(len(links2['outgoing']), 1, "Item2 should have one outgoing link")
        self.assertEqual(len(links2['incoming']), 1, "Item2 should have one incoming link")
        
        # Get links for non-existent item
        links_none = self.db.get_links("non-existent-id")
        self.assertEqual(len(links_none['outgoing']), 0, "Non-existent item should have no outgoing links")
        self.assertEqual(len(links_none['incoming']), 0, "Non-existent item should have no incoming links")
        
if __name__ == '__main__':
    unittest.main() 