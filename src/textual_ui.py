from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

try:  # pragma: no cover - Textual is optional
    from textual.app import App, ComposeResult  # type: ignore
    from textual.binding import Binding  # type: ignore
    from textual.containers import Container, Horizontal, Vertical  # type: ignore
    from textual.css.query import NoMatches  # type: ignore
    from textual.screen import Screen  # type: ignore
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
    )

    TEXTUAL_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - fallback stub
    TEXTUAL_AVAILABLE = False

    class App:  # type: ignore
        def __init__(self, *_, **__):
            pass

        def run(self, *_, **__):
            print("Textual not available")

    class Static:  # type: ignore
        def __init__(self, *_, **__):
            pass

    # Define empty classes for type checking
    ComposeResult = Any
    Binding = Any
    Container = Any
    Horizontal = Any
    Vertical = Any
    Screen = Any
    Button = Any
    DataTable = Any
    Footer = Any
    Header = Any
    Input = Any
    Label = Any
    Select = Any
    Static = Any  # noqa: F811
    TabPane = Any
    TabbedContent = Any
    Widget = Any
    NoMatches = Exception

from src.models import ItemStatus, ItemType, Priority
from src.storage import WorkSystem


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
            return None

        # Debug: Print ItemType values
        print(
            f"ItemType values: TASK={ItemType.TASK.value}, LEARNING={ItemType.LEARNING.value}, RESEARCH={ItemType.RESEARCH.value}, THOUGHT={ItemType.THOUGHT.value}"
        )

        yield Label("Add New Item", id="form-title")

        yield Label("Goal:")
        yield Input(placeholder="Project or goal name", id="goal")

        yield Label("Item Type:")
        # Debug item type values for troubleshooting
        print(
            f"ItemType values: TASK={ItemType.TASK.value}, LEARNING={ItemType.LEARNING.value}, RESEARCH={ItemType.RESEARCH.value}, THOUGHT={ItemType.THOUGHT.value}"
        )

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
        # Debug priority values
        print(
            f"Priority values: HI={Priority.HI.value}, MED={Priority.MED.value}, LOW={Priority.LOW.value}"
        )

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
            return None

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
            table.add_columns("ID", "Goal", "Type", "Priority", "Status", "Title")

            # Load all items initially
            self._load_items()

            # Set up filter change listeners
            self.query_one("#type-filter", Select).changed.connect(
                self._on_filter_change
            )
            self.query_one("#priority-filter", Select).changed.connect(
                self._on_filter_change
            )
            self.query_one("#status-filter", Select).changed.connect(
                self._on_filter_change
            )
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

            # Convert filter values to enums
            item_type = ItemType(type_filter) if type_filter else None
            priority = Priority(priority_filter) if priority_filter else None
            status = ItemStatus(status_filter) if status_filter else None

            # Get filtered items from the work system
            items = self.work_system.get_filtered_items(
                item_type=item_type, priority=priority, status=status
            )

            # Clear existing rows
            table = self.query_one("#items-table", DataTable)
            table.clear()

            # Add rows for each item
            for item in items:
                table.add_row(
                    item.id,
                    item.goal,
                    item.item_type,
                    item.priority,
                    item.status,
                    item.title,
                )
        except NoMatches:
            pass


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
            return None

        # Item selector
        with Container(id="item-selector"):
            yield Label("Select root item:")
            yield Input(placeholder="Enter item ID", id="item-id")
            yield Button("Show Tree", id="show-tree")

        # Tree display
        with Container(id="tree-container"):
            yield Static(
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

            # Get links for the item
            links = self.work_system.get_links(item_id)

            # Build a simple text tree for now
            # In a real implementation, this would be a more sophisticated tree visualization
            tree_text = f"[b]{item.id} - {item.title}[/b]\n\n"

            if links["outgoing"]:
                tree_text += "[u]Outgoing Links:[/u]\n"
                for link in links["outgoing"]:
                    tree_text += f"  → {link['target_id']} - {link['title']} (Type: {link['link_type']})\n"
                tree_text += "\n"

            if links["incoming"]:
                tree_text += "[u]Incoming Links:[/u]\n"
                for link in links["incoming"]:
                    tree_text += f"  ← {link['source_id']} - {link['title']} (Type: {link['link_type']})\n"

            # Update the tree display
            self.query_one("#tree-display", Static).update(tree_text)

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
            return None

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
            return

        yield MainScreen(self.work_system, self.start_tab)

    def on_mount(self) -> None:
        """Called when app is mounted."""
        if not TEXTUAL_AVAILABLE:
            self.exit()
            return
