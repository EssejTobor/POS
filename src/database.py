import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ItemStatus, ItemType, Priority, WorkItem


class Database:
    """SQLite database manager for the POS system"""

    def __init__(self, db_path: str = "work_items.db"):
        """Initialize database connection and create tables if they don't exist"""
        # Get the absolute path of the project root directory
        self.base_dir = Path(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.data_dir = self.base_dir / "data" / "db"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / db_path
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
        """Create necessary database tables and indexes"""
        with self.get_connection() as conn:
            # Create tables with appropriate indexes
            conn.executescript(
                """
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
                );

                -- Create indexes for common queries
                CREATE INDEX IF NOT EXISTS idx_work_items_goal 
                ON work_items(goal);
                
                CREATE INDEX IF NOT EXISTS idx_work_items_status 
                ON work_items(status);
                
                CREATE INDEX IF NOT EXISTS idx_work_items_priority 
                ON work_items(priority);
                
                CREATE INDEX IF NOT EXISTS idx_work_items_type 
                ON work_items(item_type);
                
                -- Composite index for common sorting patterns
                CREATE INDEX IF NOT EXISTS idx_work_items_goal_priority_created 
                ON work_items(goal, priority DESC, created_at DESC);
                
                CREATE TABLE IF NOT EXISTS entry_counts (
                    goal TEXT PRIMARY KEY,
                    count INTEGER NOT NULL
                );
                
                -- Create item_links table for relationships between items
                CREATE TABLE IF NOT EXISTS item_links (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    link_type TEXT NOT NULL DEFAULT 'references',
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (source_id, target_id),
                    FOREIGN KEY (source_id) REFERENCES work_items(id),
                    FOREIGN KEY (target_id) REFERENCES work_items(id)
                );
                
                -- Create indexes for item_links table
                CREATE INDEX IF NOT EXISTS idx_item_links_source 
                ON item_links(source_id);
                
                CREATE INDEX IF NOT EXISTS idx_item_links_target 
                ON item_links(target_id);
                
                CREATE INDEX IF NOT EXISTS idx_item_links_type
                ON item_links(link_type);

                -- Table for tagging items
                CREATE TABLE IF NOT EXISTS item_tags (
                    item_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    PRIMARY KEY (item_id, tag),
                    FOREIGN KEY (item_id) REFERENCES work_items(id)
                );

                CREATE INDEX IF NOT EXISTS idx_item_tags_tag
                ON item_tags(tag);
            """
            )

            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.commit()

    def add_item(self, item: WorkItem) -> None:
        """Add a new work item to the database"""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO work_items (
                    id, title, goal, item_type, description,
                    priority, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item.id,
                    item.title,
                    item.goal,
                    item.item_type.value,
                    item.description,
                    item.priority.value,
                    item.status.value,
                    item.created_at.isoformat(),
                    item.updated_at.isoformat(),
                ),
            )
            conn.commit()

    def get_item(self, item_id: str) -> Optional[WorkItem]:
        """Retrieve a work item by its ID"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM work_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()

        if row:
            return WorkItem.from_dict(dict(row))
        return None

    def update_item(self, item: WorkItem) -> None:
        """Update an existing work item"""
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE work_items SET
                    title = ?,
                    goal = ?,
                    item_type = ?,
                    description = ?,
                    priority = ?,
                    status = ?,
                    updated_at = ?
                WHERE id = ?
            """,
                (
                    item.title,
                    item.goal,
                    item.item_type.value,
                    item.description,
                    item.priority.value,
                    item.status.value,
                    item.updated_at.isoformat(),
                    item.id,
                ),
            )
            conn.commit()

    def get_items_by_goal(self, goal: str) -> List[WorkItem]:
        """Optimized query for getting items by goal"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM work_items 
                WHERE LOWER(goal) = LOWER(?) 
                ORDER BY priority DESC, created_at DESC
                """,
                (goal,),
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_items_by_goal_priority(self, goal: str) -> List[WorkItem]:
        """Optimized query for getting items by goal and priority"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM work_items 
                WHERE LOWER(goal) = LOWER(?) 
                ORDER BY priority DESC
                """,
                (goal,),
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_incomplete_items(self) -> List[WorkItem]:
        """Optimized query for getting incomplete items"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM work_items 
                WHERE status != ? 
                ORDER BY priority DESC, created_at DESC
                """,
                (ItemStatus.COMPLETED.value,),
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_items_by_filters(
        self,
        goal: Optional[str] = None,
        status: Optional[ItemStatus] = None,
        priority: Optional[Priority] = None,
        item_type: Optional[ItemType] = None,
        tag: Optional[str] = None,
        search_text: Optional[str] = None,
    ) -> List[WorkItem]:
        """Flexible query with multiple optional filters"""
        query = ["SELECT wi.* FROM work_items wi"]
        params: list[str | int] = []
        where_added = False

        if tag:
            query.append("JOIN item_tags it ON wi.id = it.item_id")

        def add_condition(clause: str) -> None:
            nonlocal where_added
            prefix = "WHERE" if not where_added else "AND"
            query.append(f"{prefix} {clause}")
            where_added = True

        if goal:
            add_condition("LOWER(wi.goal) = LOWER(?)")
            params.append(goal)
        if status:
            add_condition("status = ?")
            params.append(status.value)
        if priority:
            add_condition("priority = ?")
            params.append(priority.value)
        if item_type:
            add_condition("item_type = ?")
            params.append(item_type.value)
        if tag:
            add_condition("it.tag = ?")
            params.append(tag.lower())

        if search_text:
            add_condition("(LOWER(wi.title) LIKE ? OR LOWER(wi.description) LIKE ?)")
            term = f"%{search_text.lower()}%"
            params.extend([term, term])

        query.append("ORDER BY wi.priority DESC, wi.created_at DESC")

        with self.get_connection() as conn:
            cursor = conn.execute(" ".join(query), params)
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]

    def batch_insert_items(self, items: List[WorkItem]) -> None:
        """Batch insert multiple items efficiently"""
        with self.get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO work_items (
                    id, title, goal, item_type, description,
                    priority, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.id,
                        item.title,
                        item.goal,
                        item.item_type.value,
                        item.description,
                        item.priority.value,
                        item.status.value,
                        item.created_at.isoformat(),
                        item.updated_at.isoformat(),
                    )
                    for item in items
                ],
            )
            conn.commit()

    def execute_vacuum(self) -> None:
        """Optimize database by removing unused space"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")

    def get_items_by_type(self, item_type: ItemType) -> List[WorkItem]:
        """Get all items of a specific type"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM work_items WHERE item_type = ?", (item_type.value,)
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
                row["id"]: WorkItem.from_dict(dict(row)) for row in cursor.fetchall()
            }

    def update_entry_count(self, goal: str, count: int) -> None:
        """Update the entry count for a goal"""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO entry_counts (goal, count)
                VALUES (?, ?)
            """,
                (goal, count),
            )
            conn.commit()

    def get_entry_count(self, goal: str) -> int:
        """Get the entry count for a goal"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT count FROM entry_counts WHERE goal = ?", (goal,)
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    def get_all_entry_counts(self) -> Dict[str, int]:
        """Get all entry counts as a dictionary"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM entry_counts")
            return {row["goal"]: row["count"] for row in cursor.fetchall()}

    # ------------------------------------------------------------------
    # Tag management methods
    # ------------------------------------------------------------------

    def add_tag(self, item_id: str, tag: str) -> bool:
        """Add a tag to an item."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO item_tags (item_id, tag) VALUES (?, ?)",
                    (item_id, tag.lower()),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_tag(self, item_id: str, tag: str) -> bool:
        """Remove a tag from an item."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM item_tags WHERE item_id = ? AND tag = ?",
                (item_id, tag.lower()),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_tags(self, item_id: str) -> List[str]:
        """Get all tags for a given item."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT tag FROM item_tags WHERE item_id = ?",
                (item_id,),
            )
            return [row["tag"] for row in cursor.fetchall()]

    def get_items_by_tag(self, tag: str) -> List[WorkItem]:
        """Get all items that have a given tag."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT wi.* FROM work_items wi
                JOIN item_tags it ON wi.id = it.item_id
                WHERE it.tag = ?
                ORDER BY wi.priority DESC, wi.created_at DESC
                """,
                (tag.lower(),),
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_all_tags(self) -> List[str]:
        """Return a list of all distinct tags."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT DISTINCT tag FROM item_tags")
            return [row[0] for row in cursor.fetchall()]

    def add_link(
        self, source_id: str, target_id: str, link_type: str = "references"
    ) -> bool:
        """
        Add a link between two work items

        Args:
            source_id: ID of the source item
            target_id: ID of the target item
            link_type: Type of relationship (default: "references")

        Returns:
            bool: True if the link was added successfully, False otherwise
        """
        try:
            # Check if both items exist
            if not self.get_item(source_id) or not self.get_item(target_id):
                return False

            # Insert the link
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO item_links (
                        source_id, target_id, link_type, created_at
                    ) VALUES (?, ?, ?, ?)
                """,
                    (source_id, target_id, link_type, datetime.now().isoformat()),
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding link: {e}")
            return False

    def remove_link(self, source_id: str, target_id: str) -> bool:
        """
        Remove a link between two work items

        Args:
            source_id: ID of the source item
            target_id: ID of the target item

        Returns:
            bool: True if the link was removed successfully, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM item_links
                    WHERE source_id = ? AND target_id = ?
                """,
                    (source_id, target_id),
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing link: {e}")
            return False

    def get_links(self, item_id: str) -> Dict[str, List[Dict]]:
        """
        Get all links for an item (both incoming and outgoing)

        Args:
            item_id: ID of the item to get links for

        Returns:
            Dictionary with 'outgoing' and 'incoming' lists of links
        """
        result: Dict[str, List[Dict[str, Any]]] = {"outgoing": [], "incoming": []}

        try:
            with self.get_connection() as conn:
                # Get outgoing links (item_id is the source)
                outgoing_cursor = conn.execute(
                    """
                    SELECT il.source_id, il.target_id, il.link_type, il.created_at,
                           wi.title, wi.goal, wi.item_type
                    FROM item_links il
                    JOIN work_items wi ON il.target_id = wi.id
                    WHERE il.source_id = ?
                """,
                    (item_id,),
                )

                for row in outgoing_cursor.fetchall():
                    result["outgoing"].append(
                        {
                            "source_id": row["source_id"],
                            "target_id": row["target_id"],
                            "link_type": row["link_type"],
                            "created_at": row["created_at"],
                            "title": row["title"],
                            "goal": row["goal"],
                            "item_type": row["item_type"],
                        }
                    )

                # Get incoming links (item_id is the target)
                incoming_cursor = conn.execute(
                    """
                    SELECT il.source_id, il.target_id, il.link_type, il.created_at,
                           wi.title, wi.goal, wi.item_type
                    FROM item_links il
                    JOIN work_items wi ON il.source_id = wi.id
                    WHERE il.target_id = ?
                """,
                    (item_id,),
                )

                for row in incoming_cursor.fetchall():
                    result["incoming"].append(
                        {
                            "source_id": row["source_id"],
                            "target_id": row["target_id"],
                            "link_type": row["link_type"],
                            "created_at": row["created_at"],
                            "title": row["title"],
                            "goal": row["goal"],
                            "item_type": row["item_type"],
                        }
                    )

            return result
        except sqlite3.Error as e:
            print(f"Error getting links: {e}")
            return result
