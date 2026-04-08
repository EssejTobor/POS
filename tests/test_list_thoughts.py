import unittest
import os
import sys
import tempfile
import io
from contextlib import redirect_stdout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import ItemType
from src.storage import WorkSystem
from src.cli import WorkSystemCLI

class TestListThoughts(unittest.TestCase):
    """Tests for the thought listing functionality"""
    
    def setUp(self):
        """Set up a temporary database and CLI for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system
        
        # Add some test items
        self.thought1 = self.work_system.add_item(
            goal="TestGoal1",
            title="Test Thought 1",
            item_type=ItemType.THOUGHT,
            description="This is a test thought"
        )
        
        self.thought2 = self.work_system.add_item(
            goal="TestGoal2",
            title="Test Thought 2",
            item_type=ItemType.THOUGHT,
            description="This is another test thought"
        )
        
        self.task = self.work_system.add_item(
            goal="TestGoal1",
            title="Test Task",
            item_type=ItemType.TASK,
            description="This is a test task"
        )
        
    def tearDown(self):
        """Clean up after each test"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        
    def test_get_items_by_type(self):
        """Test the get_items_by_type method in WorkSystem"""
        # Get all thought items
        thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        
        # Verify we get only thoughts
        self.assertEqual(len(thoughts), 2)
        self.assertTrue(all(t.item_type == ItemType.THOUGHT for t in thoughts))
        
        # Verify task items are separate
        tasks = self.work_system.get_items_by_type(ItemType.TASK)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(all(t.item_type == ItemType.TASK for t in tasks))
        
    def test_list_thoughts_command(self):
        """Test the list_thoughts command in CLI"""
        # Capture output
        captured_output = io.StringIO()
        
        # Execute command and capture output
        with redirect_stdout(captured_output):
            self.cli.onecmd("list_thoughts")
        
        # Verify output contains the thought titles
        output = captured_output.getvalue()
        self.assertIn("Test Thought 1", output)
        self.assertIn("Test Thought 2", output)
        self.assertNotIn("Test Task", output)  # Task should not be listed
        
    def test_list_thoughts_by_goal(self):
        """Test the list_thoughts command filtered by goal"""
        # Capture output
        captured_output = io.StringIO()
        
        # Execute command and capture output
        with redirect_stdout(captured_output):
            self.cli.onecmd("list_thoughts TestGoal1")
        
        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Test Thought 1", output)
        self.assertNotIn("Test Thought 2", output)  # This is in TestGoal2
        self.assertNotIn("Test Task", output)  # Task should not be listed
        
    def test_list_command_thoughts_filter(self):
        """Test the 'list thoughts' command using the general list command"""
        # Capture output
        captured_output = io.StringIO()
        
        # Execute command and capture output
        with redirect_stdout(captured_output):
            self.cli.onecmd("list thoughts")
        
        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Test Thought 1", output)
        self.assertIn("Test Thought 2", output)
        self.assertNotIn("Test Task", output)  # Task should not be listed
        
if __name__ == '__main__':
    unittest.main() 