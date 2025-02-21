# Version 0.010 - Enhanced with rich
# Updated with enhanced listing capabilities

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict
import json
from pathlib import Path
import cmd

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

# Define Enums and Data Classes
class ItemType(Enum):
    TASK = "t"
    LEARNING = "l"
    RESEARCH = "r"

class ItemStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Priority(Enum):
    LOW = 1
    MED = 2
    HI = 3

@dataclass
class WorkItem:
    title: str
    item_type: ItemType
    description: str
    goal: str
    priority: Priority = Priority.MED
    status: ItemStatus = ItemStatus.NOT_STARTED
    id: str = field(default="")  # Will be set by WorkSystem
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
            'goal': self.goal,
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
        self.entry_counts: Dict[str, int] = {}  # Track entries per goal
        self.load_items()

    def generate_id(self, goal: str, item_type: ItemType, priority: Priority) -> str:
        # Get first letter of goal and type
        goal_initial = goal[0].lower()
        type_initial = item_type.value[0].lower()
        
        # Get priority number
        priority_num = priority.value
        
        # Get entry count for this goal
        if goal not in self.entry_counts:
            self.entry_counts[goal] = 0
        self.entry_counts[goal] += 1
        entry_num = self.entry_counts[goal]
        
        # Get current time
        now = datetime.now()
        time_str = str(int(now.strftime("%I"))) + now.strftime("%M%p").lower()
        
        # Combine all parts
        return f"{goal_initial}{type_initial}{priority_num}{entry_num}{time_str}"

    def add_item(self, goal: str, title: str, item_type: ItemType,
                 description: str, priority: Priority = Priority.MED) -> WorkItem:
        try:
            item = WorkItem(
                title=title,
                goal=goal,
                item_type=item_type,
                description=description,
                priority=priority
            )
            # Generate and set the ID
            item.id = self.generate_id(goal, item_type, priority)
            self.items[item.id] = item
            self.save_items()
            return item
        except Exception as e:
            print(f"Error adding item: {e}")
            raise

    def get_items_by_goal(self, goal: str) -> List[WorkItem]:
        return sorted(
            [item for item in self.items.values() if item.goal.lower() == goal.lower()],
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )

    def get_items_by_goal_priority(self, goal: str) -> List[WorkItem]:
        """Get items for a goal, sorted by priority (high to low)"""
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
            # Also save entry counts
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
            
        # Handle both old and new format
        if isinstance(data, dict) and 'items' in data:
            items_dict = data['items']
            self.entry_counts = data.get('entry_counts', {})
        else:
            items_dict = data
            # Reconstruct entry counts from existing items
            self.entry_counts = {}
            
        for _, item_data in items_dict.items():
            # Handle legacy data without 'goal' field
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
            
            # Update entry counts based on existing items
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

class WorkSystemCLI(cmd.Cmd):
    intro = "[bold green]Welcome to the Work System CLI![/bold green] Type help or ? to list commands.\n"
    prompt = "(work) "

    def __init__(self):
        super().__init__()
        self.work_system = WorkSystem()
        self.console = Console()

    def print_items(self, items: List[WorkItem]):
        """Helper method to print items in a table format using rich"""
        if not items:
            self.console.print("[bold yellow]No items to display.[/bold yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Priority", style="red")
        table.add_column("Status", style="blue")
        table.add_column("Created", style="white")
        table.add_column("Description", style="white")
        for item in items:
            table.add_row(
                item.id,
                item.title,
                item.item_type.value,
                item.priority.name,
                item.status.value,
                item.created_at.strftime('%Y-%m-%d %H:%M'),
                item.description
            )
        self.console.print(table)

    def do_add(self, arg):
        """Add a new work item using hyphen-separated format:
    add <goal>-<type>-<priority>-<title>-<description>
Example: add agentsee-t-hi-deploy landing page-Finish landing page content"""
        try:
            parts = arg.split('-', 4)
            if len(parts) < 5:
                self.console.print("[bold red]Error:[/bold red] Not enough parts. Format: goal-type-priority-title-description")
                return

            goal, type_, priority, title, description = parts
            
            item = self.work_system.add_item(
                goal=goal.strip(),
                item_type=ItemType(type_.strip()),
                priority=Priority[priority.strip().upper()],
                title=title.strip(),
                description=description.strip()
            )
            self.console.print(f"[bold green]Added:[/bold green] {item.title} (ID: {item.id})")
        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")

    def do_list(self, arg):
        """
List work items with various filtering options:
  list [goal]                  - List all items for a goal
  list <goal> priority         - List items for goal by priority (high to low)
  list <goal> id               - List items for goal by creation time (newest first)
  list incomplete              - List all incomplete items by priority
  list all                     - List everything
        """
        args = arg.lower().strip().split()
        
        try:
            # Handle empty argument
            if not args:
                self.console.print("[bold yellow]Please specify what to list.[/bold yellow] Type 'help list' for options.")
                return

            # Handle 'list incomplete'
            if args[0] == 'incomplete':
                self.console.rule("[bold red]INCOMPLETE ITEMS (All Goals, By Priority)[/bold red]")
                items = self.work_system.get_incomplete_items()
                self.print_items(items)
                return

            # Handle 'list all'
            if args[0] == 'all':
                goals = self.work_system.get_all_goals()
                for goal in goals:
                    self.console.rule(f"[bold blue]GOAL: {goal.upper()}[/bold blue]")
                    items = self.work_system.get_items_by_goal(goal)
                    self.print_items(items)
                return

            # Handle goal-specific listings
            goal = args[0]
            
            # Handle 'list <goal> priority'
            if len(args) > 1 and args[1] == 'priority':
                self.console.rule(f"[bold blue]GOAL: {goal.upper()} (By Priority)[/bold blue]")
                items = self.work_system.get_items_by_goal_priority(goal)
                self.print_items(items)
                return

            # Handle 'list <goal> id'
            if len(args) > 1 and args[1] == 'id':
                self.console.rule(f"[bold blue]GOAL: {goal.upper()} (By Creation Time)[/bold blue]")
                items = self.work_system.get_items_by_goal_id(goal)
                self.print_items(items)
                return

            # Default: list all items for the goal
            items = self.work_system.get_items_by_goal(goal)
            if items:
                self.console.rule(f"[bold blue]GOAL: {goal.upper()}[/bold blue]")
                self.print_items(items)
            else:
                self.console.print(f"[bold yellow]No items found for goal:[/bold yellow] {goal}")

        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")

    def do_update(self, arg):
        """Update item status or priority using the format:
update <id>-<status|priority>-<new_value>
Example: update at31139pm-status-in_progress"""
        try:
            parts = arg.split('-')
            if len(parts) != 3:
                self.console.print("[bold red]Error:[/bold red] Format should be: id-field-value")
                return
                
            item_id, field, value = parts
            
            if field.strip() == 'status':
                self.work_system.update_item_status(item_id.strip(), ItemStatus(value.strip()))
            elif field.strip() == 'priority':
                self.work_system.update_item_priority(item_id.strip(), Priority[value.strip().upper()])
            self.console.print(f"[bold green]Updated item[/bold green] {item_id}")
        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")

    def do_export(self, arg):
        """Export work items to markdown: export [filename]
If no filename is provided, defaults to 'work_items.md'"""
        filename = arg.strip() if arg.strip() else "work_items.md"
        try:
            self.work_system.export_markdown(filename)
            self.console.print(f"[bold green]Successfully exported to[/bold green] {filename}")
        except Exception as e:
            self.console.print(f"[bold red]Error exporting to markdown:[/bold red] {e}")

    def do_quit(self, arg):
        """Quit the program"""
        self.console.print("[bold magenta]Goodbye![/bold magenta]")
        return True

if __name__ == '__main__':
    WorkSystemCLI().cmdloop()
