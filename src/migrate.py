from datetime import datetime
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import sqlite3

from .models import WorkItem, ItemType, ItemStatus, Priority
from .database import Database
from .backup import BackupManager

class MigrationManager:
    def __init__(self, json_path: str = "work_items.json", db_path: str = "work_items.db"):
        self.json_path = Path(json_path)
        self.db_path = Path(db_path)
        self.backup_manager = BackupManager(db_path)
        self.db = Database(db_path)

    def validate_json_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate JSON data format and content"""
        errors = []
        
        # Check basic structure
        if isinstance(data, dict) and 'items' in data:
            items_dict = data['items']
        else:
            items_dict = data
            
        # Validate each item
        for item_id, item_data in items_dict.items():
            try:
                # Check required fields
                required_fields = ['title', 'item_type', 'description', 'status']
                missing_fields = [f for f in required_fields if f not in item_data]
                if missing_fields:
                    errors.append(f"Item {item_id} missing fields: {', '.join(missing_fields)}")
                    continue
                
                # Validate enum values
                if 'item_type' in item_data:
                    try:
                        ItemType(item_data['item_type'])
                    except ValueError:
                        errors.append(f"Item {item_id} has invalid item_type: {item_data['item_type']}")
                
                if 'priority' in item_data:
                    try:
                        Priority(item_data['priority'])
                    except ValueError:
                        errors.append(f"Item {item_id} has invalid priority: {item_data['priority']}")
                
                if 'status' in item_data:
                    try:
                        ItemStatus(item_data['status'])
                    except ValueError:
                        errors.append(f"Item {item_id} has invalid status: {item_data['status']}")
                
                # Validate timestamps
                for timestamp_field in ['created_at', 'updated_at']:
                    if timestamp_field in item_data:
                        try:
                            self._parse_timestamp(item_data[timestamp_field])
                        except ValueError:
                            errors.append(f"Item {item_id} has invalid {timestamp_field}")
                            
            except Exception as e:
                errors.append(f"Error validating item {item_id}: {str(e)}")
                
        return errors

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp with multiple format support"""
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO format with microseconds
            "%Y-%m-%dT%H:%M:%S",     # ISO format without microseconds
            "%Y-%m-%d %H:%M:%S",     # Standard format
            "%Y-%m-%d %H:%M"         # Simple format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")

    def migrate_json_to_sqlite(self, batch_size: int = 100) -> Tuple[int, List[str]]:
        """
        Migrate data from JSON to SQLite with batch processing
        Returns: (number of migrated items, list of errors)
        """
        if not self.json_path.exists():
            raise FileNotFoundError(f"No JSON file found at {self.json_path}")

        # Create backup before migration
        self.backup_manager.create_backup(note="pre_migration")
        
        try:
            # Read and validate JSON data
            with open(self.json_path, 'r') as f:
                data = json.load(f)
            
            validation_errors = self.validate_json_data(data)
            if validation_errors:
                return 0, validation_errors

            # Extract data based on format
            if isinstance(data, dict) and 'items' in data:
                items_dict = data['items']
                entry_counts = data.get('entry_counts', {})
            else:
                items_dict = data
                entry_counts = {}

            # Process items in batches
            items_batch = []
            processed_count = 0
            migration_errors = []

            for item_data in items_dict.values():
                try:
                    goal = item_data.get('goal', 'legacy')
                    
                    # Create WorkItem
                    item = WorkItem(
                        id=item_data['id'],
                        title=item_data['title'],
                        goal=goal,
                        item_type=ItemType(item_data['item_type']),
                        description=item_data['description'],
                        priority=Priority(item_data['priority']),
                        status=ItemStatus(item_data['status']),
                        created_at=self._parse_timestamp(item_data['created_at']),
                        updated_at=self._parse_timestamp(item_data['updated_at'])
                    )
                    items_batch.append(item)
                    
                    # Process batch if full
                    if len(items_batch) >= batch_size:
                        self.db.batch_insert_items(items_batch)
                        processed_count += len(items_batch)
                        items_batch = []
                        
                except Exception as e:
                    migration_errors.append(f"Error processing item {item_data.get('id', 'unknown')}: {str(e)}")

            # Process remaining items
            if items_batch:
                self.db.batch_insert_items(items_batch)
                processed_count += len(items_batch)

            # Migrate entry counts
            for goal, count in entry_counts.items():
                self.db.update_entry_count(goal, count)

            # Create backup of JSON file
            backup_path = self.json_path.with_suffix('.json.bak')
            self.json_path.rename(backup_path)

            return processed_count, migration_errors

        except Exception as e:
            return 0, [f"Migration failed: {str(e)}"]

if __name__ == '__main__':
    manager = MigrationManager()
    count, errors = manager.migrate_json_to_sqlite()
    if errors:
        print("\n".join(errors))
    else:
        print(f"Successfully migrated {count} items") 