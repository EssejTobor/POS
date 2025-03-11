import sqlite3
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, Any
import logging
import threading

from .config import Config

logger = logging.getLogger(__name__)

class SchemaMigrator:
    """Handles database schema migrations with versioning"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with optional custom db path"""
        self.db_path = Path(db_path) if db_path else Config.get_db_path()
        self.lock = threading.Lock()
        
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error in migrator: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def run_migrations(self):
        """Apply pending migrations based on schema version"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    # Create version table if it doesn't exist
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS schema_version (
                            version INTEGER PRIMARY KEY,
                            applied_at TEXT NOT NULL,
                            description TEXT NOT NULL
                        )
                    """)
                    
                    # Get current version
                    cur = conn.execute("SELECT MAX(version) as max_version FROM schema_version")
                    result = cur.fetchone()
                    current_version = result['max_version'] if result and result['max_version'] is not None else 0
                    
                    logger.info(f"Current schema version: {current_version}")
                    
                    # Apply migrations in order
                    migrations_applied = 0
                    
                    if current_version < 1:
                        logger.info("Applying migration v1: Thought tracking tables")
                        self._apply_v1_migration(conn)
                        migrations_applied += 1
                    
                    if current_version < 2:
                        logger.info("Applying migration v2: FTS5 search tables")
                        self._apply_v2_migration(conn)
                        migrations_applied += 1
                    
                    # Add more version checks as needed
                    
                    logger.info(f"Applied {migrations_applied} migrations, current version: {current_version + migrations_applied}")
                    return migrations_applied
            except Exception as e:
                logger.error(f"Migration failed: {e}", exc_info=True)
                raise
    
    def _apply_v1_migration(self, conn):
        """Apply version 1 schema changes (thought tracking)"""
        # Create thought tables
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
        
        # Apply changes to existing item types
        self._migrate_item_types(conn)
        
        # Record migration
        conn.execute(
            "INSERT INTO schema_version (version, applied_at, description) VALUES (?, ?, ?)",
            (1, datetime.now().isoformat(), "Thought tracking tables")
        )
    
    def _apply_v2_migration(self, conn):
        """Apply version 2 schema changes (FTS tables)"""
        # Create FTS tables
        conn.executescript("""
            -- FTS for work items
            CREATE VIRTUAL TABLE IF NOT EXISTS work_items_fts USING fts5(
                id, title, description, content='work_items',
                tokenize='porter unicode61 remove_diacritics 1'
            );
            
            -- FTS for thoughts
            CREATE VIRTUAL TABLE IF NOT EXISTS thought_nodes_fts USING fts5(
                id, title, content, content='thought_nodes',
                tokenize='porter unicode61 remove_diacritics 1'
            );
            
            -- Triggers for work_items FTS
            CREATE TRIGGER IF NOT EXISTS work_items_ai AFTER INSERT ON work_items
            BEGIN
                INSERT INTO work_items_fts(id, title, description)
                VALUES (new.id, new.title, new.description);
            END;
            
            CREATE TRIGGER IF NOT EXISTS work_items_ad AFTER DELETE ON work_items
            BEGIN
                INSERT INTO work_items_fts(work_items_fts, id, title, description)
                VALUES ('delete', old.id, old.title, old.description);
            END;
            
            CREATE TRIGGER IF NOT EXISTS work_items_au AFTER UPDATE ON work_items
            BEGIN
                INSERT INTO work_items_fts(work_items_fts, id, title, description)
                VALUES ('delete', old.id, old.title, old.description);
                INSERT INTO work_items_fts(id, title, description)
                VALUES (new.id, new.title, new.description);
            END;
            
            -- Triggers for thought_nodes FTS
            CREATE TRIGGER IF NOT EXISTS thought_nodes_ai AFTER INSERT ON thought_nodes
            BEGIN
                INSERT INTO thought_nodes_fts(id, title, content)
                VALUES (new.id, new.title, new.content);
            END;
            
            CREATE TRIGGER IF NOT EXISTS thought_nodes_ad AFTER DELETE ON thought_nodes
            BEGIN
                INSERT INTO thought_nodes_fts(thought_nodes_fts, id, title, content)
                VALUES ('delete', old.id, old.title, old.content);
            END;
            
            CREATE TRIGGER IF NOT EXISTS thought_nodes_au AFTER UPDATE ON thought_nodes
            BEGIN
                INSERT INTO thought_nodes_fts(thought_nodes_fts, id, title, content)
                VALUES ('delete', old.id, old.title, old.content);
                INSERT INTO thought_nodes_fts(id, title, content)
                VALUES (new.id, new.title, new.content);
            END;
        """)
        
        # Populate FTS tables with existing data
        conn.executescript("""
            -- Populate work_items FTS with existing data
            INSERT INTO work_items_fts(id, title, description)
            SELECT id, title, description FROM work_items;
            
            -- Populate thought_nodes FTS with existing data (if any)
            INSERT INTO thought_nodes_fts(id, title, content)
            SELECT id, title, content FROM thought_nodes;
        """)
        
        # Record migration
        conn.execute(
            "INSERT INTO schema_version (version, applied_at, description) VALUES (?, ?, ?)",
            (2, datetime.now().isoformat(), "FTS5 search tables")
        )
    
    def _migrate_item_types(self, conn):
        """Update existing item types to new naming"""
        # Create mapping
        type_mapping = {
            't': 'do',
            'l': 'learn',
            'r': 'research'
        }
        
        try:
            # Get all items
            items = conn.execute("SELECT id, item_type FROM work_items").fetchall()
            
            # Update types
            updated_count = 0
            for item in items:
                old_type = item['item_type']
                if old_type in type_mapping:
                    new_type = type_mapping[old_type]
                    conn.execute(
                        "UPDATE work_items SET item_type = ? WHERE id = ?",
                        (new_type, item['id'])
                    )
                    updated_count += 1
            
            logger.info(f"Migrated {updated_count} work items to new type format")
        except Exception as e:
            logger.error(f"Error during item type migration: {e}")
            raise 