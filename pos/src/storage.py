import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from .models import WorkItem, ItemType, ItemStatus, Priority

class WorkSystem:
    """
    Core system for managing work items. Provides:
    - Persistent storage using JSON
    - Item creation and retrieval
    - Status and priority updates
    - Various sorting and filtering capabilities
    - Backup management during saves
    """
    def __init__(self, storage_path: str = "work_items.json"):
        """
        Initialize the work system
        Args:
            storage_path: Location of the JSON storage file
        """
        self.storage_path = Path(storage_path)
        self.items: Dict[str, WorkItem] = {}
        self.entry_counts: Dict[str, int] = {}  # Track entries per goal
        self.load_items()

    def generate_id(self, goal: str, item_type: ItemType, priority: Priority) -> str:
        """
        Creates a unique ID combining:
        - First letter of goal (g)
        - Type initial (t/l/r)
        - Priority number (1/2/3)
        - Sequential number for the goal
        - Current time
        
        Example: gt21230pm (goal-task-priority2-item1-2:30pm)
        """
        goal_initial = goal[0].lower()
        type_initial = item_type.value[0].lower()
        priority_num = priority.value
        
        if goal not in self.entry_counts:
            self.entry_counts[goal] = 0
        self.entry_counts[goal] += 1
        entry_num = self.entry_counts[goal]
        
        now = datetime.now()
        time_str = str(int(now.strftime("%I"))) + now.strftime("%M%p").lower()
        
        return f"{goal_initial}{type_initial}{priority_num}{entry_num}{time_str}"

    def _get_item_key(self, title: str, item_type: ItemType, priority: Priority) -> str:
        """
        Creates a unique key for duplicate detection.
        Normalizes the title by lowercasing and removing extra whitespace.
        """
        normalized_title = " ".join(title.lower().split())
        return f"{normalized_title}|{item_type.value}|{priority.value}"

    def find_duplicate(self, title: str, item_type: ItemType, priority: Priority) -> Optional[WorkItem]:
        """
        Checks if an item with the same title, type and priority already exists.
        Returns the existing item if found, None otherwise.
        """
        search_key = self._get_item_key(title, item_type, priority)
        
        for item in self.items.values():
            item_key = self._get_item_key(item.title, item.item_type, item.priority)
            if item_key == search_key:
                return item
        return None

    def add_item(self, goal: str, title: str, item_type: ItemType,
                 description: str, priority: Priority = Priority.MED) -> WorkItem:
        """
        Enhanced add_item with duplicate detection.
        Raises ValueError if a duplicate is found.
        """
        try:
            # Check for duplicates first
            existing_item = self.find_duplicate(title, item_type, priority)
            if existing_item:
                raise ValueError(
                    f"Duplicate item found (ID: {existing_item.id}):\n"
                    f"Title: {existing_item.title}\n"
                    f"Type: {existing_item.item_type.value}\n"
                    f"Priority: {existing_item.priority.name}"
                )

            item = WorkItem(
                title=title,
                goal=goal,
                item_type=item_type,
                description=description,
                priority=priority
            )
            item.id = self.generate_id(goal, item_type, priority)
            self.items[item.id] = item
            self.save_items()
            return item
        except Exception as e:
            print(f"Error adding item: {e}")
            raise

    def get_items_by_goal(self, goal: str) -> List[WorkItem]:
        """
        Retrieves items for a specific goal, sorted by:
        1. Priority (highest first)
        2. Creation time (newest first)
        """
        return sorted(
            [item for item in self.items.values() if item.goal.lower() == goal.lower()],
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_items_by_goal_priority(self, goal: str) -> List[WorkItem]:
        """Retrieves items for a goal, sorted only by priority."""
        return sorted(
            [item for item in self.items.values() if item.goal.lower() == goal.lower()],
            key=lambda x: (x.priority.value),
            reverse=True
        )

    def get_items_by_goal_id(self, goal: str) -> List[WorkItem]:
        """Get items for a goal, sorted by creation time (newest first)"""
        return sorted(
            [item for item in self.items.values() if item.goal.lower() == goal.lower()],
            key=lambda x: x.created_at,
            reverse=True
        )

    def get_incomplete_items(self) -> List[WorkItem]:
        """Get all incomplete items across all goals, sorted by priority"""
        return sorted(
            [item for item in self.items.values() 
             if item.status != ItemStatus.COMPLETED],
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_items_by_type(self, item_type: ItemType) -> List[WorkItem]:
        return sorted(
            [item for item in self.items.values() if item.item_type == item_type],
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_all_goals(self) -> List[str]:
        return sorted(list(set(item.goal for item in self.items.values())))

    def update_item_status(self, item_id: str, new_status: ItemStatus):
        try:
            if item_id in self.items:
                item = self.items[item_id]
                item.update_status(new_status)
                self.save_items()
            else:
                print(f"Item {item_id} not found")
        except Exception as e:
            print(f"Error updating status: {e}")
            raise

    def update_item_priority(self, item_id: str, new_priority: Priority):
        try:
            if item_id in self.items:
                self.items[item_id].update_priority(new_priority)
                self.save_items()
            else:
                print(f"Item {item_id} not found")
        except Exception as e:
            print(f"Error updating priority: {e}")
            raise

    def save_items(self):
        try:
            items_dict = {id_: item.to_dict() for id_, item in self.items.items()}
            data = {
                'items': items_dict,
                'entry_counts': self.entry_counts
            }
            
            if self.storage_path.exists():
                backup_path = self.storage_path.with_suffix('.json.bak')
                self.storage_path.rename(backup_path)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            if Path(str(self.storage_path) + '.bak').exists():
                Path(str(self.storage_path) + '.bak').unlink()
                
        except Exception as e:
            print(f"Error saving items: {e}")
            if Path(str(self.storage_path) + '.bak').exists():
                Path(str(self.storage_path) + '.bak').rename(self.storage_path)
            raise

    def load_items(self):
        if not self.storage_path.exists():
            return
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, dict) and 'items' in data:
            items_dict = data['items']
            self.entry_counts = data.get('entry_counts', {})
        else:
            items_dict = data
            self.entry_counts = {}
            
        for _, item_data in items_dict.items():
            goal = item_data.get('goal', 'legacy')
            
            item = WorkItem(
                title=item_data['title'],
                goal=goal,
                item_type=ItemType(item_data['item_type']),
                description=item_data['description'],
                priority=Priority(item_data['priority']),
                status=ItemStatus(item_data['status']),
                id=item_data['id'],
                created_at=datetime.fromisoformat(item_data['created_at']),
                updated_at=datetime.fromisoformat(item_data['updated_at'])
            )
            self.items[item.id] = item
            
            if goal not in self.entry_counts:
                self.entry_counts[goal] = 0
            self.entry_counts[goal] = max(self.entry_counts[goal], 
                int(''.join(filter(str.isdigit, item.id[:4])) or 0))

    def export_markdown(self, output_path: str = "work_items.md"):
        with open(output_path, 'w') as f:
            f.write("# Work Items\n\n")
            
            goals = self.get_all_goals()
            for goal in goals:
                f.write(f"## Goal: {goal}\n\n")
                goal_items = self.get_items_by_goal(goal)
                
                for item_type in ItemType:
                    type_items = [item for item in goal_items if item.item_type == item_type]
                    if not type_items:
                        continue
                        
                    f.write(f"### {item_type.value.title()}\n\n")
                    
                    for priority in reversed(list(Priority)):
                        priority_items = [item for item in type_items if item.priority == priority]
                        if not priority_items:
                            continue
                            
                        f.write(f"#### {priority.name.title()} Priority\n\n")
                        
                        for item in priority_items:
                            f.write(f"##### {item.title}\n")
                            f.write(f"- **ID**: {item.id}\n")
                            f.write(f"- **Status**: {item.status.value}\n")
                            f.write(f"- **Created**: {item.created_at.strftime('%Y-%m-%d %H:%M')}\n")
                            f.write(f"- **Description**: {item.description}\n\n")

    def merge_duplicates(self) -> List[tuple[WorkItem, WorkItem]]:
        """
        Scans existing items for duplicates and merges them.
        Returns list of merged pairs for reporting.
        """
        merged_pairs = []
        seen_keys = {}
        items_to_remove = set()

        for item in list(self.items.values()):
            key = self._get_item_key(item.title, item.item_type, item.priority)
            
            if key in seen_keys:
                original_item = seen_keys[key]
                # Keep the older item, remove the newer one
                if item.created_at > original_item.created_at:
                    items_to_remove.add(item.id)
                    merged_pairs.append((original_item, item))
                else:
                    items_to_remove.add(original_item.id)
                    seen_keys[key] = item
                    merged_pairs.append((item, original_item))
            else:
                seen_keys[key] = item

        # Remove merged duplicates
        for item_id in items_to_remove:
            del self.items[item_id]

        if merged_pairs:
            self.save_items()

        return merged_pairs 