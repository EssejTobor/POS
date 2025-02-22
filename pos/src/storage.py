from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from .models import WorkItem, ItemType, ItemStatus, Priority
from .database import Database

class WorkSystem:
    """
    Core system for managing work items. Provides:
    - Persistent storage using SQLite
    - Item creation and retrieval
    - Status and priority updates
    - Various sorting and filtering capabilities
    """
    def __init__(self, storage_path: str = "work_items.db"):
        """
        Initialize the work system
        Args:
            storage_path: Location of the SQLite database file
        """
        self.db = Database(storage_path)
        self.items = self.db.get_all_items()
        self.entry_counts = self.db.get_all_entry_counts()

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
        
        self.db.update_entry_count(goal, self.entry_counts[goal])
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
            self.db.add_item(item)
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
        items = self.db.get_items_by_goal(goal)
        return sorted(
            items,
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_items_by_goal_priority(self, goal: str) -> List[WorkItem]:
        """Retrieves items for a goal, sorted only by priority."""
        items = self.db.get_items_by_goal(goal)
        return sorted(
            items,
            key=lambda x: (x.priority.value),
            reverse=True
        )

    def get_items_by_goal_id(self, goal: str) -> List[WorkItem]:
        """Get items for a goal, sorted by creation time (newest first)"""
        items = self.db.get_items_by_goal(goal)
        return sorted(
            items,
            key=lambda x: x.created_at,
            reverse=True
        )

    def get_incomplete_items(self) -> List[WorkItem]:
        """Get all incomplete items across all goals, sorted by priority"""
        items = self.db.get_incomplete_items()
        return sorted(
            items,
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_items_by_type(self, item_type: ItemType) -> List[WorkItem]:
        items = self.db.get_items_by_type(item_type)
        return sorted(
            items,
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_all_goals(self) -> List[str]:
        return self.db.get_all_goals()

    def update_item_status(self, item_id: str, new_status: ItemStatus):
        try:
            if item_id in self.items:
                item = self.items[item_id]
                item.update_status(new_status)
                self.db.update_item(item)
            else:
                print(f"Item {item_id} not found")
        except Exception as e:
            print(f"Error updating status: {e}")
            raise

    def update_item_priority(self, item_id: str, new_priority: Priority):
        try:
            if item_id in self.items:
                item = self.items[item_id]
                item.update_priority(new_priority)
                self.db.update_item(item)
            else:
                print(f"Item {item_id} not found")
        except Exception as e:
            print(f"Error updating priority: {e}")
            raise

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
            # Update the database to reflect the changes
            for item_id in items_to_remove:
                with self.db.get_connection() as conn:
                    conn.execute("DELETE FROM work_items WHERE id = ?", (item_id,))
                    conn.commit()

        return merged_pairs 