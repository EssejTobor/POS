import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class BackupManager:
    def __init__(self, db_path: str = "work_items.db"):
        # Get the absolute path of the project root directory
        self.base_dir = Path(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.data_dir = self.base_dir / "data"
        self.db_path = self.data_dir / "db" / db_path
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, note: Optional[str] = None) -> Path:
        """Create a timestamped backup of the database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        note_suffix = f"_{note}" if note else ""
        backup_path = self.backup_dir / f"work_items_{timestamp}{note_suffix}.db"

        # Ensure database is in a consistent state
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA wal_checkpoint(FULL)")

        # Create backup
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    def restore_backup(self, backup_path: Path) -> None:
        """Restore database from a backup"""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Create backup of current database before restore
        self.create_backup(note="pre_restore")

        # Restore database
        shutil.copy2(backup_path, self.db_path)

    def list_backups(self) -> List[Path]:
        """List all available backups"""
        return sorted(
            [f for f in self.backup_dir.glob("work_items_*.db")],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

    def cleanup_old_backups(self, keep_last: int = 5) -> int:
        """Remove old backups, keeping the specified number and return count."""
        backups = self.list_backups()
        removed = 0
        for backup in backups[keep_last:]:
            backup.unlink()
            removed += 1
        return removed

    def export_to_json(self, output_path: Optional[Path] = None) -> Path:
        """Export database content to JSON for external backup"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.backup_dir / f"work_items_{timestamp}.json"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Export work items
            cursor = conn.execute("SELECT * FROM work_items")
            items = [dict(row) for row in cursor.fetchall()]

            # Export entry counts
            cursor = conn.execute("SELECT * FROM entry_counts")
            counts = {row["goal"]: row["count"] for row in cursor.fetchall()}

            data = {
                "items": items,
                "entry_counts": counts,
                "export_date": datetime.now().isoformat(),
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

        return output_path
