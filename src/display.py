"""Utilities for displaying information to the user.

This module primarily relies on the :mod:`rich` package.  When ``rich`` is
not available (for example in minimal test environments) we fall back to
very small stub classes so that the rest of the application continues to
function.  The stubs simply print plain text tables and trees.
"""

from typing import List

try:  # pragma: no cover - import helper
    from rich.console import Console
    from rich.table import Table
    from rich.tree import Tree
except ModuleNotFoundError:  # pragma: no cover - executed only when rich missing
    class Console:
        def __init__(self, *_, **__):
            pass

        def print(self, *args, **kwargs):
            print(*args)

    class Table:
        def __init__(self, *_, **__):
            self.headers = []
            self.rows = []

        def add_column(self, name: str, **__):
            self.headers.append(name)

        def add_row(self, *values: str):
            self.rows.append(values)

        def __str__(self) -> str:
            lines = [" | ".join(self.headers)]
            for row in self.rows:
                lines.append(" | ".join(row))
            return "\n".join(lines)

    class Tree:
        def __init__(self, label: str):
            self.label = label
            self.children: List["Tree"] = []

        def add(self, label: str):
            child = Tree(label)
            self.children.append(child)
            return child

        def __str__(self) -> str:
            lines: List[str] = []

            def _walk(node: "Tree", prefix: str = ""):
                lines.append(prefix + node.label)
                for child in node.children:
                    _walk(child, prefix + "  ")

            _walk(self)
            return "\n".join(lines)

from .models import WorkItem, ItemType, Priority, ItemStatus

class Display:
    """Handles all display formatting and UI elements using Rich library"""
    
    def __init__(self):
        self.console = Console(force_terminal=True)

    def print_items(self, items: List[WorkItem]):
        """Pretty-print a list of work items as a table"""
        if not items:
            self.print_warning("No items to display.")
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
            
            # Set type styling - add special highlight for thoughts
            type_display = item.item_type.value
            if item.item_type == ItemType.THOUGHT:
                type_display = f"[bold cyan]{type_display}[/bold cyan]"
            
            # Set title styling - add special highlight for thoughts
            title_display = item.title
            if item.item_type == ItemType.THOUGHT:
                title_display = f"[italic]{title_display}[/italic]"
            
            table.add_row(
                item.id,
                item.goal,
                title_display,
                type_display,
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
                
                # Use a special styling for THOUGHT type
                if item_type == ItemType.THOUGHT:
                    type_branch = goal_branch.add(f"[bold cyan]{item_type.name}[/bold cyan]")
                else:
                    type_branch = goal_branch.add(f"[bold yellow]{item_type.name}[/bold yellow]")
                
                # Sort items by priority (high to low)
                sorted_items = sorted(type_items, key=lambda x: (x.priority.value, x.created_at), reverse=True)
                
                # Group by priority
                for priority in reversed(list(Priority)):
                    priority_items = [item for item in sorted_items if item.priority == priority]
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

    def print(self, message: str):
        """Print a formatted message"""
        self.console.print(message)

    def print_link_tree(self, items: dict, root_id: str = None, max_depth: int = 5):
        """
        Display a hierarchical tree view of item relationships based on links.
        
        Args:
            items: Dictionary mapping item IDs to (item, links) tuples
            root_id: ID of item to use as root (if None, creates a tree for each unlinked item)
            max_depth: Maximum depth to traverse to prevent infinite loops with cycles
        """
        # If no items, display error
        if not items:
            self.print_warning("No items to display in link tree.")
            return
            
        # Create the main tree
        main_tree = Tree("[bold magenta]Item Relationship Tree[/bold magenta]")
        
        # Track visited items to handle cycles
        visited = set()
        
        # Function to recursively build the tree
        def build_tree(tree_node, item_id, depth=0):
            # Prevent infinite recursion due to cycles
            if depth > max_depth or item_id in visited:
                if item_id in visited:
                    # Mark as a cycle reference
                    tree_node.add(f"[dim cyan]{item_id}[/dim cyan] [dim](cycle reference)[/dim]")
                return

            # Mark as visited to handle cycles
            visited.add(item_id)
            
            # Get the item and its links
            if item_id not in items:
                tree_node.add(f"[red]Item not found: {item_id}[/red]")
                # Remove from visited to avoid stale entries if item is missing
                visited.discard(item_id)
                return
                
            item, links = items[item_id]
            
            # Define colors for different link types
            link_type_colors = {
                "references": "blue",
                "evolves-from": "green",
                "inspired-by": "yellow",
                "parent-child": "magenta"
            }
            
            # Format the item node based on its type
            item_title = f"[cyan]{item.id}[/cyan] - "
            
            if item.item_type == ItemType.THOUGHT:
                item_title += f"[bold cyan]{item.title}[/bold cyan]"
            else:
                item_title += f"{item.title}"
                
            item_title += f" ([dim]{item.item_type.value}[/dim])"
            
            # Create the item node
            item_node = tree_node.add(item_title)
            
            # Add outgoing links if any
            if links['outgoing']:
                outgoing_node = item_node.add("[bold]Outgoing Links:[/bold]")
                
                # Group by link type
                links_by_type = {}
                for link in links['outgoing']:
                    link_type = link['link_type']
                    if link_type not in links_by_type:
                        links_by_type[link_type] = []
                    links_by_type[link_type].append(link)
                
                # Process each link type
                for link_type, type_links in links_by_type.items():
                    # Get color for this link type
                    color = link_type_colors.get(link_type, "white")
                    
                    # Create a node for this link type
                    type_node = outgoing_node.add(f"[{color}]{link_type}[/{color}] ({len(type_links)})")
                    
                    # Add each link target and recursively build its tree
                    for link in type_links:
                        target_id = link['target_id']
                        if target_id in items:
                            if depth < max_depth:
                                target_item = items[target_id][0]
                                target_node = type_node.add(
                                    f"[cyan]{target_id}[/cyan] - {target_item.title} "
                                    f"([dim]{target_item.item_type.value}[/dim])"
                                )
                                build_tree(target_node, target_id, depth + 1)
                        else:
                            type_node.add(f"[red]Target not found: {target_id}[/red]")
            
            # Remove from visited when backtracking
            visited.remove(item_id)
        
        # If a root is specified, build tree from that item
        if root_id:
            if root_id in items:
                item, _ = items[root_id]
                build_tree(main_tree, root_id)
            else:
                self.print_error(f"Root item not found: {root_id}")
                return
        else:
            # Find all items that don't have incoming links (potential roots)
            root_items = []
            for item_id, (item, links) in items.items():
                if not links['incoming']:
                    root_items.append(item_id)
            
            # If no roots found, use the first few items as roots
            if not root_items and items:
                root_items = list(items.keys())[:5]  # Limit to first 5 to avoid huge trees
                
            # Build a tree for each root item
            for root_id in root_items:
                item, _ = items[root_id]
                # Skip if already visited (could happen if we're using arbitrary items as roots)
                if root_id in visited:
                    continue
                build_tree(main_tree, root_id)
                
        # Print the tree
        self.console.print(main_tree) 