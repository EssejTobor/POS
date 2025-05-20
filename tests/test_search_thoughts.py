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


class TestSearchThoughts(unittest.TestCase):
    """Tests for searching thought items."""

    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system

        self.thought1 = self.work_system.add_item(
            goal="TestGoal",
            title="Brainstorm Idea",
            item_type=ItemType.THOUGHT,
            description="Initial brainstorming",
        )
        self.thought2 = self.work_system.add_item(
            goal="Another",
            title="Deep Thought",
            item_type=ItemType.THOUGHT,
            description="Something else",
        )
        self.task = self.work_system.add_item(
            goal="TestGoal",
            title="Task Item",
            item_type=ItemType.TASK,
            description="just a task",
        )

    def tearDown(self) -> None:
        self.temp_db.close()
        os.unlink(self.temp_db.name)

    def test_search_thoughts_command(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.cli.onecmd("search_thoughts Brainstorm")
        output = out.getvalue()
        self.assertIn("Brainstorm Idea", output)
        self.assertNotIn("Deep Thought", output)
        self.assertNotIn("Task Item", output)

    def test_search_thoughts_goal_filter(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.cli.onecmd("search_thoughts Thought Another")
        output = out.getvalue()
        self.assertIn("Deep Thought", output)
        self.assertNotIn("Brainstorm Idea", output)


if __name__ == "__main__":
    unittest.main()
