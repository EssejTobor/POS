from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from typing import List

from .models import WorkItem, ItemType, Priority, ItemStatus

class Display:
    """Handles all display formatting and UI elements using Rich library"""
    
    def __init__(self):
        self.console = Console()

    def print_items(self, items: List[WorkItem]):
        """
        Creates a formatted table showing:
        - Item ID
        - Goal
        - Title
        - Type
        - Priority
        - Status
        - Creation date
        - Description
        """
        if not items:
            self.console.print("[bold yellow]No items to display.[/bold yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Goal", style="blue")
        table.add_column("Title", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Priority", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Created", style="white")
        table.add_column("Description", style="white")
        
        for item in items:
            # Set priority color
            priority_color = {
                Priority.HI: "bright_red",
                Priority.MED: "yellow",
                Priority.LOW: "green"
            }.get(item.priority, "white")
            
            # Set status color
            status_color = {
                ItemStatus.COMPLETED: "green",
                ItemStatus.IN_PROGRESS: "yellow",
                ItemStatus.NOT_STARTED: "red"
            }.get(item.status, "white")
            
            table.add_row(
                item.id,
                item.goal,
                item.title,
                item.item_type.value,
                f"[{priority_color}]{item.priority.name}[/{priority_color}]",
                f"[{status_color}]{item.status.value}[/{status_color}]",
                item.created_at.strftime('%Y-%m-%d %H:%M'),
                item.description
            )
        self.console.print(table)

    def print_tree(self, items: List[WorkItem], goals: List[str]):
        """Display a hierarchical tree view of goals and their work items"""
        tree = Tree("[bold magenta]Work System Overview[/bold magenta]")
        
        if not goals:
            self.console.print("[bold yellow]No goals/items to display.[/bold yellow]")
            return
        
        for goal in goals:
            goal_branch = tree.add(f"[bold blue]{goal.upper()}[/bold blue]")
            goal_items = [item for item in items if item.goal.lower() == goal.lower()]
            
            # Group items by type
            for item_type in ItemType:
                type_items = [item for item in goal_items if item.item_type == item_type]
                if not type_items:
                    continue
                    
                type_branch = goal_branch.add(f"[bold yellow]{item_type.name}[/bold yellow]")
                
                # Group by priority
                for priority in reversed(list(Priority)):
                    priority_items = [item for item in type_items if item.priority == priority]
                    if not priority_items:
                        continue
                        
                    priority_color = {
                        Priority.HI: "bright_red",
                        Priority.MED: "yellow",
                        Priority.LOW: "green"
                    }.get(priority, "white")
                    
                    priority_branch = type_branch.add(f"[{priority_color}]{priority.name} Priority[/{priority_color}]")
                    
                    for item in priority_items:
                        status_color = {
                            ItemStatus.COMPLETED: "green",
                            ItemStatus.IN_PROGRESS: "yellow",
                            ItemStatus.NOT_STARTED: "red"
                        }.get(item.status, "white")
                        
                        priority_branch.add(
                            f"[cyan]{item.id}[/cyan] - {item.title} "
                            f"([{status_color}]{item.status.value}[/{status_color}])"
                        )
        
        self.console.print(tree)

    def print_success(self, message: str):
        """Print a success message"""
        self.console.print(f"[bold green]{message}[/bold green]")

    def print_error(self, message: str):
        """Print an error message"""
        self.console.print(f"[bold red]Error:[/bold red] {message}")

    def print_warning(self, message: str):
        """Print a warning message"""
        self.console.print(f"[bold yellow]{message}[/bold yellow]") 