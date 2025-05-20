from __future__ import annotations
from src.models import ItemStatus, ItemType, Priority
from src.storage import WorkSystem



from typing import Any, Callable, Dict, List, Optional, Tuple

# Define fallback types for type checking at the top level
ComposeResult = Any
NoMatches = Exception
Coordinate = Tuple[int, int]

try:  # pragma: no cover - Textual is optional
    from textual.app import App, ComposeResult  # type: ignore
    from textual.binding import Binding  # type: ignore
    from textual.containers import Container, Horizontal, Vertical  # type: ignore
    from textual.css.query import NoMatches  # type: ignore
    from textual.coordinate import Coordinate  # type: ignore
    from textual.screen import ModalScreen, Screen  # type: ignore
    from textual.widget import Widget  # type: ignore
    from textual.widgets import Footer  # type: ignore
    from textual.widgets import (
        Button,
        DataTable,
        Header,
        Input,
        Label,
        Select,
        Static,
        TabbedContent,
        TabPane,
        Tree,
    )
    from textual.command import command  # type: ignore
    from textual.suggester import SuggestFromList  # type: ignore

    TEXTUAL_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - fallback stub
    TEXTUAL_AVAILABLE = False
    
    class SuggestFromList:  # type: ignore
        def __init__(self, suggestions=None, case_sensitive=True):
            self.suggestions = suggestions or []
            self.case_sensitive = case_sensitive
    
    class ModalScreen:  # type: ignore
        def __init__(self, *_, **__):
            pass
            
        def dismiss(self):
            pass

    class Coordinate:  # type: ignore
        def __init__(self, row: int = 0, column: int = 0):
            self.row = row
            self.column = column

    class App:  # type: ignore
        def __init__(self, *_, **__):
            pass

        def run(self, *_, **__):
            print("Textual not available")
            
        def exit(self):
            print("Exiting Textual application")
            
        def push_screen(self, screen):
            pass
            
        def pop_screen(self):
            pass

    class Static:  # type: ignore
        def __init__(self, *_, **__):
            pass

    class Binding:  # type: ignore
        def __init__(self, *_, **__):
            pass

    class Container(Widget):  # type: ignore
        def __init__(self, *_, **__):
            super().__init__(*_, **__)

    class Horizontal(Container):
        pass

    class Vertical(Container):
        pass

    class Screen:  # type: ignore
        def __init__(self, *_, **__):
            pass
            
        def query_one(self, selector, selector_type=None):
            return None

    class Widget:  # type: ignore
        def __init__(self, *_, **__):
            self.app = None  # Will be set by the app when mounted
            
        def query_one(self, selector, selector_type=None):
            return None
            
        def add_class(self, class_name):
            pass
            
        def set_timer(self, delay, callback):
            pass
            
        def remove(self):
            pass
            
        def watch(self, widget, attribute, callback):
            pass
            
        def mount(self, widget):
            pass

    class Button(Widget):
        class Pressed:
            def __init__(self, button=None):
                self.button = button

    class DataTable(Widget):
        class CellSelected:
            def __init__(self, value="", coordinate=None):
                self.value = value
                self.coordinate = coordinate or Coordinate(0, 0)
            
        def __init__(self, *_, **__):
            super().__init__(*_, **__)
            self.clear_called = False
            self.columns = []
            
        def add_columns(self, *columns):
            self.columns = [Column(label) for label in columns]
            
        def clear(self):
            self.clear_called = True
            
        def add_row(self, *values):
            pass
            
        def update_cell_at(self, coordinate, value):
            pass
            
        def get_cell_at(self, coordinate):
            return "ITEM-001"  # Fallback dummy value
            
    class Column:
        def __init__(self, label):
            self.label = label

    class Footer(Widget):
        pass

    class Header(Widget):
        def __init__(self, *_, **kwargs):
            super().__init__(*_, **kwargs)
            self.show_clock = kwargs.get("show_clock", False)

    class Input(Widget):
        def __init__(self, *_, **kwargs):
            super().__init__(*_, **kwargs)
            self.value = kwargs.get("value", "")
            self.placeholder = kwargs.get("placeholder", "")

    class Label(Widget):
        def __init__(self, text="", **kwargs):
            super().__init__(**kwargs)
            self.text = text

    class Select(Widget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add value attribute for compatibility
            self.value = kwargs.get("value", None)
            self.options = args[0] if args else []

    class TabPane(Widget):
        def __init__(self, title="", **kwargs):
            super().__init__(**kwargs)
            self.title = title

    class TabbedContent(Widget):
        def __init__(self, *_, **__):
            super().__init__(*_, **__)
            self.active = ""

    class Tree(Widget):
        def __init__(self, label="", **kwargs):
            super().__init__(**kwargs)
            self.root = TreeNode(label)
            
        def expand_all(self):
            pass

    class TreeNode:
        def __init__(self, label=""):
            self.label = label
            self.children = []
            
        def add(self, label):
            node = TreeNode(label)
            self.children.append(node)
            return node
            
        def clear(self):
            self.children = []

    # These are already defined at the top of the file
    # ComposeResult = Any
    # NoMatches = Exception



class Message(Static):
    """A simple message widget that automatically removes itself after a delay."""

    DEFAULT_CSS = """
    Message {
        width: 100%;
        height: auto;
        padding: 1 2;
        margin: 1 0;
        border: tall $primary;
        color: $text;
        background: $surface;
        text-align: center;
    }
    
    Message.error {
        color: $text;
        background: $error;
        border: tall $error-lighten-2;
    }
    
    Message.success {
        color: $text;
        background: $success;
        border: tall $success-lighten-2;
    }
    
    Message.info {
        color: $text;
        background: $primary-darken-1;
        border: tall $primary;
    }
    """

    def __init__(self, text: str, message_type: str = "info", timeout: int = 5):
        super().__init__(text)
        self.message_type = message_type
        self.timeout = timeout

    def on_mount(self) -> None:
        """Called when the message is added to the DOM."""
        if TEXTUAL_AVAILABLE:
            self.add_class(self.message_type)
            self.set_timer(self.timeout, self.remove)


class ItemEntryForm(Container):
    """Form for adding new items."""

    DEFAULT_CSS = """
    ItemEntryForm {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        padding: 1;
        border: wide $primary-darken-2;
        margin-bottom: 1;
    }
    
    ItemEntryForm > Label {
        width: 100%;
        padding: 0 1;
        color: $text;
    }
    
    ItemEntryForm Input {
        width: 100%;
        margin-bottom: 1;
    }
    
    ItemEntryForm Select {
        width: 100%;
        margin-bottom: 1;
    }
    
    ItemEntryForm #buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    ItemEntryForm Button {
        margin: 0 1;
    }
    """

    def __init__(
        self, work_system: WorkSystem, on_submit: Callable[[Dict[str, Any]], None]
    ):
        super().__init__()
        self.work_system = work_system
        self.on_submit = on_submit
        self.goals = self._get_goal_choices()

    def _get_goal_choices(self) -> List[tuple]:
        """Get a list of goals for the dropdown."""
        if not TEXTUAL_AVAILABLE:
            return []

        # Get unique goals from existing items
        goals = sorted(self.work_system.get_all_goals())

        # Format for Textual Select widget
        return [(goal, goal) for goal in goals]

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            return ComposeResult()

        yield Label("Add New Item", id="form-title")

        yield Label("Goal:")
        yield Input(placeholder="Project or goal name", id="goal")

        yield Label("Item Type:")

        yield Select(
            [
                ("Task", ItemType.TASK.value),
                ("Learning", ItemType.LEARNING.value),
                ("Research", ItemType.RESEARCH.value),
                ("Thought", ItemType.THOUGHT.value),
            ],
            id="item_type",
            value=ItemType.TASK.value,
        )

        yield Label("Priority:")

        yield Select(
            [
                ("High", Priority.HI.value),
                ("Medium", Priority.MED.value),
                ("Low", Priority.LOW.value),
            ],
            id="priority",
            value=Priority.MED.value,
        )

        yield Label("Title:")
        yield Input(placeholder="Brief title", id="title")

        yield Label("Description:")
        yield Input(placeholder="Detailed description", id="description")

        # Optional linking section
        yield Label("Link to Item (Optional):")
        yield Input(
            placeholder="Item ID to link to (leave empty if none)", id="link_to"
        )

        yield Label("Link Type (Optional):")
        yield Select(
            [
                ("References", "references"),
                ("Evolves From", "evolves-from"),
                ("Parent-Child", "parent-child"),
                ("Inspired By", "inspired-by"),
            ],
            id="link_type",
            value="references",
        )

        # Buttons
        with Horizontal(id="buttons"):
            yield Button("Submit", variant="primary", id="submit")
            yield Button("Clear", variant="default", id="clear")

    def on_mount(self) -> None:
        """Set up dynamic components after the form is mounted."""
        if not TEXTUAL_AVAILABLE:
            return
            
        try:
            # Set up link suggester
            link_input = self.query_one("#link_to", Input)
            link_input.suggester = SuggestFromList(
                self.work_system.suggest_link_targets(), 
                case_sensitive=False
            )
            
            # Set up goal input to refresh link suggester when changed
            goal_input = self.query_one("#goal", Input)
            self.watch(goal_input, "value", self._refresh_link_suggestions)
            
        except NoMatches:
            pass
            
    def _refresh_link_suggestions(self, value: str = "") -> None:
        """Update link suggestions when goal changes."""
        if not TEXTUAL_AVAILABLE:
            return
            
        try:
            # Get current goal value
            goal = self.query_one("#goal", Input).value
            
            # Update suggester with filtered suggestions
            link_input = self.query_one("#link_to", Input)
            link_input.suggester = SuggestFromList(
                self.work_system.suggest_link_targets(goal=goal if goal else None),
                case_sensitive=False
            )
        except NoMatches:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if not TEXTUAL_AVAILABLE:
            return

        if event.button.id == "submit":
            self._handle_submit()
        elif event.button.id == "clear":
            self._clear_form()

    def _handle_submit(self) -> None:
        """Process form submission."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            # Collect form data
            form_data = {
                "goal": self.query_one("#goal", Input).value,
                "item_type": self.query_one("#item_type", Select).value,
                "priority": self.query_one("#priority", Select).value,
                "title": self.query_one("#title", Input).value,
                "description": self.query_one("#description", Input).value,
                "link_to": self.query_one("#link_to", Input).value,
                "link_type": self.query_one("#link_type", Select).value,
            }

            # Validate required fields
            if not form_data["goal"] or not form_data["title"]:
                self.app.add_message("Goal and title are required", "error")
                return

            # Convert values to enums before submitting
            form_data["item_type"] = ItemType(form_data["item_type"])
            form_data["priority"] = Priority(form_data["priority"])
            # Call the callback with the converted form data
            self.on_submit(form_data)

            # Clear the form
            self._clear_form()

        except NoMatches:
            # This should not happen but handle it just in case
            self.app.add_message(
                "Form error: Could not find all required fields", "error"
            )

    def _clear_form(self) -> None:
        """Reset the form to default values."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            self.query_one("#goal", Input).value = ""
            self.query_one("#item_type", Select).value = ItemType.TASK.value
            self.query_one("#priority", Select).value = Priority.MED.value
            self.query_one("#title", Input).value = ""
            self.query_one("#description", Input).value = ""
            self.query_one("#link_to", Input).value = ""
            self.query_one("#link_type", Select).value = "references"
        except NoMatches:
            pass


class ItemListView(Container):
    """Widget to display and interact with work items."""

    DEFAULT_CSS = """
    ItemListView {
        width: 100%;
        height: 100%;
        layout: vertical;
    }
    
    ItemListView #filters {
        width: 100%;
        height: auto;
        layout: horizontal;
        align: center middle;
        background: $surface;
        padding: 1;
        margin-bottom: 1;
    }
    
    ItemListView #filters Select {
        margin-right: 1;
    }
    
    ItemListView #list-container {
        width: 100%;
        height: 1fr;
        background: $surface;
        overflow: auto;
    }
    
    ItemListView DataTable {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, work_system: WorkSystem):
        super().__init__()
        self.work_system = work_system

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            return ComposeResult()

        # Filters
        with Horizontal(id="filters"):
            yield Label("Filter by:")
            yield Select(
                [
                    ("All Types", None),
                    ("Tasks", ItemType.TASK.value),
                    ("Thoughts", ItemType.THOUGHT.value),
                    ("Learning", ItemType.LEARNING.value),
                    ("Research", ItemType.RESEARCH.value),
                ],
                id="type-filter",
                value=None,
            )
            yield Select(
                [
                    ("All Priorities", None),
                    ("High", Priority.HI.value),
                    ("Medium", Priority.MED.value),
                    ("Low", Priority.LOW.value),
                ],
                id="priority-filter",
                value=None,
            )
            yield Select(
                [
                    ("All Statuses", None),
                    ("Not Started", ItemStatus.NOT_STARTED.value),
                    ("In Progress", ItemStatus.IN_PROGRESS.value),
                    ("Completed", ItemStatus.COMPLETED.value),
                ],
                id="status-filter",
                value=None,
            )
            yield Select(
                [("All Tags", None)]
                + [(t, t) for t in self.work_system.get_all_tags()],
                id="tag-filter",
                value=None,
            )

        # Table container
        with Container(id="list-container"):
            yield DataTable(id="items-table")

    def on_mount(self) -> None:
        """Set up the data table and load items."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            # Set up columns
            table = self.query_one("#items-table", DataTable)
            table.add_columns(
                "ID",
                "Goal",
                "Type",
                "Priority",
                "Status",
                "Title",
                "Tags",
            )

            # Load all items initially
            self._load_items()

            # Set up filter change listeners
            # Check if the Select widget has 'changed' attribute (newer Textual versions)
            # or fall back to 'on_select_changed' (older versions)
            for filter_id in ["#type-filter", "#priority-filter", "#status-filter", "#tag-filter"]:
                select_widget = self.query_one(filter_id, Select)
                
                # Try to use the changed event if available (newer Textual versions)
                if hasattr(select_widget, "changed"):
                    select_widget.changed.connect(self._on_filter_change)
                # Otherwise use watch API or direct binding as fallback
                else:
                    # Direct approach for older Textual versions
                    self.watch(select_widget, "value", self._on_filter_change)
                    
        except NoMatches:
            pass

    def _on_filter_change(self, _: Any) -> None:
        """Reload the items table when filters change."""
        self._load_items()

    def _load_items(self) -> None:
        """Load items based on current filters."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            # Get filter values
            type_filter = self.query_one("#type-filter", Select).value
            priority_filter = self.query_one("#priority-filter", Select).value
            status_filter = self.query_one("#status-filter", Select).value
            tag_filter = self.query_one("#tag-filter", Select).value

            # Convert filter values to enums
            item_type = ItemType(type_filter) if type_filter else None
            priority = Priority(priority_filter) if priority_filter else None
            status = ItemStatus(status_filter) if status_filter else None

            # Get filtered items from the work system
            items = self.work_system.get_filtered_items(
                item_type=item_type,
                priority=priority,
                status=status,
                tag=tag_filter,
            )

            # Clear existing rows
            table = self.query_one("#items-table", DataTable)
            table.clear()

            # Add rows for each item
            for item in items:
                tags = ", ".join(self.work_system.get_tags_for_item(item.id))
                table.add_row(
                    item.id,
                    item.goal,
                    item.item_type,
                    item.priority,
                    item.status,
                    item.title,
                    tags,
                )
        except NoMatches:
            pass

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Handle cell selection in the data table."""
        if not TEXTUAL_AVAILABLE:
            return
        
        # Don't allow editing the ID column
        if event.coordinate.column == 0:
            return
        
        # Get the column name and ID of the selected item
        table = self.query_one("#items-table", DataTable)
        column_name = table.columns[event.coordinate.column].label
        item_id = table.get_cell_at((event.coordinate.row, 0))
        
        # Open the edit cell modal
        self.app.push_screen(
            EditCellScreen(
                coord=event.coordinate,
                column_name=column_name,
                current_value=event.value,
                item_id=item_id
            )
        )


class LinkTreeView(Container):
    """Widget to display relationship trees between items."""

    DEFAULT_CSS = """
    LinkTreeView {
        width: 100%;
        height: 100%;
        layout: vertical;
    }
    
    LinkTreeView #item-selector {
        width: 100%;
        height: auto;
        padding: 1;
        margin-bottom: 1;
        background: $surface;
    }
    
    LinkTreeView #tree-container {
        width: 100%;
        height: 1fr;
        background: $surface;
        border: wide $primary-darken-2;
        padding: 1;
        overflow: auto;
    }
    """

    def __init__(self, work_system: WorkSystem):
        super().__init__()
        self.work_system = work_system

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            return ComposeResult()

        # Item selector
        with Container(id="item-selector"):
            yield Label("Select root item:")
            yield Input(placeholder="Enter item ID", id="item-id")
            yield Button("Show Tree", id="show-tree")

        # Tree display
        with Container(id="tree-container"):
            yield Tree(
                "Select an item to view its relationship tree", id="tree-display"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if not TEXTUAL_AVAILABLE:
            return

        if event.button.id == "show-tree":
            self._show_tree()

    def _show_tree(self) -> None:
        """Display the relationship tree for the selected item."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            # Get the item ID
            item_id = self.query_one("#item-id", Input).value

            if not item_id:
                self.app.add_message("Please enter an item ID", "error")
                return

            # Get the item
            item = self.work_system.db.get_item(item_id)

            if not item:
                self.app.add_message(f"Item {item_id} not found", "error")
                return

            tree = self.query_one("#tree-display", Tree)

            # Reset the tree with the selected item as the root
            tree.root.label = f"[b]{item.id} - {item.title}[/b]"
            tree.root.clear()

            link_type_colors = {
                "references": "blue",
                "evolves-from": "green",
                "inspired-by": "yellow",
                "parent-child": "magenta",
            }

            visited: set[str] = set()

            def build(node: Any, current_id: str, depth: int = 0) -> None:
                if depth > 5 or current_id in visited:
                    if current_id in visited:
                        node.add(f"[dim]{current_id}[/dim] (cycle reference)")
                    return

                visited.add(current_id)
                links = self.work_system.get_links(current_id)

                if links["outgoing"]:
                    out_node = node.add("[b]Outgoing Links[/b]")
                    for link in links["outgoing"]:
                        color = link_type_colors.get(link["link_type"], "white")
                        target_id = link["target_id"]
                        target_item = self.work_system.db.get_item(target_id)
                        if target_item:
                            label = (
                                f"[{color}]{link['link_type']}[/{color}] → "
                                f"{target_id} - {target_item.title}"
                            )
                            build(out_node.add(label), target_id, depth + 1)
                        else:
                            out_node.add(f"[red]Item not found: {target_id}[/red]")

                if links["incoming"]:
                    in_node = node.add("[b]Incoming Links[/b]")
                    for link in links["incoming"]:
                        color = link_type_colors.get(link["link_type"], "white")
                        source_id = link["source_id"]
                        source_item = self.work_system.db.get_item(source_id)
                        if source_item:
                            label = (
                                f"[{color}]{link['link_type']}[/{color}] ← "
                                f"{source_id} - {source_item.title}"
                            )
                            build(in_node.add(label), source_id, depth + 1)
                        else:
                            in_node.add(f"[red]Item not found: {source_id}[/red]")

                visited.remove(current_id)

            build(tree.root, item_id)
            tree.expand_all()

        except NoMatches:
            pass


class MainScreen(Screen):
    """Main application screen with tabbed interface."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "new_item", "New Item"),
        Binding("r", "refresh", "Refresh"),
        Binding("f1", "help", "Help"),
    ]

    def __init__(self, work_system: WorkSystem, start_tab: str | None = None):
        super().__init__()
        self.work_system = work_system
        self.start_tab = start_tab

    def on_mount(self) -> None:
        """Set the starting tab when the screen is displayed."""
        if not TEXTUAL_AVAILABLE or not self.start_tab:
            return

        try:
            tabs = self.query_one(TabbedContent)
            tabs.active = self.start_tab
        except NoMatches:
            pass

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            return ComposeResult()

        # Header with app title
        yield Header(show_clock=True)

        # Main content
        with TabbedContent():
            # New Item Form
            with TabPane("New Item", id="new-item-tab"):
                yield ItemEntryForm(self.work_system, self._on_item_submit)

            # Item List
            with TabPane("Items", id="items-tab"):
                yield ItemListView(self.work_system)

            # Link Tree
            with TabPane("Link Tree", id="link-tree-tab"):
                yield LinkTreeView(self.work_system)

        # Message area for notifications (starts empty)
        yield Container(id="message-area")

        # Footer with key bindings
        yield Footer()

    def action_new_item(self) -> None:
        """Switch to the new item tab."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            tabs = self.query_one(TabbedContent)
            tabs.active = "new-item-tab"
        except NoMatches:
            pass

    def action_refresh(self) -> None:
        """Refresh the current view."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            tabs = self.query_one(TabbedContent)
            active_tab = tabs.active

            if active_tab == "items-tab":
                self.query_one(ItemListView)._load_items()
                self.add_message("Items refreshed", "info")
        except NoMatches:
            pass

    def action_help(self) -> None:
        """Show help information."""
        if not TEXTUAL_AVAILABLE:
            return

        self.add_message(
            "Keys: [Q] Quit, [N] New Item, [R] Refresh, [F1] Help", "info", 10
        )

    def _on_item_submit(self, form_data: Dict[str, Any]) -> None:
        """Handle form submission from the ItemEntryForm."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            # Add the new item
            new_item = self.work_system.add_item(
                goal=form_data["goal"],
                item_type=form_data["item_type"],
                priority=form_data["priority"],
                title=form_data["title"],
                description=form_data["description"],
            )

            # Add link if specified
            link_to = form_data.get("link_to")
            if link_to and new_item:
                link_type = form_data.get("link_type", "references")
                self.work_system.add_link(new_item.id, link_to, link_type)
                self.add_message(
                    f"Item {new_item.id} created and linked to {link_to}", "success"
                )
            elif new_item:
                self.add_message(f"Item {new_item.id} created", "success")
            else:
                self.add_message("Failed to create item", "error")

            # Refresh the item list
            try:
                self.query_one(ItemListView)._load_items()
            except NoMatches:
                pass

        except Exception as e:
            self.add_message(f"Error: {str(e)}", "error")

    def add_message(
        self, text: str, message_type: str = "info", timeout: int = 5
    ) -> None:
        """Add a message to the message area."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            message_area = self.query_one("#message-area")
            message = Message(text, message_type, timeout)
            message_area.mount(message)
        except NoMatches:
            pass


class EditCellScreen(ModalScreen):
    """Modal screen for editing a DataTable cell."""

    DEFAULT_CSS = """
    EditCellScreen {
        align: center middle;
    }

    .edit-container {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    .edit-container #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    .edit-container Input, .edit-container Select {
        width: 100%;
        margin-bottom: 1;
    }

    .edit-container #buttons {
        width: 100%;
        height: 3;
        align: center middle;
    }

    .edit-container Button {
        margin: 0 1;
    }
    """

    def __init__(self, coord: Coordinate, column_name: str, current_value: str, item_id: str):
        super().__init__()
        self.coord = coord
        self.column_name = column_name
        self.current_value = current_value
        self.item_id = item_id
        self.field_widgets = {}

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            return ComposeResult()

        with Vertical(classes="edit-container"):
            yield Label(f"Edit {self.column_name}", id="title")
            
            if self.column_name == "Status":
                self.field_widgets["status"] = Select(
                    [
                        (ItemStatus.NOT_STARTED.name, ItemStatus.NOT_STARTED.value),
                        (ItemStatus.IN_PROGRESS.name, ItemStatus.IN_PROGRESS.value),
                        (ItemStatus.COMPLETED.name, ItemStatus.COMPLETED.value),
                    ],
                    value=self.current_value,
                    id="value-input"
                )
                yield self.field_widgets["status"]
            elif self.column_name == "Priority":
                self.field_widgets["priority"] = Select(
                    [
                        (Priority.HI.name, Priority.HI.value),
                        (Priority.MED.name, Priority.MED.value),
                        (Priority.LOW.name, Priority.LOW.value),
                    ],
                    value=self.current_value,
                    id="value-input"
                )
                yield self.field_widgets["priority"]
            elif self.column_name == "Type":
                self.field_widgets["item_type"] = Select(
                    [
                        (ItemType.TASK.name, ItemType.TASK.value),
                        (ItemType.THOUGHT.name, ItemType.THOUGHT.value),
                        (ItemType.LEARNING.name, ItemType.LEARNING.value),
                        (ItemType.RESEARCH.name, ItemType.RESEARCH.value),
                    ],
                    value=self.current_value,
                    id="value-input"
                )
                yield self.field_widgets["item_type"]
            else:
                # Default to text input for other fields
                self.field_widgets["text"] = Input(
                    value=self.current_value,
                    id="value-input"
                )
                yield self.field_widgets["text"]
            
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save":
            self._save_changes()
        elif event.button.id == "cancel":
            self.dismiss()

    def _save_changes(self) -> None:
        """Save the changes to the database and update the table."""
        if not TEXTUAL_AVAILABLE:
            return

        try:
            # Get the new value from the appropriate widget
            widget = self.query_one("#value-input")
            new_value = widget.value
            
            # Get the field name from the column name
            field = self.column_name.lower()
            
            # Get the work system and update the item
            app = self.app
            work_system = app.work_system
            
            # Form the update kwargs
            update_kwargs = {field: new_value}
            
            # Update the item
            work_system.update_item(self.item_id, **update_kwargs)
            
            # Get the table and update the cell
            main_screen = app.query_one(MainScreen)
            table = main_screen.query_one(ItemListView).query_one(DataTable)
            table.update_cell_at(self.coord, new_value)
            
            # Show success message
            main_screen.add_message(f"Updated {self.column_name} for item {self.item_id}", "success")
            
            # Dismiss the modal
            self.dismiss()
        except Exception as e:
            # Show error message but don't dismiss
            main_screen = self.app.query_one(MainScreen)
            main_screen.add_message(f"Error updating {self.column_name}: {str(e)}", "error")


class TextualApp(App):
    """
    Textual-based UI for the Personal Operating System (POS).

    A more intuitive interface for managing work items, thoughts, and their relationships.
    """

    TITLE = "Personal Operating System"
    CSS = """
    Screen {
        background: $surface;
    }
    
    #message-area {
        width: 100%;
        height: auto;
        layout: vertical;
        align: center top;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(
        self, work_system: Optional[WorkSystem] = None, start_tab: str | None = None
    ):
        super().__init__()
        self.work_system = work_system or WorkSystem()
        self.start_tab = start_tab

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        if not TEXTUAL_AVAILABLE:
            yield Static("POS Textual UI - Textual library not available")
            return ComposeResult()

        yield MainScreen(self.work_system, self.start_tab)

    def on_mount(self) -> None:
        """Called when app is mounted."""
        if not TEXTUAL_AVAILABLE:
            self.exit()
            return
            
    @command
    def add_new_item(self) -> None:
        """Create a new work item."""
        if not TEXTUAL_AVAILABLE:
            return
            
        try:
            main_screen = self.query_one(MainScreen)
            main_screen.action_new_item()
        except NoMatches:
            pass
            
    @command
    def view_items(self) -> None:
        """View and filter work items."""
        if not TEXTUAL_AVAILABLE:
            return
            
        try:
            main_screen = self.query_one(MainScreen)
            tabs = main_screen.query_one(TabbedContent)
            tabs.active = "items-tab"
        except NoMatches:
            pass
            
    @command
    def view_link_tree(self) -> None:
        """View item relationships as a tree."""
        if not TEXTUAL_AVAILABLE:
            return
            
        try:
            main_screen = self.query_one(MainScreen)
            tabs = main_screen.query_one(TabbedContent)
            tabs.active = "link-tree-tab"
        except NoMatches:
            pass
            
    @command
    def refresh_data(self) -> None:
        """Refresh the current view."""
        if not TEXTUAL_AVAILABLE:
            return
            
        try:
            main_screen = self.query_one(MainScreen)
            main_screen.action_refresh()
        except NoMatches:
            pass
