import json
from pathlib import Path
from typing import Dict, Any

from .models import WorkItem, ItemType, ItemStatus, Priority
from .database import Database

def migrate_json_to_sqlite(json_path: str = "work_items.json", db_path: str = "work_items.db"):
    """
    Migrate data from JSON storage to SQLite database
    
    Args:
        json_path: Path to the JSON file
        db_path: Path to the SQLite database
    """
    json_path = Path(json_path)
    if not json_path.exists():
        print(f"No JSON file found at {json_path}")
        return
        
    try:
        # Read JSON data
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Initialize database
        db = Database(db_path)
        
        # Extract data based on format
        if isinstance(data, dict) and 'items' in data:
            items_dict = data['items']
            entry_counts = data.get('entry_counts', {})
        else:
            items_dict = data
            entry_counts = {}
            
        # Migrate items
        for item_data in items_dict.values():
            goal = item_data.get('goal', 'legacy')
            
            item = WorkItem(
                id=item_data['id'],
                title=item_data['title'],
                goal=goal,
                item_type=ItemType(item_data['item_type']),
                description=item_data['description'],
                priority=Priority(item_data['priority']),
                status=ItemStatus(item_data['status']),
                created_at=item_data['created_at'],
                updated_at=item_data['updated_at']
            )
            db.add_item(item)
            
        # Migrate entry counts
        for goal, count in entry_counts.items():
            db.update_entry_count(goal, count)
            
        print(f"Successfully migrated {len(items_dict)} items to SQLite database")
        
        # Create backup of JSON file
        backup_path = json_path.with_suffix('.json.bak')
        json_path.rename(backup_path)
        print(f"Created backup of JSON file at {backup_path}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == '__main__':
    migrate_json_to_sqlite() 