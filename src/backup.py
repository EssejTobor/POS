import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, db_path: str = "work_items.db"):
        # Get the absolute path of the project root directory
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        logger.info(f"Created database backup: {backup_path}")
        return backup_path

    def restore_backup(self, backup_path: Path) -> None:
        """Restore database from a backup"""
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
        # Create backup of current database before restore
        self.create_backup(note="pre_restore")
        
        # Restore database
        shutil.copy2(backup_path, self.db_path)
        logger.info(f"Restored database from backup: {backup_path}")

    def list_backups(self) -> List[Path]:
        """List all available backups"""
        return sorted(
            [f for f in self.backup_dir.glob("work_items_*.db")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

    def cleanup_old_backups(self, keep_last: int = 5) -> None:
        """Remove old backups, keeping the specified number"""
        backups = self.list_backups()
        for backup in backups[keep_last:]:
            backup.unlink()
            logger.info(f"Removed old backup: {backup}")

    def export_to_json(self, output_path: Optional[Path] = None) -> Path:
        """Export database content to JSON for external backup"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.backup_dir / f"work_items_{timestamp}.json"

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Export work items
                cursor = conn.execute("SELECT * FROM work_items")
                items = [dict(row) for row in cursor.fetchall()]
                
                # Export entry counts (using goal_entry_count table if it exists)
                try:
                    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goal_entry_count'")
                    if cursor.fetchone():
                        cursor = conn.execute("SELECT * FROM goal_entry_count")
                    else:
                        cursor = conn.execute("SELECT * FROM entry_counts")
                    counts = {row['goal']: row['count'] for row in cursor.fetchall()}
                except Exception as e:
                    logger.warning(f"Error exporting entry counts: {e}")
                    counts = {}
                
                # Export thought data if tables exist
                thoughts = []
                thought_relationships = []
                thought_tags = []
                thought_references = []
                
                # Check if thought tables exist
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thought_nodes'")
                if cursor.fetchone():
                    try:
                        # Export thought nodes
                        cursor = conn.execute("SELECT * FROM thought_nodes")
                        thoughts = [dict(row) for row in cursor.fetchall()]
                        
                        # Export thought relationships
                        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thought_relationships'")
                        if cursor.fetchone():
                            cursor = conn.execute("SELECT * FROM thought_relationships")
                            thought_relationships = [dict(row) for row in cursor.fetchall()]
                        
                        # Export thought tags
                        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thought_tags'")
                        if cursor.fetchone():
                            cursor = conn.execute("SELECT * FROM thought_tags")
                            thought_tags = [dict(row) for row in cursor.fetchall()]
                        
                        # Export thought references (links to work items)
                        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thought_references'")
                        if cursor.fetchone():
                            cursor = conn.execute("SELECT * FROM thought_references")
                            thought_references = [dict(row) for row in cursor.fetchall()]
                    except Exception as e:
                        logger.warning(f"Error exporting thought data: {e}")
                
                # Compile all data
                data = {
                    'items': items,
                    'entry_counts': counts,
                    'thoughts': thoughts,
                    'thought_relationships': thought_relationships,
                    'thought_tags': thought_tags,
                    'thought_references': thought_references,
                    'export_date': datetime.now().isoformat(),
                    'version': '0.2.0'
                }
                
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Exported data to JSON: {output_path}")
                logger.info(f"Exported {len(items)} work items, {len(thoughts)} thoughts")
                return output_path
        except Exception as e:
            logger.error(f"Error exporting data to JSON: {e}", exc_info=True)
            raise
            
    def import_from_json(self, json_path: Path, overwrite: bool = False) -> None:
        """Import data from a JSON file into the database
        
        Args:
            json_path: Path to the JSON file to import
            overwrite: If True, delete existing data before import
        """
        if not json_path.exists():
            logger.error(f"JSON file not found: {json_path}")
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        # Create a backup before import
        self.create_backup(note="pre_import")
        
        try:
            # Load JSON data
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Validate data
            required_keys = ['items']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Required key '{key}' not found in JSON data")
            
            # Import data
            with sqlite3.connect(self.db_path) as conn:
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    # Import work items
                    if overwrite:
                        conn.execute("DELETE FROM work_items")
                    
                    work_items = data.get('items', [])
                    for item in work_items:
                        # Check if item already exists
                        cursor = conn.execute("SELECT COUNT(*) FROM work_items WHERE id = ?", (item['id'],))
                        if cursor.fetchone()[0] > 0 and not overwrite:
                            # Skip existing item if not overwriting
                            continue
                        
                        # Insert or replace item
                        placeholders = ', '.join(['?'] * len(item))
                        columns = ', '.join(item.keys())
                        values = list(item.values())
                        
                        conn.execute(
                            f"INSERT OR REPLACE INTO work_items ({columns}) VALUES ({placeholders})",
                            values
                        )
                    
                    # Import entry counts if available
                    if 'entry_counts' in data and data['entry_counts']:
                        # Check which table exists
                        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goal_entry_count'")
                        table_name = "goal_entry_count" if cursor.fetchone() else "entry_counts"
                        
                        if overwrite:
                            conn.execute(f"DELETE FROM {table_name}")
                        
                        for goal, count in data['entry_counts'].items():
                            conn.execute(
                                f"INSERT OR REPLACE INTO {table_name} (goal, count) VALUES (?, ?)",
                                (goal, count)
                            )
                    
                    # Ensure thought tables exist
                    self._ensure_thought_tables_exist(conn)
                    
                    # Import thought nodes if available
                    if 'thoughts' in data and data['thoughts']:
                        if overwrite:
                            conn.execute("DELETE FROM thought_nodes")
                        
                        thoughts = data.get('thoughts', [])
                        for thought in thoughts:
                            # Check if thought already exists
                            cursor = conn.execute("SELECT COUNT(*) FROM thought_nodes WHERE id = ?", (thought['id'],))
                            if cursor.fetchone()[0] > 0 and not overwrite:
                                # Skip existing thought if not overwriting
                                continue
                            
                            # Insert or replace thought
                            placeholders = ', '.join(['?'] * len(thought))
                            columns = ', '.join(thought.keys())
                            values = list(thought.values())
                            
                            conn.execute(
                                f"INSERT OR REPLACE INTO thought_nodes ({columns}) VALUES ({placeholders})",
                                values
                            )
                    
                    # Import thought relationships if available
                    if 'thought_relationships' in data and data['thought_relationships']:
                        if overwrite:
                            conn.execute("DELETE FROM thought_relationships")
                        
                        relationships = data.get('thought_relationships', [])
                        for rel in relationships:
                            # Check if relationship already exists
                            cursor = conn.execute(
                                "SELECT COUNT(*) FROM thought_relationships WHERE parent_id = ? AND child_id = ?", 
                                (rel['parent_id'], rel['child_id'])
                            )
                            if cursor.fetchone()[0] > 0 and not overwrite:
                                # Skip existing relationship if not overwriting
                                continue
                            
                            # Insert or replace relationship
                            placeholders = ', '.join(['?'] * len(rel))
                            columns = ', '.join(rel.keys())
                            values = list(rel.values())
                            
                            conn.execute(
                                f"INSERT OR REPLACE INTO thought_relationships ({columns}) VALUES ({placeholders})",
                                values
                            )
                    
                    # Import thought tags if available
                    if 'thought_tags' in data and data['thought_tags']:
                        if overwrite:
                            conn.execute("DELETE FROM thought_tags")
                        
                        tags = data.get('thought_tags', [])
                        for tag in tags:
                            # Check if tag already exists
                            cursor = conn.execute(
                                "SELECT COUNT(*) FROM thought_tags WHERE thought_id = ? AND tag = ?", 
                                (tag['thought_id'], tag['tag'])
                            )
                            if cursor.fetchone()[0] > 0 and not overwrite:
                                # Skip existing tag if not overwriting
                                continue
                            
                            # Insert or replace tag
                            placeholders = ', '.join(['?'] * len(tag))
                            columns = ', '.join(tag.keys())
                            values = list(tag.values())
                            
                            conn.execute(
                                f"INSERT OR REPLACE INTO thought_tags ({columns}) VALUES ({placeholders})",
                                values
                            )
                    
                    # Import thought references if available
                    if 'thought_references' in data and data['thought_references']:
                        if overwrite:
                            conn.execute("DELETE FROM thought_references")
                        
                        references = data.get('thought_references', [])
                        for ref in references:
                            # Check if reference already exists
                            cursor = conn.execute(
                                "SELECT COUNT(*) FROM thought_references WHERE thought_id = ? AND work_item_id = ?", 
                                (ref['thought_id'], ref['work_item_id'])
                            )
                            if cursor.fetchone()[0] > 0 and not overwrite:
                                # Skip existing reference if not overwriting
                                continue
                            
                            # Insert or replace reference
                            placeholders = ', '.join(['?'] * len(ref))
                            columns = ', '.join(ref.keys())
                            values = list(ref.values())
                            
                            conn.execute(
                                f"INSERT OR REPLACE INTO thought_references ({columns}) VALUES ({placeholders})",
                                values
                            )
                    
                    # Update FTS tables if they exist
                    self._update_fts_tables(conn)
                    
                    # Commit transaction
                    conn.commit()
                    
                    # Log summary
                    logger.info(f"Imported data from JSON: {json_path}")
                    logger.info(f"Imported {len(data.get('items', []))} work items, {len(data.get('thoughts', []))} thoughts")
                    
                except Exception as e:
                    # Rollback on error
                    conn.rollback()
                    logger.error(f"Error importing data: {e}", exc_info=True)
                    raise
        except Exception as e:
            logger.error(f"Error importing data from JSON: {e}", exc_info=True)
            raise
    
    def _ensure_thought_tables_exist(self, conn: sqlite3.Connection) -> None:
        """Ensure thought-related tables exist"""
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
            
            -- Thought tags
            CREATE TABLE IF NOT EXISTS thought_tags (
                thought_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                PRIMARY KEY (thought_id, tag),
                FOREIGN KEY (thought_id) REFERENCES thought_nodes(id)
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
    
    def _update_fts_tables(self, conn: sqlite3.Connection) -> None:
        """Update FTS tables with current data"""
        # Check if work_items_fts exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='work_items_fts'")
        if cursor.fetchone():
            try:
                # Rebuild work_items_fts
                conn.execute("DELETE FROM work_items_fts")
                conn.execute("""
                    INSERT INTO work_items_fts(id, title, description)
                    SELECT id, title, description FROM work_items
                """)
                logger.info("Rebuilt work_items_fts index")
            except Exception as e:
                logger.warning(f"Error rebuilding work_items_fts: {e}")
        
        # Check if thought_nodes_fts exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thought_nodes_fts'")
        if cursor.fetchone():
            try:
                # Rebuild thought_nodes_fts
                conn.execute("DELETE FROM thought_nodes_fts")
                conn.execute("""
                    INSERT INTO thought_nodes_fts(id, title, content)
                    SELECT id, title, content FROM thought_nodes
                """)
                logger.info("Rebuilt thought_nodes_fts index")
            except Exception as e:
                logger.warning(f"Error rebuilding thought_nodes_fts: {e}") 