from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager
from sqlite3 import IntegrityError, OperationalError

from .models import WorkItem, ItemType, ItemStatus, Priority
from .database import Database
from .backup import BackupManager

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
        self.backup_manager = BackupManager(storage_path)
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

    @contextmanager
    def _atomic_operation(self):
        """Ensure atomic operations with proper rollback"""
        items_snapshot = self.items.copy()
        try:
            yield
        except Exception as e:
            self.items = items_snapshot
            raise e

    def _refresh_cache(self):
        """Refresh the in-memory cache from database"""
        self.items = self.db.get_all_items()
        self.entry_counts = self.db.get_all_entry_counts()

    def add_item(self, goal: str, title: str, item_type: ItemType,
                 description: str, priority: Priority = Priority.MED) -> WorkItem:
        """Enhanced add_item with atomic operations and proper error handling"""
        with self._atomic_operation():
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
                
                # Add to database first
                try:
                    self.db.add_item(item)
                except IntegrityError:
                    raise ValueError(f"Item with ID {item.id} already exists")
                except OperationalError as e:
                    raise RuntimeError(f"Database error: {str(e)}")
                
                # Update cache only after successful database operation
                self.items[item.id] = item
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
        """Enhanced update_status with atomic operations"""
        with self._atomic_operation():
            try:
                if item_id not in self.items:
                    raise ValueError(f"Item {item_id} not found")
                    
                item = self.items[item_id]
                old_status = item.status
                
                try:
                    item.update_status(new_status)
                    self.db.update_item(item)
                except Exception as e:
                    item.status = old_status  # Rollback in-memory change
                    raise RuntimeError(f"Failed to update status: {str(e)}")
                    
            except Exception as e:
                print(f"Error updating status: {e}")
                raise

    def update_item_priority(self, item_id: str, new_priority: Priority):
        """Enhanced update_priority with atomic operations"""
        with self._atomic_operation():
            try:
                if item_id not in self.items:
                    raise ValueError(f"Item {item_id} not found")
                    
                item = self.items[item_id]
                old_priority = item.priority
                
                try:
                    item.update_priority(new_priority)
                    self.db.update_item(item)
                except Exception as e:
                    item.priority = old_priority  # Rollback in-memory change
                    raise RuntimeError(f"Failed to update priority: {str(e)}")
                    
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
        """Enhanced merge_duplicates with atomic operations"""
        with self._atomic_operation():
            try:
                merged_pairs = []
                seen_keys = {}
                items_to_remove = set()

                for item in list(self.items.values()):
                    key = self._get_item_key(item.title, item.item_type, item.priority)
                    
                    if key in seen_keys:
                        original_item = seen_keys[key]
                        if item.created_at > original_item.created_at:
                            items_to_remove.add(item.id)
                            merged_pairs.append((original_item, item))
                        else:
                            items_to_remove.add(original_item.id)
                            seen_keys[key] = item
                            merged_pairs.append((item, original_item))
                    else:
                        seen_keys[key] = item

                # Remove merged duplicates atomically
                with self.db.get_connection() as conn:
                    for item_id in items_to_remove:
                        conn.execute("DELETE FROM work_items WHERE id = ?", (item_id,))
                    conn.commit()

                # Update cache after successful database operation
                for item_id in items_to_remove:
                    del self.items[item_id]

                return merged_pairs
                
            except Exception as e:
                print(f"Error merging duplicates: {e}")
                self._refresh_cache()  # Ensure cache is consistent
                raise

    def get_filtered_items(self, 
                         goal: Optional[str] = None,
                         status: Optional[ItemStatus] = None,
                         priority: Optional[Priority] = None,
                         item_type: Optional[ItemType] = None) -> List[WorkItem]:
        """Use optimized database query directly"""
        return self.db.get_items_by_filters(
            goal=goal,
            status=status,
            priority=priority,
            item_type=item_type
        )

    def optimize_database(self):
        """Optimize the database by removing unused space"""
        self.db.execute_vacuum()
        
    def add_link(self, source_id: str, target_id: str, link_type: str = "references") -> bool:
        """
        Create a link between two work items
        
        Args:
            source_id: ID of the source item
            target_id: ID of the target item
            link_type: Type of relationship (default: "references")
            
        Returns:
            bool: True if the link was added successfully, False otherwise
        """
        try:
            # Verify both items exist in our cache
            if source_id not in self.items or target_id not in self.items:
                print(f"Error adding link: One or both items don't exist")
                return False
                
            with self._atomic_operation():
                return self.db.add_link(source_id, target_id, link_type)
        except Exception as e:
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
            with self._atomic_operation():
                return self.db.remove_link(source_id, target_id)
        except Exception as e:
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
        try:
            if item_id not in self.items:
                print(f"Error getting links: Item {item_id} doesn't exist")
                return {'outgoing': [], 'incoming': []}
                
            return self.db.get_links(item_id)
        except Exception as e:
            print(f"Error getting links: {e}")
            return {'outgoing': [], 'incoming': []} 