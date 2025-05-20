import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.cli import WorkSystemCLI
from src.storage import WorkSystem


class TestCleanupBackups(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system
        # Use a temporary directory for backups
        self.temp_backup_dir = tempfile.TemporaryDirectory()
        self.work_system.backup_manager.backup_dir = Path(self.temp_backup_dir.name)
        self.cli.backup_manager = self.work_system.backup_manager
        # Create three backups with unique names
        for i in range(3):
            self.cli.backup_manager.create_backup(note=f"n{i}")

    def tearDown(self) -> None:
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        self.temp_backup_dir.cleanup()

    def test_cleanup_backups_reports_count(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.cli.onecmd("cleanup_backups 1")
        output = out.getvalue()
        self.assertIn("Removed 2 old backup(s)", output)
        self.assertEqual(len(self.cli.backup_manager.list_backups()), 1)


if __name__ == "__main__":
    unittest.main()
