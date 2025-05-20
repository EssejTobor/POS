import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cli import WorkSystemCLI
from src.storage import WorkSystem


class TestRestoreCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.work_system = WorkSystem(self.temp_db.name)
        self.cli = WorkSystemCLI()
        self.cli.work_system = self.work_system

    def tearDown(self) -> None:
        self.temp_db.close()
        os.unlink(self.temp_db.name)
        # Cleanup any backups created during the test
        for f in self.work_system.backup_manager.backup_dir.glob("*.db"):
            f.unlink(missing_ok=True)

    def test_restore_from_backup_dir(self) -> None:
        # create a backup using the work system
        backup_path = self.work_system.backup_manager.create_backup("restore")

        # remove the database to force restore
        os.unlink(self.temp_db.name)

        out = io.StringIO()
        with redirect_stdout(out):
            self.cli.onecmd(f"restore {backup_path.name}")

        self.assertIn("Database restored successfully", out.getvalue())
        # ensure database file was restored
        self.assertTrue(os.path.exists(self.temp_db.name))
        # cleanup
        backup_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
