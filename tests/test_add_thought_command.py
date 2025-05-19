import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cli import WorkSystemCLI
from src.models import ItemType
from src.schemas import AddThoughtInput
from src.storage import WorkSystem


class TestAddThoughtCommand(unittest.TestCase):
    """Tests for the add_thought command and schema"""

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

    def test_add_thought_input_parser(self):
        """Test parsing input for add_thought command"""
        # Basic input
        input_str = "TestGoal-Test Title-Test description"
        parsed = AddThoughtInput.parse_input(input_str)
        self.assertEqual(parsed.goal, "TestGoal")
        self.assertEqual(parsed.title, "Test Title")
        self.assertEqual(parsed.description, "Test description")
        self.assertIsNone(parsed.parent_id)
        self.assertEqual(parsed.link_type, "evolves-from")

        # Input with parent
        input_str = "TestGoal-Test Title-Test description --parent abc123"
        parsed = AddThoughtInput.parse_input(input_str)
        self.assertEqual(parsed.goal, "TestGoal")
        self.assertEqual(parsed.title, "Test Title")
        self.assertEqual(parsed.description, "Test description")
        self.assertEqual(parsed.parent_id, "abc123")
        self.assertEqual(parsed.link_type, "evolves-from")

        # Input with parent and link type
        input_str = (
            "TestGoal-Test Title-Test description --parent abc123 --link inspired-by"
        )
        parsed = AddThoughtInput.parse_input(input_str)
        self.assertEqual(parsed.goal, "TestGoal")
        self.assertEqual(parsed.title, "Test Title")
        self.assertEqual(parsed.description, "Test description")
        self.assertEqual(parsed.parent_id, "abc123")
        self.assertEqual(parsed.link_type, "inspired-by")

        # Invalid input (too few parts)
        with self.assertRaises(ValueError):
            AddThoughtInput.parse_input("TestGoal-Test Title")

        # Invalid link type
        with self.assertRaises(ValueError):
            AddThoughtInput.parse_input(
                "TestGoal-Test Title-Test description --parent abc123 --link invalid-type"
            )

    def test_add_thought_command(self):
        """Test the add_thought command functionality"""
        # Capture output
        captured_output = io.StringIO()

        # Add a thought
        with redirect_stdout(captured_output):
            self.cli.onecmd("add_thought TestGoal-Test Thought-This is a test thought")

        # Check that a thought was added
        thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        self.assertEqual(len(thoughts), 1)
        self.assertEqual(thoughts[0].title, "Test Thought")
        self.assertEqual(thoughts[0].goal, "TestGoal")
        self.assertEqual(thoughts[0].description, "This is a test thought")
        self.assertEqual(thoughts[0].item_type, ItemType.THOUGHT)

        # Test adding a thought with parent
        # First, get the ID of the first thought to use as parent
        parent_id = thoughts[0].id

        with redirect_stdout(captured_output):
            self.cli.onecmd(
                f"add_thought TestGoal-Child Thought-This references the parent --parent {parent_id}"
            )

        # Check that a second thought was added
        thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        self.assertEqual(len(thoughts), 2)

        # Get the child thought (the one that's not the parent)
        child_thought = next(t for t in thoughts if t.id != parent_id)
        self.assertEqual(child_thought.title, "Child Thought")

        # Check that a link was created
        links = self.work_system.get_links(child_thought.id)
        self.assertEqual(len(links["outgoing"]), 1)  # Should have one outgoing link
        self.assertEqual(links["outgoing"][0]["target_id"], parent_id)
        self.assertEqual(links["outgoing"][0]["link_type"], "evolves-from")

        # Test with custom link type
        with redirect_stdout(captured_output):
            self.cli.onecmd(
                f"add_thought TestGoal-Inspired Thought-This was inspired by the original --parent {parent_id} --link inspired-by"
            )

        # Check that a third thought was added
        thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
        self.assertEqual(len(thoughts), 3)

        # Get the inspired thought (the newest one)
        inspired_thought = max(thoughts, key=lambda t: t.created_at)

        # Check that a link with custom type was created
        links = self.work_system.get_links(inspired_thought.id)
        self.assertEqual(len(links["outgoing"]), 1)
        self.assertEqual(links["outgoing"][0]["target_id"], parent_id)
        self.assertEqual(links["outgoing"][0]["link_type"], "inspired-by")


if __name__ == "__main__":
    unittest.main()
