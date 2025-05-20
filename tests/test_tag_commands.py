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


class TestTagCommands(unittest.TestCase):
    """CLI tests for tag and untag commands."""

    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system

        self.item = self.work_system.add_item(
            goal="TestGoal",
            title="Item",
            item_type=ItemType.TASK,
            description="desc",
        )

    def tearDown(self) -> None:
        self.temp_db.close()
        os.unlink(self.temp_db.name)

    def test_tag_and_untag(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.cli.onecmd(f"tag {self.item.id} demo")
        self.assertIn("added", out.getvalue())
        self.assertIn("demo", self.work_system.get_tags_for_item(self.item.id))

        out = io.StringIO()
        with redirect_stdout(out):
            self.cli.onecmd(f"untag {self.item.id} demo")
        self.assertIn("removed", out.getvalue())
        self.assertEqual(self.work_system.get_tags_for_item(self.item.id), [])

    def test_list_by_tag(self) -> None:
        self.work_system.add_tag_to_item(self.item.id, "alpha")
        out = io.StringIO()
        with redirect_stdout(out):
            self.cli.onecmd("list_by_tag alpha")
        self.assertIn(self.item.title, out.getvalue())


if __name__ == "__main__":
    unittest.main()
