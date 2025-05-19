import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cli import WorkSystemCLI
from src.models import ItemType
from src.storage import WorkSystem


class TestLinkCommands(unittest.TestCase):
    """Tests for the link and unlink commands"""

    def setUp(self):
        """Set up a temporary database and CLI for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system

        # Add two test items to link
        self.thought = self.work_system.add_item(
            goal="TestGoal",
            title="Test Thought",
            item_type=ItemType.THOUGHT,
            description="This is a test thought",
        )

        self.task = self.work_system.add_item(
            goal="TestGoal",
            title="Test Task",
            item_type=ItemType.TASK,
            description="This is a test task",
        )

    def tearDown(self):
        """Clean up after each test"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)

    def test_link_command(self):
        """Test the link command functionality"""
        # Capture output
        captured_output = io.StringIO()

        # Create a link between thought and task
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link {self.thought.id} {self.task.id}")

        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Link created successfully", output)

        # Verify link exists in the database
        links = self.work_system.get_links(self.thought.id)
        self.assertEqual(len(links["outgoing"]), 1)
        self.assertEqual(links["outgoing"][0]["target_id"], self.task.id)
        self.assertEqual(
            links["outgoing"][0]["link_type"], "references"
        )  # Default type

    def test_link_command_with_type(self):
        """Test the link command with a specific link type"""
        captured_output = io.StringIO()

        # Create a link with a custom type
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link {self.thought.id} {self.task.id} evolves-from")

        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Link created successfully", output)
        self.assertIn("evolves-from", output)

        # Verify link exists with correct type
        links = self.work_system.get_links(self.thought.id)
        self.assertEqual(len(links["outgoing"]), 1)
        self.assertEqual(links["outgoing"][0]["target_id"], self.task.id)
        self.assertEqual(links["outgoing"][0]["link_type"], "evolves-from")

    def test_link_command_invalid_id(self):
        """Test the link command with invalid IDs"""
        captured_output = io.StringIO()

        # Try to link with invalid source ID
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link invalid-id {self.task.id}")

        # Verify error message
        output = captured_output.getvalue()
        self.assertIn("Source item not found", output)

        # Reset output
        captured_output = io.StringIO()

        # Try to link with invalid target ID
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link {self.thought.id} invalid-id")

        # Verify error message
        output = captured_output.getvalue()
        self.assertIn("Target item not found", output)

    def test_link_command_invalid_type(self):
        """Test the link command with an invalid link type"""
        captured_output = io.StringIO()

        # Try to create link with invalid type
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"link {self.thought.id} {self.task.id} invalid-type")

        # Verify error message
        output = captured_output.getvalue()
        self.assertIn("Invalid link type", output)

    def test_unlink_command(self):
        """Test the unlink command functionality"""
        # First create a link
        self.work_system.add_link(self.thought.id, self.task.id)

        # Verify link exists
        links = self.work_system.get_links(self.thought.id)
        self.assertEqual(len(links["outgoing"]), 1)

        # Capture output
        captured_output = io.StringIO()

        # Remove the link
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"unlink {self.thought.id} {self.task.id}")

        # Verify output
        output = captured_output.getvalue()
        self.assertIn("Link removed successfully", output)

        # Verify link has been removed
        links = self.work_system.get_links(self.thought.id)
        self.assertEqual(len(links["outgoing"]), 0)

    def test_unlink_command_no_link(self):
        """Test the unlink command when no link exists"""
        # Verify no link exists
        links = self.work_system.get_links(self.thought.id)
        self.assertEqual(len(links["outgoing"]), 0)

        # Capture output
        captured_output = io.StringIO()

        # Try to remove a non-existent link
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"unlink {self.thought.id} {self.task.id}")

        # Verify error message
        output = captured_output.getvalue()
        self.assertIn("No link found", output)

    def test_unlink_command_invalid_ids(self):
        """Test the unlink command with invalid IDs"""
        captured_output = io.StringIO()

        # Try to unlink with invalid source ID
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"unlink invalid-id {self.task.id}")

        # Verify error message
        output = captured_output.getvalue()
        self.assertIn("Source item not found", output)

        # Reset output
        captured_output = io.StringIO()

        # Try to unlink with invalid target ID
        with redirect_stdout(captured_output):
            self.cli.onecmd(f"unlink {self.thought.id} invalid-id")

        # Verify error message
        output = captured_output.getvalue()
        self.assertIn("Target item not found", output)


if __name__ == "__main__":
    unittest.main()
