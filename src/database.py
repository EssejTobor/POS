import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import os
import threading
import logging

from .models import WorkItem, ItemType, ItemStatus, Priority, ThoughtNode, ThoughtStatus, BranchType
from .config import Config

logger = logging.getLogger(__name__)

class Database:
    """SQLite database manager for the POS system"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection and create tables if they don't exist"""
        # Use the config path or the provided path
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Config.get_db_path()
        
        self._create_tables()
        # Thread lock for database operations
        self.lock = threading.Lock()
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
            
    def _create_tables(self):
        """Create necessary database tables and indexes"""
        with self.get_connection() as conn:
            # Create tables with appropriate indexes
            conn.executescript("""
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
                
                CREATE INDEX IF NOT EXISTS idx_work_items_type
                ON work_items(item_type);
                
                CREATE INDEX IF NOT EXISTS idx_work_items_priority
                ON work_items(priority);
                
                CREATE TABLE IF NOT EXISTS goal_entry_count (
                    goal TEXT PRIMARY KEY,
                    count INTEGER NOT NULL
                );
            """)
            
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
        """Optimized query for getting items by goal"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM work_items 
                WHERE LOWER(goal) = LOWER(?) 
                ORDER BY priority DESC, created_at DESC
                """,
                (goal,)
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
                (goal,)
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
                (ItemStatus.COMPLETED.value,)
            )
            return [WorkItem.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_items_by_filters(self, 
                           goal: Optional[str] = None,
                           status: Optional[ItemStatus] = None,
                           priority: Optional[Priority] = None,
                           item_type: Optional[ItemType] = None) -> List[WorkItem]:
        """Flexible query with multiple optional filters"""
        query = ["SELECT * FROM work_items WHERE 1=1"]
        params = []

        if goal:
            query.append("AND LOWER(goal) = LOWER(?)")
            params.append(goal)
        if status:
            query.append("AND status = ?")
            params.append(status.value)
        if priority:
            query.append("AND priority = ?")
            params.append(priority.value)
        if item_type:
            query.append("AND item_type = ?")
            params.append(item_type.value)

        query.append("ORDER BY priority DESC, created_at DESC")
        
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
                [(
                    item.id,
                    item.title,
                    item.goal,
                    item.item_type.value,
                    item.description,
                    item.priority.value,
                    item.status.value,
                    item.created_at.isoformat(),
                    item.updated_at.isoformat()
                ) for item in items]
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

    # New thought related methods
    def add_thought(self, thought: ThoughtNode) -> bool:
        """Add a new thought to the database"""
        with self.lock:
            try:
                with self.get_connection() as conn:
                    # Check if the thought table exists
                    self._ensure_thought_tables(conn)
                    
                    # Convert to dict for storage
                    data = thought.to_dict()
                    
                    # Insert thought
                    conn.execute("""
                        INSERT INTO thought_nodes (
                            id, title, content, branch_name, is_external, 
                            parent_id, status, tags, branch_type, 
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data['id'], data['title'], data['content'], data['branch_name'],
                        data['is_external'], data['parent_id'], data['status'], 
                        data['tags'], data['branch_type'], data['created_at'], 
                        data['updated_at']
                    ))
                    return True
            except Exception as e:
                logger.error(f"Error adding thought: {e}", exc_info=True)
                return False
    
    def _ensure_thought_tables(self, conn: sqlite3.Connection) -> None:
        """Ensure thought tables exist (helper for transition period)"""
        conn.executescript("""
            -- Thought nodes table
            CREATE TABLE IF NOT EXISTS thought_nodes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                branch_name TEXT NOT NULL,
                is_external INTEGER NOT NULL DEFAULT 0,
                parent_id TEXT,
                status TEXT NOT NULL,
                tags TEXT,
                branch_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            
            -- Thought relationships
            CREATE TABLE IF NOT EXISTS thought_relationships (
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (parent_id, child_id),
                FOREIGN KEY (parent_id) REFERENCES thought_nodes(id),
                FOREIGN KEY (child_id) REFERENCES thought_nodes(id)
            );
            
            -- Work item to thought connections
            CREATE TABLE IF NOT EXISTS thought_references (
                thought_id TEXT NOT NULL,
                work_item_id TEXT NOT NULL,
                PRIMARY KEY (thought_id, work_item_id),
                FOREIGN KEY (thought_id) REFERENCES thought_nodes(id),
                FOREIGN KEY (work_item_id) REFERENCES work_items(id)
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_thought_nodes_branch 
            ON thought_nodes(branch_name);
            
            CREATE INDEX IF NOT EXISTS idx_thought_nodes_status 
            ON thought_nodes(status);
            
            CREATE INDEX IF NOT EXISTS idx_thought_nodes_parent
            ON thought_nodes(parent_id);
            
            CREATE INDEX IF NOT EXISTS idx_thought_relationships_parent 
            ON thought_relationships(parent_id);
            
            CREATE INDEX IF NOT EXISTS idx_thought_relationships_child 
            ON thought_relationships(child_id);
        """)
    
    def update_thought(self, thought: ThoughtNode) -> bool:
        """Update an existing thought"""
        with self.lock:
            try:
                with self.get_connection() as conn:
                    # Convert to dict for storage
                    data = thought.to_dict()
                    
                    # Update thought
                    cursor = conn.execute("""
                        UPDATE thought_nodes
                        SET title = ?, content = ?, branch_name = ?, 
                            is_external = ?, parent_id = ?, status = ?,
                            tags = ?, branch_type = ?, updated_at = ?
                        WHERE id = ?
                    """, (
                        data['title'], data['content'], data['branch_name'],
                        data['is_external'], data['parent_id'], data['status'],
                        data['tags'], data['branch_type'], data['updated_at'],
                        data['id']
                    ))
                    return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"Error updating thought: {e}", exc_info=True)
                return False
    
    def get_thought(self, thought_id: str) -> Optional[ThoughtNode]:
        """Get a thought by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM thought_nodes WHERE id = ?
                """, (thought_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Convert row to dict
                thought_dict = dict(row)
                return ThoughtNode.from_dict(thought_dict)
        except Exception as e:
            logger.error(f"Error getting thought {thought_id}: {e}")
            return None
    
    def add_thought_relationship(self, parent_id: str, child_id: str, 
                                relationship_type: str) -> bool:
        """Add a relationship between two thoughts"""
        with self.lock:
            try:
                with self.get_connection() as conn:
                    # Add relationship
                    conn.execute("""
                        INSERT INTO thought_relationships
                        (parent_id, child_id, relationship_type, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (
                        parent_id, child_id, relationship_type, 
                        datetime.now().isoformat()
                    ))
                    return True
            except Exception as e:
                logger.error(f"Error adding thought relationship: {e}")
                return False
    
    def get_thought_children(self, thought_id: str) -> List[ThoughtNode]:
        """Get all child thoughts of a given thought"""
        try:
            with self.get_connection() as conn:
                # Get child IDs from relationships
                child_ids = conn.execute("""
                    SELECT child_id FROM thought_relationships 
                    WHERE parent_id = ?
                """, (thought_id,)).fetchall()
                
                if not child_ids:
                    return []
                
                # Get actual thought objects
                children = []
                for row in child_ids:
                    child = self.get_thought(row['child_id'])
                    if child:
                        children.append(child)
                
                return children
        except Exception as e:
            logger.error(f"Error getting thought children for {thought_id}: {e}")
            return []
    
    def get_thought_parents(self, thought_id: str) -> List[ThoughtNode]:
        """Get all parent thoughts of a given thought"""
        try:
            with self.get_connection() as conn:
                # Get parent IDs from relationships
                parent_ids = conn.execute("""
                    SELECT parent_id FROM thought_relationships 
                    WHERE child_id = ?
                """, (thought_id,)).fetchall()
                
                if not parent_ids:
                    return []
                
                # Get actual thought objects
                parents = []
                for row in parent_ids:
                    parent = self.get_thought(row['parent_id'])
                    if parent:
                        parents.append(parent)
                
                return parents
        except Exception as e:
            logger.error(f"Error getting thought parents for {thought_id}: {e}")
            return []
    
    def get_thoughts_by_branch(self, branch_name: str) -> List[ThoughtNode]:
        """Get all thoughts in a specific branch"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT * FROM thought_nodes 
                    WHERE LOWER(branch_name) = LOWER(?)
                    ORDER BY created_at ASC
                """, (branch_name,)).fetchall()
                
                return [ThoughtNode.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting thoughts by branch {branch_name}: {e}")
            return []
    
    def get_thoughts_by_status(self, status: ThoughtStatus) -> List[ThoughtNode]:
        """Get all thoughts with a specific status"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT * FROM thought_nodes 
                    WHERE status = ?
                    ORDER BY updated_at DESC
                """, (status.value,)).fetchall()
                
                return [ThoughtNode.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting thoughts by status {status}: {e}")
            return []
    
    def get_all_thought_branches(self) -> List[str]:
        """Get all unique branch names"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT DISTINCT branch_name FROM thought_nodes
                    ORDER BY branch_name
                """).fetchall()
                
                return [row['branch_name'] for row in rows]
        except Exception as e:
            logger.error(f"Error getting all thought branches: {e}")
            return []
    
    def get_branch_root_thoughts(self, branch_name: str) -> List[ThoughtNode]:
        """Get root level thoughts in a branch (those without parents)"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT * FROM thought_nodes 
                    WHERE LOWER(branch_name) = LOWER(?)
                    AND parent_id IS NULL
                    ORDER BY created_at ASC
                """, (branch_name,)).fetchall()
                
                return [ThoughtNode.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting root thoughts for branch {branch_name}: {e}")
            return []
    
    def search_thoughts(self, query: str) -> List[ThoughtNode]:
        """Search thoughts using FTS (if available) or fallback to LIKE"""
        try:
            with self.get_connection() as conn:
                # Check if FTS table exists
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='thought_nodes_fts'
                """)
                
                if cursor.fetchone():
                    # Use FTS table
                    rows = conn.execute("""
                        SELECT * FROM thought_nodes
                        WHERE id IN (
                            SELECT id FROM thought_nodes_fts
                            WHERE thought_nodes_fts MATCH ?
                        )
                        ORDER BY updated_at DESC
                    """, (query,)).fetchall()
                else:
                    # Fallback to LIKE search
                    search_term = f"%{query}%"
                    rows = conn.execute("""
                        SELECT * FROM thought_nodes
                        WHERE title LIKE ? OR content LIKE ?
                        ORDER BY updated_at DESC
                    """, (search_term, search_term)).fetchall()
                
                return [ThoughtNode.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error searching thoughts with query '{query}': {e}")
            return []
    
    def link_thought_to_work_item(self, thought_id: str, work_item_id: str) -> bool:
        """Create a link between a thought and a work item"""
        with self.lock:
            try:
                with self.get_connection() as conn:
                    conn.execute("""
                        INSERT OR IGNORE INTO thought_references
                        (thought_id, work_item_id)
                        VALUES (?, ?)
                    """, (thought_id, work_item_id))
                    return True
            except Exception as e:
                logger.error(f"Error linking thought {thought_id} to work item {work_item_id}: {e}")
                return False
    
    def get_linked_work_items(self, thought_id: str) -> List[WorkItem]:
        """Get all work items linked to a thought"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT w.* FROM work_items w
                    JOIN thought_references tr ON w.id = tr.work_item_id
                    WHERE tr.thought_id = ?
                """, (thought_id,)).fetchall()
                
                return [WorkItem.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting linked work items for thought {thought_id}: {e}")
            return []
    
    def get_linked_thoughts(self, work_item_id: str) -> List[ThoughtNode]:
        """Get all thoughts linked to a work item"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute("""
                    SELECT t.* FROM thought_nodes t
                    JOIN thought_references tr ON t.id = tr.thought_id
                    WHERE tr.work_item_id = ?
                """, (work_item_id,)).fetchall()
                
                return [ThoughtNode.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting linked thoughts for work item {work_item_id}: {e}")
            return [] 