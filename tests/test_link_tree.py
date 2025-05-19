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

class TestLinkTree(unittest.TestCase):
    """Tests for the link_tree command and visualization"""
    
    def setUp(self):
        """Set up a temporary database and CLI with test data"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system
        
        # Create test items with various relationships
        
        # Create a thought
        self.thought1 = self.work_system.add_item(
            goal="TestGoal",
            title="Initial Thought",
            item_type=ItemType.THOUGHT,
            description="This is the first thought"
        )
        
        # Create a task
        self.task1 = self.work_system.add_item(
            goal="TestGoal",
            title="Related Task",
            item_type=ItemType.TASK,
            description="This task is related to the thought"
        )
        
        # Create a second thought that evolves from the first
        self.thought2 = self.work_system.add_item(
            goal="TestGoal",
            title="Evolved Thought",
            item_type=ItemType.THOUGHT,
            description="This thought evolves from the first thought"
        )
        
        # Create a third thought inspired by the first
        self.thought3 = self.work_system.add_item(
            goal="TestGoal",
            title="Inspired Thought",
            item_type=ItemType.THOUGHT,
            description="This thought was inspired by the first thought"
        )
        
        # Create links between items with different link types
        self.work_system.add_link(self.thought1.id, self.task1.id, "references")
        self.work_system.add_link(self.thought2.id, self.thought1.id, "evolves-from")
        self.work_system.add_link(self.thought3.id, self.thought1.id, "inspired-by")
        
        # Create a cycle for testing cycle detection
        self.work_system.add_link(self.thought1.id, self.thought3.id, "references")
        
    def tearDown(self):
        """Clean up after each test"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        
    def test_link_tree_basic(self):
        """Test the basic link_tree command without arguments"""
        # Capture output
        captured_output = io.StringIO()
        
        # Run the command
        with redirect_stdout(captured_output):
            self.cli.onecmd("link_tree")
        
        # Check output contains expected elements
        output = captured_output.getvalue()
        
        # Should display a success message with item count
        self.assertIn("Displaying relationships for", output)
        
        # Should contain all our test items
        self.assertIn("Initial Thought", output)
        self.assertIn("Related Task", output)
        self.assertIn("Evolved Thought", output)
        self.assertIn("Inspired Thought", output)
        
        # Should contain link types with colored formatting
        self.assertIn("references", output)
        self.assertIn("evolves-from", output)
        self.assertIn("inspired-by", output)
        
    def test_link_tree_with_root(self):
        """Test the link_tree command with a specific root item"""
        # Capture output
        captured_output = io.StringIO()
        
        # Run the command with a specific root
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link_tree {self.thought1.id}")
        
        # Check output contains expected elements
        output = captured_output.getvalue()
        
        # Should display a success message with the root item
        self.assertIn(f"Displaying relationship tree for: {self.thought1.title}", output)
        
        # Should contain the root item and linked items
        self.assertIn("Initial Thought", output)
        self.assertIn("Related Task", output)
        self.assertIn("Inspired Thought", output)
        
        # Should contain appropriate link types
        self.assertIn("references", output)
        
    def test_link_tree_thoughts_only(self):
        """Test the link_tree command filtered to thoughts only"""
        # Capture output
        captured_output = io.StringIO()
        
        # Run the command with thoughts filter
        with redirect_stdout(captured_output):
            self.cli.onecmd("link_tree --thoughts")
        
        # Check output contains expected elements
        output = captured_output.getvalue()
        
        # Should display a success message with thought count
        self.assertIn("Displaying relationships for", output)
        self.assertIn("thought items", output)
        
        # Should contain all thought items
        self.assertIn("Initial Thought", output)
        self.assertIn("Evolved Thought", output)
        self.assertIn("Inspired Thought", output)
        
        # The task should be visible as a linked item but not as a root
        # This is tricky to test in the text output, but we can check for the task ID
        self.assertIn(self.task1.id, output)
        
    def test_link_tree_with_depth(self):
        """Test the link_tree command with a specified maximum depth"""
        # Capture output
        captured_output = io.StringIO()
        
        # Run the command with a specific root and limited depth
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link_tree {self.thought1.id} 1")  # Depth of 1
        
        # Check output contains expected elements
        output = captured_output.getvalue()
        
        # Should display a success message with the root item
        self.assertIn(f"Displaying relationship tree for: {self.thought1.title}", output)
        
        # Should contain the root item and direct children
        self.assertIn("Initial Thought", output)
        self.assertIn("Related Task", output)
        self.assertIn("Inspired Thought", output)
        
        # Create a more complex tree with multiple levels
        thought4 = self.work_system.add_item(
            goal="TestGoal",
            title="Deep Thought",
            item_type=ItemType.THOUGHT,
            description="This thought is deeper in the tree"
        )
        
        self.work_system.add_link(self.thought3.id, thought4.id, "parent-child")
        
        # Test with normal depth (should include the deep thought)
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link_tree {self.thought1.id}")
            
        output = captured_output.getvalue()
        self.assertIn("Deep Thought", output)
        
        # Test with depth of 1 (should not include the deep thought)
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link_tree {self.thought1.id} 1")
            
        output = captured_output.getvalue()
        self.assertNotIn("Deep Thought", output)


    def test_missing_item_cleanup(self):
        """Ensure missing items are removed from the visited set"""
        # Create an additional thought that will be removed
        missing_thought = self.work_system.add_item(
            goal="TestGoal",
            title="Temporary Thought",
            item_type=ItemType.THOUGHT,
            description="Will be removed",
        )

        # Link two existing items to the thought
        self.work_system.add_link(self.thought1.id, missing_thought.id, "references")
        self.work_system.add_link(self.thought2.id, missing_thought.id, "references")

        # Remove the thought from the in-memory cache to simulate a missing item
        del self.work_system.items[missing_thought.id]

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.onecmd("link_tree")

        output = captured_output.getvalue()

        # The missing item should be reported for each reference and never marked as a cycle
        self.assertGreaterEqual(output.count(f"Item not found: {missing_thought.id}"), 2)
        self.assertNotIn(f"{missing_thought.id}[/dim cyan] [dim](cycle reference)", output)

    def test_link_tree_cycle_detection(self):
        """Cycle references should be indicated in the output"""
        captured_output = io.StringIO()

        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link_tree {self.thought1.id}")

        output = captured_output.getvalue()
        self.assertIn("(cycle reference)", output)

        
    def test_invalid_arguments(self):
        """Test error handling with invalid arguments"""
        # Test with non-existent item ID
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.onecmd("link_tree nonexistent-id")
            
        output = captured_output.getvalue()
        self.assertIn("Item not found", output)
        
        # Test with invalid depth
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link_tree {self.thought1.id} abc")
            
        output = captured_output.getvalue()
        self.assertIn("Invalid maximum depth", output)
        
        # Test with negative depth
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link_tree {self.thought1.id} -1")
            
        output = captured_output.getvalue()
        self.assertIn("Maximum depth must be greater than 0", output)
        
        # Test with unknown option
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.onecmd("link_tree --unknown-option")
            
        output = captured_output.getvalue()
        self.assertIn("Unknown option", output)

if __name__ == '__main__':
    unittest.main() 