import cmd
from rich.prompt import Prompt

from .models import ItemType, ItemStatus, Priority
from .storage import WorkSystem
from .display import Display

class WorkSystemCLI(cmd.Cmd):
    """
    Command-line interface providing:
    - Interactive command prompt
    - Rich text formatting for output
    - Command history
    - Help system
    
    Commands:
    - add: Create new items
    - list: View items with various filters
    - update: Modify existing items
    - export: Generate markdown report
    - quit: Exit the program
    """
    intro = "[bold green]Welcome to the Work System CLI![/bold green] Type help or ? to list commands.\n"
    prompt = "(work) "

    def __init__(self):
        super().__init__()
        self.work_system = WorkSystem()
        self.display = Display()

    def do_add(self, arg):
        """
        Adds new work items. Example usage:
        add ProjectA-t-HI-Setup Database-Create initial schema
        
        Format:
        add <goal>-<type>-<priority>-<title>-<description>
        """
        try:
            parts = arg.split('-', 4)
            if len(parts) < 5:
                self.display.print_error("Not enough parts. Format: goal-type-priority-title-description")
                return

            goal, type_, priority, title, description = parts
            
            item = self.work_system.add_item(
                goal=goal.strip(),
                item_type=ItemType(type_.strip()),
                priority=Priority[priority.strip().upper()],
                title=title.strip(),
                description=description.strip()
            )
            self.display.print_success(f"Added: {item.title} (ID: {item.id})")
        except Exception as e:
            self.display.print_error(str(e))

    def do_list(self, arg):
        """
        Lists items with various filters. Examples:
        - list ProjectA          (all items for goal)
        - list ProjectA priority (sorted by priority)
        - list ProjectA id       (sorted by creation)
        - list incomplete        (all incomplete items)
        - list all              (everything)
        """
        args = arg.lower().strip().split()
        
        try:
            if not args:
                self.display.print_warning("Please specify what to list. Type 'help list' for options.")
                return

            if args[0] == 'incomplete':
                self.display.print_items(self.work_system.get_incomplete_items())
                return

            if args[0] == 'all':
                goals = self.work_system.get_all_goals()
                for goal in goals:
                    items = self.work_system.get_items_by_goal(goal)
                    if items:
                        self.display.print_items(items)
                return

            goal = args[0]
            
            if len(args) > 1 and args[1] == 'priority':
                items = self.work_system.get_items_by_goal_priority(goal)
                self.display.print_items(items)
                return

            if len(args) > 1 and args[1] == 'id':
                items = self.work_system.get_items_by_goal_id(goal)
                self.display.print_items(items)
                return

            items = self.work_system.get_items_by_goal(goal)
            if items:
                self.display.print_items(items)
            else:
                self.display.print_warning(f"No items found for goal: {goal}")

        except Exception as e:
            self.display.print_error(str(e))

    def do_update(self, arg):
        """
        Handles status updates for existing items.
        Simple format: update-<id>-<new_status>
        Extended format: update-<id>-<status|priority>-<new_value>
        """
        try:
            parts = arg.split('-')
            
            if len(parts) == 3:
                item_id, new_status = parts[1:]
                self.work_system.update_item_status(item_id.strip(), ItemStatus(new_status.strip()))
                self.display.print_success(f"Updated item {item_id}")
                return
            
            if len(parts) == 4:
                item_id, field, value = parts[1:]
                if field.strip() == 'status':
                    self.work_system.update_item_status(item_id.strip(), ItemStatus(value.strip()))
                elif field.strip() == 'priority':
                    self.work_system.update_item_priority(item_id.strip(), Priority[value.strip().upper()])
                self.display.print_success(f"Updated item {item_id}")
                return
                
            self.display.print_error("Format should be: update-id-status or update-id-field-value")
            
        except Exception as e:
            self.display.print_error(str(e))

    def do_export(self, arg):
        """
        Exports work items to a markdown file for external viewing.
        Organizes items by goal, type, and priority.
        """
        filename = arg.strip() if arg.strip() else "work_items.md"
        try:
            self.work_system.export_markdown(filename)
            self.display.print_success(f"Successfully exported to {filename}")
        except Exception as e:
            self.display.print_error(f"Error exporting to markdown: {e}")

    def do_tree(self, arg):
        """
        Display a hierarchical tree view of goals and their work items.
        Shows items organized by goal with color-coded status and priority.
        """
        goals = self.work_system.get_all_goals()
        items = [item for item in self.work_system.items.values()]
        self.display.print_tree(items, goals)

    def do_quit(self, arg):
        """Quit the program"""
        self.display.print_success("Goodbye!")
        return True

# Entry point for the CLI application
def main():
    WorkSystemCLI().cmdloop()

if __name__ == '__main__':
    main() 