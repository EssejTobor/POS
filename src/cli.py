import cmd
from datetime import datetime
from pathlib import Path

# The CLI uses the ``rich`` library for nicer output. However, the
# execution environment for the unit tests might not have ``rich``
# installed.  To make the CLI usable (and importable) without the
# optional dependency we fall back to very small stub implementations
# when ``rich`` is unavailable.
try:  # pragma: no cover - small import helper
    from rich.prompt import Prompt as RichPrompt  # type: ignore
    from rich.table import Table as RichTable  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed only on minimal envs

    class Prompt:  # minimal replacement used in tests
        @staticmethod
        def ask(text: str) -> str:
            return input(text)

    class Table:
        def __init__(self, *_, **__):
            self.headers = []
            self.rows = []

        def add_column(self, name: str, **__):
            self.headers.append(name)

        def add_row(self, *values: str):
            self.rows.append(values)

        def __str__(self) -> str:  # simple textual representation
            lines = [" | ".join(self.headers)]
            for row in self.rows:
                lines.append(" | ".join(row))
            return "\n".join(lines)

else:
    Prompt = RichPrompt  # type: ignore
    Table = RichTable  # type: ignore

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from pydantic import ValidationError
else:
    try:
        from pydantic import ValidationError  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - allow running without pydantic

        class ValidationError(Exception):
            """Fallback when ``pydantic`` is not installed."""

            pass


from .backup import BackupManager
from .display import Display
from .migrate import MigrationManager
from .models import ItemStatus, ItemType, Priority
from .schemas import AddItemInput, AddThoughtInput, UpdateItemInput
from .storage import WorkSystem

try:
    import textual  # noqa: F401
except Exception:  # pragma: no cover - textual not installed
    TEXTUAL_AVAILABLE = False
else:  # pragma: no cover - textual installed
    TEXTUAL_AVAILABLE = True


class WorkSystemCLI(cmd.Cmd):
    """
    Command-line interface providing:
    - Interactive command prompt
    - Rich text formatting for output
    - Command history
    - Help system

    Commands:
    - add: Create new items (including thoughts with optional linking)
    - list: View items with various filters
    - list_thoughts: View all thought items
    - link: Create a link between two work items
    - unlink: Remove a link between two work items
    - link_tree: Display a hierarchical view of item relationships
    - tree: View items organized by goal, type, and priority
    - update: Modify existing items
    - export: Generate markdown report
    - form: Launch Textual UI form for adding items
    - tui: Launch the Textual dashboard (use ``--tab`` to select a starting tab)
    - tui_list: Launch Textual UI list view
    - quit: Exit the program
    - dedupe: Scan for and merge duplicate work items
    - optimize: Optimize the database storage
    - backup: Create a backup of the database
    - restore: Restore database from a backup file
    - list_backups: List all available backups
    - cleanup_backups: Remove old backups, keeping the most recent ones
    - export_json: Export database to JSON format
    - migrate: Migrate data from JSON to SQLite database
    - tag: Add a tag to an item
    - untag: Remove a tag from an item
    - list_by_tag: List items that share a tag
    """

    prompt = "(work) "

    def __init__(self):
        super().__init__()
        self.work_system = WorkSystem()
        self.display = Display()
        self.backup_manager = BackupManager()
        self.migration_manager = MigrationManager()
        # Display welcome message using rich
        self.display.console.print(
            "[bold green]Welcome to the Work System CLI![/bold green]"
        )
        self.display.console.print(
            "Type [yellow]help[/yellow] or [yellow]?[/yellow] to list commands.\n"
        )

    def do_add(self, arg):
        """
        Adds new work items, including thoughts. Example usage:
        add ProjectA-t-HI-Setup Database-Create initial schema
        add ThinkingProcess-th-MED-Initial Concept-My first thought about the project
        add ThinkingProcess-th-MED-Follow-up-Building on previous idea --link-to abc123
        add ThinkingProcess-th-MED-Related-Another perspective --link-to abc123 --link-type inspired-by

        Format:
        add <goal>-<type>-<priority>-<title>-<description> [--link-to <item_id>] [--link-type <type>]

        Types:
        - t (task): Regular tasks - day-to-day work items
        - l (learning): Learning-related items - educational goals
        - r (research): Research-related items - investigation tasks
        - th (thought): Thought items - ideas and concepts to track

        Priority: HI, MED, LOW

        Link types (when using --link-to):
        - references (default): This item references or mentions another item
        - evolves-from: This thought is an evolution of another item
        - inspired-by: This thought was inspired by but may diverge from another item
        - parent-child: Hierarchical relationship
        """
        try:
            # Validate input
            input_data = AddItemInput.parse_input(arg)

            # Create item
            item = self.work_system.add_item(
                goal=input_data.goal,
                item_type=ItemType(input_data.type_),
                priority=Priority[input_data.priority],
                title=input_data.title,
                description=input_data.description,
            )

            # Handle optional linking
            if input_data.link_to:
                # Verify the linked item exists
                target_item = self.work_system.items.get(input_data.link_to)
                if target_item:
                    # Create the link with appropriate type
                    success = self.work_system.add_link(
                        item.id, input_data.link_to, input_data.link_type
                    )
                    if success:
                        self.display.print_success(
                            f"Added: {item.title} (ID: {item.id})\n"
                            f"Linked to: {target_item.title} (ID: {target_item.id}) with type: {input_data.link_type}"
                        )
                    else:
                        self.display.print_warning(
                            f"Added: {item.title} (ID: {item.id})\n"
                            f"Failed to create link to item (ID: {input_data.link_to})"
                        )
                else:
                    self.display.print_warning(
                        f"Added: {item.title} (ID: {item.id})\n"
                        f"Link target not found: {input_data.link_to}"
                    )
            else:
                self.display.print_success(f"Added: {item.title} (ID: {item.id})")

        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = error["loc"][0]
                message = error["msg"]
                errors.append(f"{field}: {message}")
            self.display.print_error("\n".join(errors))
        except Exception as e:
            self.display.print_error(str(e))

    def do_add_thought(self, arg):
        """Add a thought item with optional parent linking."""
        try:
            input_data = AddThoughtInput.parse_input(arg)

            item = self.work_system.add_item(
                goal=input_data.goal,
                item_type=ItemType.THOUGHT,
                priority=Priority.MED,
                title=input_data.title,
                description=input_data.description,
            )

            if input_data.parent_id:
                self.work_system.add_link(
                    item.id, input_data.parent_id, input_data.link_type
                )

            self.display.print_success(f"Added: {item.title} (ID: {item.id})")

        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = error["loc"][0]
                message = error["msg"]
                errors.append(f"{field}: {message}")
            self.display.print_error("\n".join(errors))
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
        - list thoughts         (all thought items)
        """
        args = arg.lower().strip().split()

        try:
            if not args:
                self.display.print_warning(
                    "Please specify what to list. Type 'help list' for options."
                )
                return

            if args[0] == "incomplete":
                self.display.print_items(self.work_system.get_incomplete_items())
                return

            if args[0] == "all":
                goals = self.work_system.get_all_goals()
                for goal in goals:
                    items = self.work_system.get_items_by_goal(goal)
                    if items:
                        self.display.print_items(items)
                return

            if args[0] == "thoughts":
                thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
                if thoughts:
                    self.display.print_items(thoughts)
                else:
                    self.display.print_warning("No thought items found.")
                return

            goal = args[0]

            if len(args) > 1 and args[1] == "priority":
                items = self.work_system.get_items_by_goal_priority(goal)
                self.display.print_items(items)
                return

            if len(args) > 1 and args[1] == "id":
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

    def do_list_thoughts(self, arg):
        """
        List all thought items, optionally filtered by goal.

        Usage:
        - list_thoughts           (all thoughts)
        - list_thoughts ProjectA  (thoughts for specific goal)
        """
        args = arg.lower().strip().split()
        try:
            if not args:
                # List all thoughts
                thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
                if thoughts:
                    self.display.print_items(thoughts)
                else:
                    self.display.print_warning("No thought items found.")
                return

            # Filter thoughts by goal
            goal = args[0]
            all_thoughts = self.work_system.get_items_by_type(ItemType.THOUGHT)
            goal_thoughts = [t for t in all_thoughts if t.goal.lower() == goal.lower()]

            if goal_thoughts:
                self.display.print_items(goal_thoughts)
            else:
                self.display.print_warning(f"No thought items found for goal: {goal}")

        except Exception as e:
            self.display.print_error(f"Error listing thoughts: {str(e)}")

    def do_search_thoughts(self, arg):
        """Search thought items by keyword. Usage: search_thoughts <text> [goal]"""
        args = arg.strip().split()
        if not args:
            self.display.print_error("Please provide search text")
            return

        search_text = args[0]
        goal = args[1] if len(args) > 1 else None

        try:
            thoughts = self.work_system.search_thoughts(search_text, goal=goal)
            if thoughts:
                self.display.print_items(thoughts)
            else:
                self.display.print_warning("No thought items found.")
        except Exception as e:
            self.display.print_error(f"Error searching thoughts: {str(e)}")

    def do_update(self, arg):
        """
        Handles status updates for existing items.
        Simple format: update-<id>-<new_status>
        Extended format: update-<id>-<status|priority>-<new_value>
        """
        try:
            # Validate input
            input_data = UpdateItemInput.parse_input(arg)

            if not input_data.field:  # Simple status update
                self.work_system.update_item_status(
                    input_data.item_id, ItemStatus(input_data.value)
                )
            elif input_data.field == "status":
                self.work_system.update_item_status(
                    input_data.item_id, ItemStatus(input_data.value)
                )
            elif input_data.field == "priority":
                self.work_system.update_item_priority(
                    input_data.item_id, Priority[input_data.value.upper()]
                )

            self.display.print_success(f"Updated item {input_data.item_id}")

        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = error["loc"][0]
                message = error["msg"]
                errors.append(f"{field}: {message}")
            self.display.print_error("\n".join(errors))
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
        try:
            goals = self.work_system.get_all_goals()
            items = self.work_system.get_filtered_items()  # Using new method
            self.display.print_tree(items, goals)
        except Exception as e:
            self.display.print_error(f"Error displaying tree: {str(e)}")

    def do_link_tree(self, arg):
        """
        Display a hierarchical tree view of item relationships.
        Shows how items are linked to each other with color-coded relationship types.

        Usage:
        link_tree                 (shows all items with their links)
        link_tree <item_id>       (shows tree starting from specific item)
        link_tree --thoughts      (focuses on thought items and their links)
        link_tree <item_id> <max_depth>  (limits the tree depth to avoid large outputs)

        Examples:
        link_tree abc123         (shows relationships starting from item abc123)
        link_tree --thoughts     (shows only thoughts and their relationships)
        link_tree abc123 3       (shows up to 3 levels of links from item abc123)
        """
        try:
            # Parse arguments
            args = arg.strip().split()

            # Default settings
            root_id = None
            max_depth = 5
            only_thoughts = False

            # Process arguments
            if args:
                if args[0] == "--thoughts":
                    only_thoughts = True
                elif args[0].startswith("--"):
                    self.display.print_error(f"Unknown option: {args[0]}")
                    return
                else:
                    root_id = args[0]

                    # Check if max_depth is specified
                    if len(args) > 1:
                        try:
                            max_depth = int(args[1])
                            if max_depth <= 0:
                                self.display.print_error(
                                    "Maximum depth must be greater than 0"
                                )
                                return
                        except ValueError:
                            self.display.print_error(
                                f"Invalid maximum depth: {args[1]}"
                            )
                            return

            # Get all items or filter for thoughts
            if only_thoughts:
                all_items = self.work_system.get_items_by_type(ItemType.THOUGHT)
                item_ids = [item.id for item in all_items]
            else:
                # Get all items
                all_items = list(self.work_system.items.values())
                item_ids = list(self.work_system.items.keys())

            # Display a message about what we're showing
            if root_id:
                if root_id not in self.work_system.items:
                    self.display.print_error(f"Item not found: {root_id}")
                    return
                item = self.work_system.items[root_id]
                self.display.print_success(
                    f"Displaying relationship tree for: {item.title} (ID: {root_id})"
                )
            elif only_thoughts:
                self.display.print_success(
                    f"Displaying relationships for {len(all_items)} thought items"
                )
            else:
                self.display.print_success(
                    f"Displaying relationships for {len(all_items)} items"
                )

            # Get links for all items and build a dictionary of items with their links
            items_with_links = {}
            for item_id in item_ids:
                links = self.work_system.get_links(item_id)
                items_with_links[item_id] = (self.work_system.items[item_id], links)

            # Print the link tree
            self.display.print_link_tree(items_with_links, root_id, max_depth)

        except Exception as e:
            self.display.print_error(f"Error displaying link tree: {str(e)}")

    def do_dedupe(self, arg):
        """
        Scans for and merges duplicate work items.
        Usage: dedupe
        """
        try:
            merged_pairs = self.work_system.merge_duplicates()

            if not merged_pairs:
                self.display.print_success("No duplicates found!")
                return

            self.display.print_success(
                f"Found and merged {len(merged_pairs)} duplicate pairs:"
            )

            for kept_item, removed_item in merged_pairs:
                self.display.print(
                    f"[yellow]Merged:[/yellow] {removed_item.id} -> {kept_item.id}\n"
                    f"  Title: {kept_item.title}\n"
                    f"  Type: {kept_item.item_type.value}\n"
                    f"  Priority: {kept_item.priority.name}\n"
                )

        except Exception as e:
            self.display.print_error(str(e))

    def do_optimize(self, arg):
        """
        Optimize the database storage
        """
        try:
            self.work_system.optimize_database()
            self.display.print_success("Database optimized successfully")
        except Exception as e:
            self.display.print_error(f"Error optimizing database: {str(e)}")

    def do_backup(self, arg):
        """
        Create a backup of the database.
        Usage: backup [note]
        Example: backup pre_update
        """
        try:
            note = arg.strip() if arg.strip() else None
            backup_path = self.work_system.backup_manager.create_backup(note)
            self.display.print_success(f"Created backup at: {backup_path}")
        except Exception as e:
            self.display.print_error(f"Backup failed: {str(e)}")

    def do_restore(self, arg):
        """
        Restore database from a backup.
        Usage: restore <backup_filename>
        Example: restore work_items_20250222_123456.db
        """
        if not arg:
            self.display.print_error("Please specify backup file to restore")
            return

        try:
            backup_path = self.work_system.backup_manager.backup_dir / arg.strip()
            self.work_system.backup_manager.restore_backup(backup_path)
            self.work_system._refresh_cache()  # Refresh cache after restore
            self.display.print_success("Database restored successfully")
        except Exception as e:
            self.display.print_error(f"Restore failed: {str(e)}")

    def do_list_backups(self, arg):
        """
        List all available backups.
        Usage: list_backups
        """
        try:
            backups = self.work_system.backup_manager.list_backups()
            if not backups:
                self.display.print_warning("No backups found")
                return

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Backup File", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Created", style="yellow")

            for backup in backups:
                size_mb = backup.stat().st_size / (1024 * 1024)
                created = datetime.fromtimestamp(backup.stat().st_mtime)
                table.add_row(
                    str(backup.name),
                    f"{size_mb:.2f} MB",
                    created.strftime("%Y-%m-%d %H:%M:%S"),
                )

            self.display.console.print(table)
        except Exception as e:
            self.display.print_error(f"Error listing backups: {str(e)}")

    def do_cleanup_backups(self, arg):
        """Remove old backups, keeping only the most recent ones.

        Usage: cleanup_backups [max_to_keep=5]

        Examples:
          cleanup_backups        # Keeps the 5 most recent backups
          cleanup_backups 10     # Keeps the 10 most recent backups
        """
        try:
            max_to_keep = 5  # Default value
            if arg:
                max_to_keep = int(arg)

            if max_to_keep < 1:
                self.display.print_error("Max backups to keep must be at least 1")
                return

            count = self.backup_manager.cleanup_old_backups(max_to_keep)
            self.display.console.print(
                f"[green]Removed {count} old backup(s), keeping {max_to_keep} most recent.[/green]"
            )
        except ValueError:
            self.display.print_error(f"Invalid number: {arg}")

    def do_export_json(self, arg):
        """
        Export database to JSON format.
        Usage: export_json [output_path]
        Example: export_json my_backup.json
        """
        try:
            output_path = Path(arg.strip()) if arg.strip() else None
            json_path = self.work_system.backup_manager.export_to_json(output_path)
            self.display.print_success(f"Exported database to: {json_path}")
        except Exception as e:
            self.display.print_error(f"Export failed: {str(e)}")

    def do_migrate(self, arg):
        """
        Migrate data from JSON to SQLite database
        Usage: migrate [json_path]
        """
        try:
            json_path = arg.strip() if arg else "work_items.json"
            self.migration_manager = MigrationManager(json_path=json_path)

            processed_count, errors = self.migration_manager.migrate_json_to_sqlite()

            if errors:
                self.display.print_error("Migration completed with errors:")
                for error in errors:
                    self.display.print_error(f"- {error}")
            else:
                self.display.print_success(
                    f"Successfully migrated {processed_count} items"
                )

            # Refresh work system to load migrated data
            self.work_system = WorkSystem()

        except Exception as e:
            self.display.print_error(f"Migration failed: {str(e)}")

    def do_link(self, arg):
        """
        Create a link between two work items.

        Usage:
        link <source_id> <target_id> [link_type]

        Examples:
        link abc123 def456             (creates link with default 'references' type)
        link abc123 def456 evolves-from (creates link with 'evolves-from' type)

        Link types:
        - references: Basic connection between items (default)
        - evolves-from: Shows thought evolution
        - inspired-by: Influence without direct evolution
        - parent-child: Hierarchical relationship
        """
        try:
            # Parse arguments
            args = arg.strip().split()
            if len(args) < 2:
                self.display.print_error(
                    "Please provide source and target IDs. Type 'help link' for usage."
                )
                return

            source_id = args[0]
            target_id = args[1]
            link_type = args[2] if len(args) > 2 else "references"

            # Validate IDs exist
            if source_id not in self.work_system.items:
                self.display.print_error(f"Source item not found: {source_id}")
                return

            if target_id not in self.work_system.items:
                self.display.print_error(f"Target item not found: {target_id}")
                return

            # Validate link type
            valid_link_types = [
                "references",
                "evolves-from",
                "inspired-by",
                "parent-child",
            ]
            if link_type not in valid_link_types:
                self.display.print_error(
                    f"Invalid link type: {link_type}\n"
                    f"Valid types: {', '.join(valid_link_types)}"
                )
                return

            # Create the link
            success = self.work_system.add_link(source_id, target_id, link_type)

            if success:
                source_item = self.work_system.items[source_id]
                target_item = self.work_system.items[target_id]

                self.display.print_success(
                    f"Link created successfully:\n"
                    f"  Source: {source_item.title} (ID: {source_id})\n"
                    f"  Target: {target_item.title} (ID: {target_id})\n"
                    f"  Type: {link_type}"
                )
            else:
                self.display.print_error(
                    "Failed to create link. The link might already exist."
                )

        except Exception as e:
            self.display.print_error(f"Error creating link: {str(e)}")

    def do_unlink(self, arg):
        """
        Remove a link between two work items.

        Usage:
        unlink <source_id> <target_id>

        Example:
        unlink abc123 def456  (removes any link from abc123 to def456)
        """
        try:
            # Parse arguments
            args = arg.strip().split()
            if len(args) != 2:
                self.display.print_error(
                    "Please provide source and target IDs. Type 'help unlink' for usage."
                )
                return

            source_id = args[0]
            target_id = args[1]

            # Validate IDs exist
            if source_id not in self.work_system.items:
                self.display.print_error(f"Source item not found: {source_id}")
                return

            if target_id not in self.work_system.items:
                self.display.print_error(f"Target item not found: {target_id}")
                return

            # Remove the link
            success = self.work_system.remove_link(source_id, target_id)

            if success:
                source_item = self.work_system.items[source_id]
                target_item = self.work_system.items[target_id]

                self.display.print_success(
                    f"Link removed successfully:\n"
                    f"  Source: {source_item.title} (ID: {source_id})\n"
                    f"  Target: {target_item.title} (ID: {target_id})"
                )
            else:
                self.display.print_error("No link found between the specified items.")

        except Exception as e:
            self.display.print_error(f"Error removing link: {str(e)}")

    def do_tag(self, arg):
        """Add a tag to an item. Usage: tag <item_id> <tag>"""
        parts = arg.strip().split()
        if len(parts) != 2:
            self.display.print_error("Usage: tag <item_id> <tag>")
            return
        item_id, tag = parts
        if item_id not in self.work_system.items:
            self.display.print_error(f"Item not found: {item_id}")
            return
        if self.work_system.add_tag_to_item(item_id, tag):
            self.display.print_success(f"Tag '{tag}' added to {item_id}")
        else:
            self.display.print_error("Failed to add tag (maybe duplicate)")

    def do_untag(self, arg):
        """Remove a tag from an item. Usage: untag <item_id> <tag>"""
        parts = arg.strip().split()
        if len(parts) != 2:
            self.display.print_error("Usage: untag <item_id> <tag>")
            return
        item_id, tag = parts
        if item_id not in self.work_system.items:
            self.display.print_error(f"Item not found: {item_id}")
            return
        if self.work_system.remove_tag_from_item(item_id, tag):
            self.display.print_success(f"Tag '{tag}' removed from {item_id}")
        else:
            self.display.print_error("Tag not found")

    def do_list_by_tag(self, arg):
        """List items that have a specific tag. Usage: list_by_tag <tag>"""
        tag = arg.strip()
        if not tag:
            self.display.print_error("Usage: list_by_tag <tag>")
            return
        items = self.work_system.get_items_by_tag(tag)
        if items:
            self.display.print_items(items)
        else:
            self.display.print_warning(f"No items found with tag: {tag}")

    def do_quit(self, arg):
        """Quit the program"""
        self.display.print_success("Goodbye!")
        return True

    def do_help(self, arg):
        """List available commands with help text."""
        if arg:
            # Show help for specific command
            try:
                func = getattr(self, "help_" + arg)
                func()
            except AttributeError:
                try:
                    doc = getattr(self, "do_" + arg).__doc__
                    if doc:
                        self.display.console.print(
                            f"\n[yellow]Help for[/yellow] [blue]{arg}[/blue]:"
                        )
                        self.display.console.print(f"{doc}\n")
                    else:
                        self.display.print_error(f"No help for {arg}")
                except AttributeError:
                    self.display.print_error(f"No command '{arg}'")
        else:
            # Show command list
            self.display.console.print(
                "\n[yellow]Documented commands[/yellow] (type [yellow]help[/yellow] [blue]<topic>[/blue]):"
            )
            self.display.console.print("=" * 40)

            cmds = []
            for name in self.get_names():
                if name[:3] == "do_" and name != "do_help":
                    cmds.append(name[3:])

            # Format in columns
            max_len = max(map(len, cmds))
            cols = 4
            col_width = max_len + 2

            # Print commands in rows
            cmds.sort()
            for i in range(0, len(cmds), cols):
                row = cmds[i : i + cols]
                line = ""
                for cmd in row:
                    line += f"[blue]{cmd:<{col_width}}[/blue]"
                self.display.console.print(line)

            self.display.console.print()
        return False  # Don't stop the command loop

    def do_form(self, arg):
        """Launch the Textual UI form for adding new items.

        Usage: form

        This launches an interactive form for adding new work items,
        with a more user-friendly interface than command-line input.
        """
        if not TEXTUAL_AVAILABLE:
            self.display.print_error(
                "Textual UI is not available. Please install textual: pip install textual"
            )
            return

        try:
            from .textual_ui import TextualApp

            app = TextualApp(self.work_system, start_tab="new-item-tab")
            app.run()
        except Exception as e:
            self.display.print_error(f"Error launching Textual UI: {str(e)}")

    def do_tui(self, arg):
        """Launch the enhanced Textual dashboard.

        Usage: tui [--tab <new-item|items|link-tree>]

        Opens the dashboard with tabs for adding items, browsing the item list,
        and viewing the link tree.  Use the optional ``--tab`` flag to jump
        directly to a specific tab when the interface starts.
        """
        if not TEXTUAL_AVAILABLE:
            self.display.print_error(
                "Textual UI is not available. Please install textual: pip install textual"
            )
            return

        try:
            from .textual_ui import TextualApp

            args = arg.strip().split()
            start_tab = None
            if args:
                if args[0] in {"--tab", "-t"} and len(args) > 1:
                    tab_arg = args[1].lower()
                else:
                    tab_arg = args[0].lower()
                tab_map = {
                    "new-item": "new-item-tab",
                    "new": "new-item-tab",
                    "items": "items-tab",
                    "list": "items-tab",
                    "link-tree": "link-tree-tab",
                    "tree": "link-tree-tab",
                }
                start_tab = tab_map.get(tab_arg)
                if args[0] in {"--tab", "-t"} and len(args) == 1:
                    self.display.print_error("Please specify a tab after --tab")
                    return
                if args[0] not in {"--tab", "-t"} and start_tab is None:
                    self.display.print_error(f"Unknown option: {args[0]}")
                    return

            app = TextualApp(self.work_system, start_tab=start_tab)
            app.run()
        except Exception as e:
            self.display.print_error(f"Error launching Textual UI: {str(e)}")

    def do_tui_list(self, arg):
        """Launch the Textual UI list view for browsing items.

        Usage: tui_list

        Opens the dashboard directly to the Items tab, allowing for
        filtering and browsing of work items.
        """
        if not TEXTUAL_AVAILABLE:
            self.display.print_error(
                "Textual UI is not available. Please install textual: pip install textual"
            )
            return

        try:
            from .textual_ui import TextualApp

            app = TextualApp(self.work_system, start_tab="items-tab")
            # The app will default to the items tab
            app.run()
        except Exception as e:
            self.display.print_error(f"Error launching Textual UI: {str(e)}")


# Entry point for the CLI application
def main():
    WorkSystemCLI().cmdloop()


if __name__ == "__main__":
    main()
