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
from src.schemas import AddItemInput

class TestUnifiedAddCommand(unittest.TestCase):
    """Tests for the unified add command with thought support"""
    
    def setUp(self):
        """Set up a temporary database and CLI for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system
        
    def tearDown(self):
        """Clean up after each test"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        
    def test_add_thought_via_add_command(self):
        """Test adding a thought item using the unified add command"""
        # Capture output
        captured_output = io.StringIO()
        
        # Add a thought using the add command
        with redirect_stdout(captured_output):
            self.cli.onecmd("add TestGoal-th-MED-Test Thought-This is a test thought")
        
        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Added:", output)
        
        # Verify a thought was added
        thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        self.assertEqual(len(thoughts), 1)
        self.assertEqual(thoughts[0].title, "Test Thought")
        self.assertEqual(thoughts[0].item_type, ItemType.THOUGHT)
        
    def test_add_thought_with_linking(self):
        """Test adding a thought with linking using the unified add command"""
        # First add a regular item to link to
        task = self.work_system.add_item(
            goal="TestGoal",
            title="Test Task",
            item_type=ItemType.TASK,
            description="This is a test task"
        )
        
        # Capture output
        captured_output = io.StringIO()
        
        # Add a thought with linking
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"add TestGoal-th-MED-Linked Thought-This references a task --link-to {task.id}")
        
        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Added:", output)
        self.assertIn("Linked to:", output)
        
        # Verify a thought was added
        thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        self.assertEqual(len(thoughts), 1)
        
        # Verify link was created
        links = self.work_system.get_links(thoughts[0].id)
        self.assertEqual(len(links['outgoing']), 1)
        self.assertEqual(links['outgoing'][0]['target_id'], task.id)
        self.assertEqual(links['outgoing'][0]['link_type'], "references")  # Default link type
        
    def test_add_thought_with_custom_link_type(self):
        """Test adding a thought with custom link type"""
        # First add a thought to link to
        thought1 = self.work_system.add_item(
            goal="TestGoal",
            title="Original Thought",
            item_type=ItemType.THOUGHT,
            description="This is the original thought"
        )
        
        # Capture output
        captured_output = io.StringIO()
        
        # Add a thought with linking and custom link type
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"add TestGoal-th-MED-Evolution-This evolves the original --link-to {thought1.id} --link-type evolves-from")
        
        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Added:", output)
        self.assertIn("Linked to:", output)
        self.assertIn("evolves-from", output)
        
        # Verify a thought was added
        thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        self.assertEqual(len(thoughts), 2)
        
        # Find the new thought
        thought2 = next(t for t in thoughts if t.id != thought1.id)
        
        # Verify link was created with correct type
        links = self.work_system.get_links(thought2.id)
        self.assertEqual(len(links['outgoing']), 1)
        self.assertEqual(links['outgoing'][0]['target_id'], thought1.id)
        self.assertEqual(links['outgoing'][0]['link_type'], "evolves-from")
        
    def test_schema_parsing(self):
        """Test the updated AddItemInput schema parsing"""
        # Basic command with no linking
        cmd = "TestGoal-th-MED-Test Thought-This is a test thought"
        input_data = AddItemInput.parse_input(cmd)
        self.assertEqual(input_data.goal, "TestGoal")
        self.assertEqual(input_data.type_, "th")
        self.assertEqual(input_data.priority, "MED")
        self.assertEqual(input_data.title, "Test Thought")
        self.assertEqual(input_data.description, "This is a test thought")
        self.assertIsNone(input_data.link_to)
        self.assertEqual(input_data.link_type, "references")  # Default link type
        
        # Command with link_to
        cmd = "TestGoal-th-MED-Test Thought-This is a test thought --link-to abc123"
        input_data = AddItemInput.parse_input(cmd)
        self.assertEqual(input_data.goal, "TestGoal")
        self.assertEqual(input_data.type_, "th")
        self.assertEqual(input_data.title, "Test Thought")
        self.assertEqual(input_data.link_to, "abc123")
        self.assertEqual(input_data.link_type, "references")  # Default link type
        
        # Command with link_to and link_type
        cmd = "TestGoal-th-MED-Test Thought-This is a test thought --link-to abc123 --link-type inspired-by"
        input_data = AddItemInput.parse_input(cmd)
        self.assertEqual(input_data.goal, "TestGoal")
        self.assertEqual(input_data.type_, "th")
        self.assertEqual(input_data.title, "Test Thought")
        self.assertEqual(input_data.link_to, "abc123")
        self.assertEqual(input_data.link_type, "inspired-by")

if __name__ == '__main__':
    unittest.main() 