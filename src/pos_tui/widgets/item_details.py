"""
Modal dialog for displaying item details.

Shows all fields and metadata for a selected work item.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, Markdown
from textual import on
from textual.message import Message
from textual.events import Click

from ...models import WorkItem, LinkType
from ..workers import LinkWorker


class LinkedItemsWidget(Container):
    """Widget for displaying linked items with visual indicators for link types."""
    
    DEFAULT_CSS = """
    LinkedItemsWidget {
        width: 100%;
        height: auto;
        margin: 1 0;
        border: solid $primary;
        padding: 1;
    }
    
    LinkedItemsWidget #links-header {
        text-style: bold;
        margin-bottom: 1;
    }
    
    LinkedItemsWidget #links-container {
        height: auto;
    }
    
    LinkedItemsWidget .link-item {
        height: auto;
        margin-bottom: 1;
        padding: 1;
        border-left: heavy $primary;
    }
    
    LinkedItemsWidget .link-type-references {
        border-left: heavy $primary;
    }
    
    LinkedItemsWidget .link-type-evolves-from {
        border-left: heavy $success;
    }
    
    LinkedItemsWidget .link-type-inspired-by {
        border-left: heavy $warning;
    }
    
    LinkedItemsWidget .link-type-parent-child {
        border-left: heavy $accent;
    }
    
    LinkedItemsWidget .link-type-indicator {
        width: 2;
        height: 100%;
        margin-right: 1;
    }
    
    LinkedItemsWidget .link-details {
        width: 1fr;
    }
    
    LinkedItemsWidget .link-title {
        text-style: bold;
    }
    
    LinkedItemsWidget .link-id {
        color: $text-muted;
    }
    
    LinkedItemsWidget .link-type {
        color: $text-muted;
    }
    """
    
    class LinkSelected(Message):
        """Event emitted when a linked item is selected."""
        def __init__(self, item_id: str):
            self.item_id = item_id
            super().__init__()
    
    def __init__(self, item_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_id = item_id
        self.links = {"outgoing": [], "incoming": []}
    
    def compose(self) -> ComposeResult:
        """Compose the linked items widget."""
        yield Static("Linked Items", id="links-header")
        yield Container(id="links-container")
    
    def on_mount(self) -> None:
        """Load linked items when the widget is mounted."""
        self.load_links()
    
    def load_links(self) -> None:
        """Load linked items for the current item."""
        def on_worker_completed(worker) -> None:
            if worker.result and worker.result.get("success", False):
                self.links = worker.result.get("links", {"outgoing": [], "incoming": []})
                self.refresh_links_display()
        
        # Create and start the worker
        worker = LinkWorker()
        worker.completed.connect(on_worker_completed)
        worker.start(operation="get", source_id=self.item_id)
    
    def refresh_links_display(self) -> None:
        """Update the display with the current links."""
        container = self.query_one("#links-container")
        container.remove_children()
        
        # Display outgoing links if any
        if self.links["outgoing"]:
            with container.mount(Static("Outgoing Links:", classes="links-section-header")):
                for link in self.links["outgoing"]:
                    self._create_link_item(container, link, "outgoing")
        
        # Display incoming links if any
        if self.links["incoming"]:
            with container.mount(Static("Incoming Links:", classes="links-section-header")):
                for link in self.links["incoming"]:
                    self._create_link_item(container, link, "incoming")
        
        # Show message if no links
        if not self.links["outgoing"] and not self.links["incoming"]:
            container.mount(Static("No linked items", classes="no-links"))
    
    def _create_link_item(self, container, link, direction) -> None:
        """Create a visual representation of a link."""
        link_type = link["link_type"]
        item_id = link["target_id"] if direction == "outgoing" else link["source_id"]
        title = link["title"]
        
        # Format the link type for display
        link_type_display = link_type.replace("-", " ").title()
        
        # Determine CSS class based on link type
        link_type_class = f"link-type-{link_type}"
        
        # Create the link item container with appropriate styling
        with container.mount(Horizontal(classes=f"link-item {link_type_class}", id=f"link_{item_id}")):
            # Add visual indicator based on link type
            yield Static("", classes=f"link-type-indicator")
            
            # Add link details
            with Vertical(classes="link-details"):
                yield Static(title, classes="link-title")
                yield Static(f"ID: {item_id}", classes="link-id")
                yield Static(f"Relationship: {link_type_display}", classes="link-type")
    
    @on(Click, ".link-item")
    def handle_link_click(self, event: Click) -> None:
        """Handle click on a linked item."""
        # Extract the item ID from the link element's ID
        link_id = event.sender.id
        if link_id and link_id.startswith("link_"):
            item_id = link_id[5:]  # Remove "link_" prefix
            self.post_message(self.LinkSelected(item_id))


class ItemDetailsModal(ModalScreen):
    """Modal dialog for displaying work item details."""
    
    DEFAULT_CSS = """
    ItemDetailsModal {
        align: center middle;
    }
    
    #details-container {
        background: $surface;
        border: thick $primary;
        width: 80%;
        height: 80%;
        padding: 1 2;
    }
    
    #details-title {
        text-style: bold;
        text-align: center;
        width: 100%;
        background: $primary;
        padding: 1 0;
        color: $text;
    }
    
    #breadcrumb-container {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
        background: $surface-darken-1;
    }
    
    .breadcrumb-item {
        margin-right: 1;
        text-decoration: underline;
        cursor: pointer;
    }
    
    .breadcrumb-separator {
        margin-right: 1;
        color: $text-muted;
    }
    
    .field-label {
        text-style: bold;
        width: 15;
    }
    
    .field-value {
        width: 1fr;
        min-width: 40;
    }
    
    #details-description {
        height: 25%;
        min-height: 10;
        border: solid $primary;
        margin: 1 0;
        padding: 1;
    }
    
    #details-content {
        height: 1fr;
        overflow-y: auto;
    }
    
    #details-footer {
        align-horizontal: center;
        margin-top: 1;
    }
    """
    
    def __init__(self, item: WorkItem, navigation_history=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        self.navigation_history = navigation_history or []
        # Add current item to navigation history if not already there
        if not self.navigation_history or self.navigation_history[-1] != (self.item.id, self.item.title):
            self.navigation_history.append((self.item.id, self.item.title))
    
    def compose(self) -> ComposeResult:
        """Compose the item details modal."""
        with Container(id="details-container"):
            yield Static(f"Item Details: {self.item.title}", id="details-title")
            
            # Breadcrumb navigation
            yield self._compose_breadcrumbs()
            
            with Vertical(id="details-content"):
                # Basic information
                with Horizontal(classes="details-row"):
                    yield Label("ID:", classes="field-label")
                    yield Label(self.item.id, classes="field-value", id="item-id")
                
                with Horizontal(classes="details-row"):
                    yield Label("Title:", classes="field-label")
                    yield Label(self.item.title, classes="field-value", id="item-title")
                
                with Horizontal(classes="details-row"):
                    yield Label("Goal:", classes="field-label")
                    yield Label(self.item.goal, classes="field-value", id="item-goal")
                
                with Horizontal(classes="details-row"):
                    yield Label("Type:", classes="field-label")
                    yield Label(self.item.item_type.name, classes="field-value", id="item-type")
                
                with Horizontal(classes="details-row"):
                    yield Label("Status:", classes="field-label")
                    yield Label(self.item.status.name.replace("_", " ").title(), 
                               classes="field-value", id="item-status")
                
                with Horizontal(classes="details-row"):
                    yield Label("Priority:", classes="field-label")
                    yield Label(self.item.priority.name, classes="field-value", id="item-priority")
                
                with Horizontal(classes="details-row"):
                    yield Label("Created:", classes="field-label")
                    yield Label(self.item.created_at.strftime("%Y-%m-%d %H:%M"), 
                               classes="field-value", id="item-created")
                
                with Horizontal(classes="details-row"):
                    yield Label("Updated:", classes="field-label")
                    yield Label(self.item.updated_at.strftime("%Y-%m-%d %H:%M"), 
                               classes="field-value", id="item-updated")
                
                # Description
                yield Label("Description:", classes="field-label")
                yield Static(self.item.description, id="details-description")
                
                # Related items and links
                yield LinkedItemsWidget(self.item.id, id="linked-items-widget")
                
                # Footer with buttons
                with Horizontal(id="details-footer"):
                    yield Button("Edit", id="edit-item", variant="primary")
                    yield Button("Close", id="close-modal", variant="default")
    
    def _compose_breadcrumbs(self) -> Container:
        """Create breadcrumb navigation component."""
        container = Container(id="breadcrumb-container")
        
        # Add breadcrumb items based on navigation history
        for i, (item_id, item_title) in enumerate(self.navigation_history):
            # Add separator between breadcrumb items
            if i > 0:
                container.mount(Static(" > ", classes="breadcrumb-separator"))
            
            # Add the breadcrumb item
            container.mount(Static(
                item_title, 
                classes="breadcrumb-item", 
                id=f"breadcrumb_{item_id}"
            ))
        
        return container
    
    @on(Button.Pressed, "#edit-item")
    def handle_edit_button(self) -> None:
        """Handle edit button press."""
        # Emit a message to the parent screen to open the edit form
        self.app.push_screen("edit_item", item=self.item)
        self.dismiss()
    
    @on(Button.Pressed, "#close-modal")
    def handle_close_button(self) -> None:
        """Handle close button press."""
        self.app.pop_screen()
    
    @on(Click, ".breadcrumb-item")
    def handle_breadcrumb_click(self, event: Click) -> None:
        """Handle click on a breadcrumb item."""
        # Extract the item ID from the breadcrumb's ID
        breadcrumb_id = event.sender.id
        if breadcrumb_id and breadcrumb_id.startswith("breadcrumb_"):
            item_id = breadcrumb_id[11:]  # Remove "breadcrumb_" prefix
            item_idx = -1
            
            # Find the index of this item in the history
            for idx, (history_id, _) in enumerate(self.navigation_history):
                if history_id == item_id:
                    item_idx = idx
                    break
            
            if item_idx >= 0:
                # Truncate history to this item
                self.navigation_history = self.navigation_history[:item_idx + 1]
                self.app.fetch_and_display_item(item_id, self.navigation_history)
    
    @on(LinkedItemsWidget.LinkSelected)
    def handle_link_selected(self, event: LinkedItemsWidget.LinkSelected) -> None:
        """Handle selection of a linked item."""
        # Get the item ID from the event
        item_id = event.item_id
        
        # Add to navigation history
        self.navigation_history.append((item_id, "Loading..."))  # Title will be updated when item is loaded
        
        # Load and display the selected item
        self.app.fetch_and_display_item(item_id, self.navigation_history) 