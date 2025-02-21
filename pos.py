from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict
import json
from pathlib import Path
import uuid
import cmd
import argparse
from textwrap import dedent

class ItemType(Enum):
    TASK = "task"          # Concrete, completable actions
    LEARNING = "learning"  # Skills/knowledge to acquire
    RESEARCH = "research"  # Less structured exploration

class ItemStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

@dataclass
class WorkItem:
    title: str
    item_type: ItemType
    description: str
    priority: Priority = Priority.MEDIUM
    status: ItemStatus = ItemStatus.NOT_STARTED
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_status(self, new_status: ItemStatus):
        self.status = new_status
        self.updated_at = datetime.now()

    def update_priority(self, new_priority: Priority):
        self.priority = new_priority
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'item_type': self.item_type.value,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WorkSystem:
    def __init__(self, storage_path: str = "work_items.json"):
        self.storage_path = Path(storage_path)
        self.items: Dict[str, WorkItem] = {}
        self.load_items()
    
    def export_markdown(self, output_path: str = "work_items.md"):
        """Export all items to a markdown file, organized by type and priority."""
        with open(output_path, 'w') as f:
            f.write("# Work Items\n\n")
            
            # Process each type
            for item_type in ItemType:
                items = self.get_items_by_type(item_type)
                if not items:
                    continue
                    
                f.write(f"## {item_type.value.title()}\n\n")
                
                # Group by priority
                for priority in reversed(list(Priority)):
                    priority_items = [item for item in items if item.priority == priority]
                    if not priority_items:
                        continue
                        
                    f.write(f"### {priority.name.title()} Priority\n\n")
                    
                    # Write each item
                    for item in priority_items:
                        f.write(f"#### {item.title}\n")
                        f.write(f"- **ID**: {item.id}\n")
                        f.write(f"- **Status**: {item.status.value}\n")
                        f.write(f"- **Created**: {item.created_at.strftime('%Y-%m-%d %H:%M')}\n")
                        f.write(f"- **Updated**: {item.updated_at.strftime('%Y-%m-%d %H:%M')}\n")
                        f.write(f"- **Description**: {item.description}\n\n")

    def add_item(self, 
                 title: str,
                 item_type: ItemType,
                 description: str,
                 priority: Priority = Priority.MEDIUM) -> WorkItem:
        try:
            item = WorkItem(
                title=title,
                item_type=item_type,
                description=description,
                priority=priority
            )
            self.items[item.id] = item
            self.save_items()
            return item
        except Exception as e:
            print(f"Error adding item: {e}")
            raise

    def get_items_by_type(self, item_type: ItemType) -> List[WorkItem]:
        return sorted(
            [item for item in self.items.values() if item.item_type == item_type],
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_items_by_status(self, status: ItemStatus) -> List[WorkItem]:
        return sorted(
            [item for item in self.items.values() if item.status == status],
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def update_item_status(self, item_id: str, new_status: ItemStatus):
        try:
            if item_id in self.items:
                self.items[item_id].update_status(new_status)
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
            # Create a backup of the existing file if it exists
            if self.storage_path.exists():
                backup_path = self.storage_path.with_suffix('.json.bak')
                self.storage_path.rename(backup_path)
            
            # Write the new data
            with open(self.storage_path, 'w') as f:
                json.dump(items_dict, f, indent=2)
            
            # Remove the backup if save was successful
            if Path(str(self.storage_path) + '.bak').exists():
                Path(str(self.storage_path) + '.bak').unlink()
                
        except Exception as e:
            print(f"Error saving items: {e}")
            # Restore from backup if save failed
            if Path(str(self.storage_path) + '.bak').exists():
                Path(str(self.storage_path) + '.bak').rename(self.storage_path)
            raise

    def load_items(self):
        if not self.storage_path.exists():
            return
        
        with open(self.storage_path, 'r') as f:
            items_dict = json.load(f)
            
        for _, item_data in items_dict.items():
            item = WorkItem(
                title=item_data['title'],
                item_type=ItemType(item_data['item_type']),
                description=item_data['description'],
                priority=Priority(item_data['priority']),
                status=ItemStatus(item_data['status']),
                id=item_data['id'],
                created_at=datetime.fromisoformat(item_data['created_at']),
                updated_at=datetime.fromisoformat(item_data['updated_at'])
            )
            self.items[item.id] = item

class WorkSystemCLI(cmd.Cmd):
    intro = 'Welcome to the Work System. Type help or ? to list commands.\n'
    prompt = '(work) '

    def __init__(self):
        super().__init__()
        self.work_system = WorkSystem()

    def do_add(self, arg):
        """Add a new work item: add <type> <priority> <title> <description>
        Types: task, learning, research
        Priority: low, medium, high
        Example: add task high "Learn Python" "Complete Python tutorial"
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('type', choices=['task', 'learning', 'research'])
        parser.add_argument('priority', choices=['low', 'medium', 'high'])
        parser.add_argument('title')
        parser.add_argument('description')

        try:
            # Split by spaces, but respect quoted strings
            args = parser.parse_args(arg.split(' "')[0].split() + 
                                   [x.strip('"') for x in arg.split('" "')[0:2]])
            
            item = self.work_system.add_item(
                title=args.title,
                item_type=ItemType(args.type),
                description=args.description,
                priority=Priority[args.priority.upper()]
            )
            print(f"Added: {item.title} (ID: {item.id})")
        except Exception as e:
            print(f"Error: {e}")

    def do_list(self, arg):
        """List work items by type: list [task|learning|research|all]"""
        arg = arg.lower().strip()
        if arg and arg not in ['task', 'learning', 'research', 'all']:
            print("Invalid type. Use: task, learning, research, or all")
            return

        def print_items(items):
            for item in items:
                print(f"\nID: {item.id}")
                print(f"Title: {item.title}")
                print(f"Type: {item.item_type.value}")
                print(f"Priority: {item.priority.name}")
                print(f"Status: {item.status.value}")
                print(f"Description: {item.description}")
                print("-" * 40)

        if arg == 'all' or not arg:
            for type_ in ItemType:
                items = self.work_system.get_items_by_type(type_)
                if items:
                    print(f"\n{type_.value.upper()} ITEMS:")
                    print_items(items)
        else:
            items = self.work_system.get_items_by_type(ItemType(arg))
            print(f"\n{arg.upper()} ITEMS:")
            print_items(items)

    def do_update(self, arg):
        """Update item status: update <id> <status|priority> <new_value>
        Status options: not_started, in_progress, completed
        Priority options: low, medium, high
        Example: update 123 status in_progress
        """
        try:
            item_id, field, value = arg.split()
            if field == 'status':
                self.work_system.update_item_status(item_id, ItemStatus(value))
            elif field == 'priority':
                self.work_system.update_item_priority(item_id, Priority[value.upper()])
            print(f"Updated item {item_id}")
        except Exception as e:
            print(f"Error: {e}")

    def do_export(self, arg):
        """Export work items to markdown: export [filename]
        If no filename is provided, defaults to 'work_items.md'
        Example: export my_tasks.md"""
        filename = arg.strip() if arg.strip() else "work_items.md"
        try:
            self.work_system.export_markdown(filename)
            print(f"Successfully exported to {filename}")
        except Exception as e:
            print(f"Error exporting to markdown: {e}")

    def do_quit(self, arg):
        """Quit the program"""
        return True

if __name__ == '__main__':
    WorkSystemCLI().cmdloop()