import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from .models import WorkItem, ItemType, ItemStatus, Priority

class Database:
    """SQLite database manager for the POS system"""
    
    def __init__(self, db_path: str = "work_items.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = Path(db_path)
        self._create_tables()
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
            
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS work_items (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entry_counts (
                    goal TEXT PRIMARY KEY,
                    count INTEGER NOT NULL
                )
            """)
            conn.commit()
            
    def add_item(self, item: WorkItem) -> None:
        """Add a new work item to the database"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO work_items (
                    id, title, goal, item_type, description,
                    priority, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.title,
                item.goal,
                item.item_type.value,
                item.description,
                item.priority.value,
                item.status.value,
                item.created_at.isoformat(),
                item.updated_at.isoformat()
            ))
            conn.commit()
            
    def get_item(self, item_id: str) -> Optional[WorkItem]:
        """Retrieve a work item by its ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM work_items WHERE id = ?",
                (item_id,)
            )
            row = cursor.fetchone()
            
        if row:
            return WorkItem.from_dict(dict(row))
        return None
        
    def update_item(self, item: WorkItem) -> None:
        """Update an existing work item"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE work_items SET
                    title = ?,
                    goal = ?,
                    item_type = ?,
                    description = ?,
                    priority = ?,
                    status = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                item.title,
                item.goal,
                item.item_type.value,
                item.description,
                item.priority.value,
                item.status.value,
                item.updated_at.isoformat(),
                item.id
            ))
            conn.commit()
            
    def get_items_by_goal(self, goal: str) -> List[WorkItem]:
        """Get all items for a specific goal"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM work_items WHERE LOWER(goal) = LOWER(?)",
                (goal,)
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]
            
    def get_incomplete_items(self) -> List[WorkItem]:
        """Get all incomplete items"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM work_items WHERE status != ?",
                (ItemStatus.COMPLETED.value,)
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]
            
    def get_items_by_type(self, item_type: ItemType) -> List[WorkItem]:
        """Get all items of a specific type"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM work_items WHERE item_type = ?",
                (item_type.value,)
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]
            
    def get_all_goals(self) -> List[str]:
        """Get a list of all unique goals"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT DISTINCT goal FROM work_items")
            return [row[0] for row in cursor.fetchall()]
            
    def get_all_items(self) -> Dict[str, WorkItem]:
        """Get all work items as a dictionary keyed by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM work_items")
            return {
                row['id']: WorkItem.from_dict(dict(row))
                for row in cursor.fetchall()
            }
            
    def update_entry_count(self, goal: str, count: int) -> None:
        """Update the entry count for a goal"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO entry_counts (goal, count)
                VALUES (?, ?)
            """, (goal, count))
            conn.commit()
            
    def get_entry_count(self, goal: str) -> int:
        """Get the entry count for a goal"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT count FROM entry_counts WHERE goal = ?",
                (goal,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0
            
    def get_all_entry_counts(self) -> Dict[str, int]:
        """Get all entry counts as a dictionary"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM entry_counts")
            return {row['goal']: row['count'] for row in cursor.fetchall()} 