"""
Form widget for entering and editing work items.

Provides a user-friendly interface for creating and editing work items
with validation and error handling.
"""

from typing import Dict, List, Optional, Set, Union

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.message import Message
from textual.validation import Validator, ValidationResult
from textual.widgets import Button, Input, Label, ListView, Select, Static, TextArea

from ...models import ItemStatus, ItemType, LinkType, Priority, WorkItem
from ..workers import LinkWorker, ItemSearchWorker


class ItemEntryForm(Container):
    """Form for creating and editing work items with validation."""
    
    DEFAULT_CSS = """
    ItemEntryForm {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    ItemEntryForm #form-header {
        text-align: center;
        margin-bottom: 1;
    }
    
    ItemEntryForm #form-title {
        text-style: bold;
        background: $accent;
        color: $text;
        width: 100%;
        padding: 1;
        text-align: center;
    }
    
    ItemEntryForm .form-section {
        margin-bottom: 1;
    }
    
    ItemEntryForm .field-container {
        height: auto;
        margin-bottom: 1;
    }
    
    ItemEntryForm .field-label {
        width: 30%;
        padding-top: 1;
    }
    
    ItemEntryForm .field-input {
        width: 70%;
    }
    
    ItemEntryForm TextArea {
        height: 6;
    }
    
    ItemEntryForm #error-container {
        color: $error;
        height: auto;
        margin: 1 0;
    }
    
    ItemEntryForm #button-container {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    
    ItemEntryForm #button-container Button {
        margin: 0 1;
    }
    
    ItemEntryForm #links-section {
        margin-top: 1;
        border: solid $accent;
        padding: 1;
    }
    
    ItemEntryForm #links-title {
        text-style: bold;
        margin-bottom: 1;
    }
    
    ItemEntryForm #links-container {
        height: auto;
        max-height: 8;
        overflow-y: auto;
    }
    
    ItemEntryForm .link-item {
        height: auto;
        padding: 0 1;
    }
    
    ItemEntryForm .link-item:hover {
        background: $accent-darken-1;
    }
    
    ItemEntryForm .link-remove {
        background: $error;
        color: $text;
        padding: 0 1;
        margin-left: 1;
    }
    
    ItemEntryForm #link-controls {
        margin-top: 1;
    }
    """
    
    class ItemSubmitted(Message):
        """Message sent when an item is submitted."""
        def __init__(self, item_data: Dict[str, Union[str, int, bool]], links: List[Dict[str, str]]) -> None:
            self.item_data = item_data
            self.links = links
            super().__init__()
            
    class EditCancelled(Message):
        """Message sent when editing is cancelled."""
        pass
    
    def __init__(self, id: Optional[str] = None):
        """Initialize the form widget."""
        super().__init__(id=id)
        self.editing_item: Optional[WorkItem] = None
        self.errors: List[str] = []
        self.linked_items: List[Dict[str, str]] = []
        self.item_search_results: List[Dict[str, str]] = []
    
    def compose(self) -> ComposeResult:
        """Compose the form layout."""
        # Form header
        with Container(id="form-header"):
            yield Static("Create New Item", id="form-title")
        
        # Main form
        with Vertical(classes="form-section"):
            # Goal field
            with Horizontal(classes="field-container"):
                yield Label("Goal:", classes="field-label")
                yield Input(
                    placeholder="Enter goal",
                    id="goal_field",
                    classes="field-input",
                )

            # Title field
            with Horizontal(classes="field-container"):
                yield Label("Title:", classes="field-label")
                yield Input(placeholder="Enter title", id="title_field", classes="field-input")
            
            # Type field
            with Horizontal(classes="field-container"):
                yield Label("Type:", classes="field-label")
                yield Select(
                    [(t.name, t.value) for t in ItemType],
                    id="type_field",
                    value=ItemType.TASK.value,
                    classes="field-input"
                )
            
            # Priority field
            with Horizontal(classes="field-container"):
                yield Label("Priority:", classes="field-label")
                yield Select(
                    [(p.name, str(p.value)) for p in Priority],
                    id="priority_field",
                    value=str(Priority.MED.value),
                    classes="field-input"
                )
            
            # Status field
            with Horizontal(classes="field-container"):
                yield Label("Status:", classes="field-label")
                yield Select(
                    [(s.name, s.value) for s in ItemStatus],
                    id="status_field",
                    value=ItemStatus.NOT_STARTED.value,
                    classes="field-input"
                )
            
            # Tags field
            with Horizontal(classes="field-container"):
                yield Label("Tags:", classes="field-label")
                yield Input(
                    placeholder="Enter tags separated by commas",
                    id="tags_field",
                    classes="field-input"
                )
            
            # Description field
            with Horizontal(classes="field-container"):
                yield Label("Description:", classes="field-label")
                yield TextArea(
                    id="description_field",
                    classes="field-input"
                )
                
            # Links section
            with Container(id="links-section"):
                yield Static("Linked Items", id="links-title")
                
                # Container for linked items display
                yield Container(id="links-container")
                
                # Link controls
                with Horizontal(id="link-controls"):
                    # Item search field
                    yield Input(
                        placeholder="Search for items to link",
                        id="item_search_field",
                        classes="field-input"
                    )
                    
                    # Link type selector
                    yield Select(
                        [(lt.name, lt.value) for lt in LinkType],
                        id="link_type_field",
                        value=LinkType.REFERENCES.value,
                        classes="field-input"
                    )
                    
                    # Add link button
                    yield Button("Add Link", id="add_link_btn", variant="primary")
                    
                # Search results container
                yield Container(id="search_results_container")
        
        # Error container
        yield Static("", id="error-container")
        
        # Buttons
        with Horizontal(id="button-container"):
            yield Button("Clear", variant="default", id="clear_btn")
            yield Button("Cancel", variant="primary", id="cancel_btn")
            yield Button("Submit", variant="success", id="submit_btn")
    
    def on_mount(self) -> None:
        """Handle the mount event to set up initial state."""
        # Hide the cancel button initially
        self.query_one("#cancel_btn").display = False
        
        # Clear any previous linked items
        self.linked_items = []
        self.refresh_linked_items_display()
        
    def edit_item(self, item: WorkItem) -> None:
        """Set up the form for editing an existing item."""
        self.editing_item = item
        
        # Update the form title
        self.query_one("#form-title").update(f"Edit Item: {item.id}")
        
        # Set form values
        self.query_one("#goal_field").value = item.goal
        self.query_one("#title_field").value = item.title
        self.query_one("#type_field").value = item.item_type.value
        self.query_one("#priority_field").value = str(item.priority.value)
        self.query_one("#status_field").value = item.status.value
        
        # Set tags if available
        if hasattr(item, "tags") and item.tags:
            self.query_one("#tags_field").value = ", ".join(item.tags)
        
        # Set description if available
        if hasattr(item, "description") and item.description:
            self.query_one("#description_field").value = item.description
            
        
        # Show the cancel button
        self.query_one("#cancel_btn").display = True
        
        # Load linked items if this is an existing item
        if item.id:
            self.load_linked_items(item.id)
    
    def load_linked_items(self, item_id: str) -> None:
        """Load linked items for an existing item."""
        # Clear any previous linked items
        self.linked_items = []
        
        # Start a worker to fetch links
        def on_worker_completed(worker) -> None:
            if worker.result and worker.result.get("success", False):
                links = worker.result.get("links", {})
                
                # Process outgoing links
                for link in links.get("outgoing", []):
                    self.linked_items.append({
                        "id": link["target_id"],
                        "title": link["title"],
                        "link_type": link["link_type"]
                    })
                
                # Refresh the linked items display
                self.refresh_linked_items_display()
        
        # Create and start the worker
        worker = LinkWorker()
        worker.completed.connect(on_worker_completed)
        worker.start(operation="get", source_id=item_id)
    
    def refresh_linked_items_display(self) -> None:
        """Update the linked items display based on current links."""
        # Get the container for linked items
        container = self.query_one("#links-container")
        
        # Clear existing content
        container.remove_children()
        
        # Add each linked item
        if not self.linked_items:
            container.mount(Static("No linked items", classes="no-links"))
        else:
            for item in self.linked_items:
                with container.mount(Horizontal(classes="link-item")):
                    link_type_display = item["link_type"].replace("-", " ").title()
                    link_text = f"{link_type_display}: {item['title']} ({item['id']})"
                    yield Static(link_text)
                    yield Button("X", classes="link-remove", id=f"remove_link_{item['id']}")
    
    def search_items(self, search_term: str) -> None:
        """Search for items to link."""
        # Clear previous search results
        results_container = self.query_one("#search_results_container")
        results_container.remove_children()
        
        # If search term is empty, hide results
        if not search_term:
            return
        
        # Get IDs to exclude (current item and already linked items)
        exclude_ids = []
        if self.editing_item:
            exclude_ids.append(self.editing_item.id)
        exclude_ids.extend([item["id"] for item in self.linked_items])
        
        # Start a worker to search for items
        def on_worker_completed(worker) -> None:
            if worker.result and worker.result.get("success", False):
                items = worker.result.get("items", [])
                
                # Store search results
                self.item_search_results = [
                    {"id": item["id"], "title": item.get("title", f"Item {item['id']}")} 
                    for item in items
                ]
                
                # Display search results
                for i, item in enumerate(self.item_search_results):
                    results_container.mount(
                        Button(
                            f"{item['title']} ({item['id']})",
                            id=f"search_result_{i}",
                            variant="default"
                        )
                    )
                
                # If no results found
                if not self.item_search_results:
                    results_container.mount(Static("No items found"))
        
        # Create and start the worker
        worker = ItemSearchWorker()
        worker.completed.connect(on_worker_completed)
        worker.start(search_term=search_term, exclude_ids=exclude_ids)
        
        # Show loading message while searching
        results_container.mount(Static("Searching..."))
    
    def clear_form(self) -> None:
        """Clear all form fields."""
        # Reset to default values
        self.query_one("#goal_field").value = ""
        self.query_one("#title_field").value = ""
        self.query_one("#type_field").value = ItemType.TASK.value
        self.query_one("#priority_field").value = str(Priority.MED.value)
        self.query_one("#status_field").value = ItemStatus.NOT_STARTED.value
        self.query_one("#tags_field").value = ""
        self.query_one("#description_field").value = ""
        
        # Clear item search field
        self.query_one("#item_search_field").value = ""
        
        # Reset link type to default
        self.query_one("#link_type_field").value = LinkType.REFERENCES.value
        
        # Clear search results
        search_results = self.query_one("#search_results_container")
        search_results.remove_children()
        
        # Clear linked items
        self.linked_items = []
        self.refresh_linked_items_display()
        
        # Clear errors
        self.errors = []
        self.query_one("#error-container").update("")
        
        # Reset edit state
        self.editing_item = None
        self.query_one("#form-title").update("Create New Item")
        self.query_one("#cancel_btn").display = False
    
    def validate_form(self) -> bool:
        """Validate form data and show errors if any."""
        # Clear previous errors
        self.errors = []
        self.query_one("#error-container").update("")
        
        # Check required fields
        goal = self.query_one("#goal_field").value
        title = self.query_one("#title_field").value
        if not title:
            self.errors.append("Title is required")
        
        description = self.query_one("#description_field").value
        if not description:
            self.errors.append("Description is required")
        
        # Validate link constraints
        self._validate_link_constraints()
        
        # Show errors if any
        if self.errors:
            error_message = "\n".join(f"- {error}" for error in self.errors)
            self.query_one("#error-container").update(error_message)
            return False
        
        return True
    
    def _validate_link_constraints(self) -> None:
        """Validate links for consistency and prevent circular references."""
        # Skip if no links or not editing an item
        if not self.linked_items or not self.editing_item:
            return
            
        # Check for self-referential links
        for link in self.linked_items:
            if link["id"] == self.editing_item.id:
                self.errors.append("An item cannot link to itself")
                break
        
        # Check for circular references in "evolves-from" relationships
        # This is a simplified check - a more complete implementation would
        # check the entire graph for cycles
        evolves_from_links = [link for link in self.linked_items 
                             if link["link_type"] == LinkType.EVOLVES_FROM.value]
        
        if evolves_from_links and self.editing_item:
            # Get all target IDs for evolves-from links
            target_ids = [link["id"] for link in evolves_from_links]
            
            # Check if any of these items have evolves-from links back to this item
            # This would require additional database queries in a full implementation
            # For now, we'll add a placeholder warning
            if len(evolves_from_links) > 1:
                self.errors.append("An item should typically evolve from at most one item")
    
        # Validate that parent-child relationships are used consistently
        parent_child_links = [link for link in self.linked_items 
                              if link["link_type"] == LinkType.PARENT_CHILD.value]
        
        # Add warnings for potentially inconsistent usage
        if parent_child_links and evolves_from_links:
            self.errors.append("Mixing 'Parent-Child' and 'Evolves-From' links may create confusing relationships")
    
    def collect_form_data(self) -> Dict[str, Union[str, int, bool]]:
        """Collect data from the form fields."""
        # Get values from form fields
        goal = self.query_one("#goal_field").value
        title = self.query_one("#title_field").value
        item_type = self.query_one("#type_field").value
        priority = int(self.query_one("#priority_field").value)
        status = self.query_one("#status_field").value
        tags_str = self.query_one("#tags_field").value
        description = self.query_one("#description_field").value
        
        # Process tags
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        # Return collected data
        return {
            "goal": goal,
            "title": title,
            "item_type": item_type,
            "priority": priority,
            "status": status,
            "tags": tags,
            "description": description,
        }
    
    @on(Button.Pressed, "#submit_btn")
    def handle_submit(self) -> None:
        """Handle the submit button click."""
        # Validate form
        if not self.validate_form():
            return
        
        # Collect form data
        item_data = self.collect_form_data()
        
        # Post a message with the collected data
        self.post_message(self.ItemSubmitted(item_data, self.linked_items))
    
    @on(Button.Pressed, "#clear_btn")
    def handle_clear(self) -> None:
        """Handle the clear button click."""
        self.clear_form()
    
    @on(Button.Pressed, "#cancel_btn")
    def handle_cancel(self) -> None:
        """Handle the cancel button click."""
        self.post_message(self.EditCancelled())
    
    @on(Input.Changed, "#item_search_field")
    def handle_item_search(self, event: Input.Changed) -> None:
        """Handle changes to the item search field."""
        self.search_items(event.value)
    
    @on(Button.Pressed, "#add_link_btn")
    def handle_add_link(self) -> None:
        """Handle adding a link to the item."""
        # Get the currently selected item from search results
        search_container = self.query_one("#search_results_container")
        selected_buttons = search_container.query("Button.selected")
        
        if not selected_buttons:
            self.show_error("Please select an item to link")
            return
        
        selected_button = selected_buttons[0]
        item_id = selected_button.id.replace("search_result_", "")
        item_title = selected_button.label
        
        # Get the link type
        link_type = self.query_one("#link_type_field").value
        
        # Check if this item is already linked
        if any(link["id"] == item_id for link in self.linked_items):
            self.show_error(f"Item '{item_title}' is already linked")
            return
        
        # Add to linked items
        self.linked_items.append({
            "id": item_id,
            "title": item_title,
            "link_type": link_type
        })
        
        # Refresh the linked items display
        self.refresh_linked_items_display()
        
        # Clear the search field and results
        self.query_one("#item_search_field").value = ""
        search_container.remove_children()
    
    @on(Button.Pressed, ".link-remove")
    def handle_remove_link(self, event: Button.Pressed) -> None:
        """Handle removing a link."""
        # Extract the item ID from the button ID
        button_id = event.button.id
        if button_id.startswith("remove_link_"):
            item_id = button_id[12:]  # Remove "remove_link_" prefix
            
            # Remove the item from linked_items
            self.linked_items = [link for link in self.linked_items if link["id"] != item_id]
            
            # Refresh the display
            self.refresh_linked_items_display()
    
    @on(Button.Pressed, "#search_results_container Button")
    def handle_search_result_click(self, event: Button.Pressed) -> None:
        """Handle clicking on a search result."""
        # Clear any existing selection
        search_container = self.query_one("#search_results_container")
        for button in search_container.query("Button"):
            button.remove_class("selected")
        
        # Mark this button as selected
        event.button.add_class("selected")

    def show_error(self, message: str) -> None:
        """Display an error message in the error container."""
        self.query_one("#error-container").update(message)

__all__ = [
    "ItemStatus",
    "ItemType",
    "LinkType",
    "POSTUI",
    "Priority",
    "WorkItem",
    "WorkSystem",
    "WorkSystemCLI",
]
