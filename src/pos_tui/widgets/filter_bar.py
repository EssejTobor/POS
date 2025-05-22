"""
Filter bar widget for the dashboard screen.

Provides UI controls for filtering and searching items.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label, Select, Static

from ...models import ItemStatus, ItemType, Priority


class FilterBar(Container):
    """Widget providing filtering and searching capabilities for work items."""
    
    DEFAULT_CSS = """
    FilterBar {
        layout: horizontal;
        height: 3;
        margin: 0 0 1 0;
        background: $panel;
        padding: 0 1;
    }
    
    #type_filter {
        width: 15;
    }
    
    #search_input {
        width: 30;
    }
    
    .filter-label {
        padding: 1 1 0 0;
        color: $text-muted;
    }
    
    .status-button {
        margin: 0 1 0 0;
    }
    
    .status-button.selected {
        background: $accent;
    }
    
    #clear_filters {
        margin: 0 0 0 1;
    }
    """
    
    class FilterChanged(Message):
        """Message sent when filters are changed."""
        
        def __init__(
            self, 
            item_type: str = None, 
            search_text: str = None,
            status: str = None,
            priority: str = None
        ) -> None:
            self.item_type = item_type
            self.search_text = search_text
            self.status = status
            self.priority = priority
            super().__init__()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_type = None
        self._current_search = ""
        self._current_status = None
        self._current_priority = None
        
    def compose(self) -> ComposeResult:
        """Compose the filter bar widgets."""
        # Type filter dropdown
        yield Label("Type:", classes="filter-label")
        
        yield Select(
            [(t.value, t.name) for t in ItemType],
            prompt="All Types",
            id="type_filter",
        )
        
        # Search input
        yield Label("Search:", classes="filter-label")
        yield Input(placeholder="Search titles...", id="search_input")
        
        # Status toggle buttons
        with Horizontal(id="status_buttons"):
            yield Label("Status:", classes="filter-label")
            for status in ItemStatus:
                yield Button(
                    status.name.replace("_", " ").title(),
                    id=f"status_{status.value}",
                    classes="status-button",
                )
        
        # Clear filters button
        yield Button("Clear Filters", id="clear_filters", variant="primary")
        
    def on_mount(self) -> None:
        """Set up event handlers when the widget is mounted."""
        # Focus the search input by default
        self.query_one("#search_input").focus()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle changes to the search input."""
        if event.input.id == "search_input":
            self._current_search = event.value
            self._emit_filter_changed()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle changes to the type filter dropdown."""
        if event.select.id == "type_filter":
            self._current_type = event.value
            self._emit_filter_changed()
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "clear_filters":
            self._clear_all_filters()
        elif button_id.startswith("status_"):
            self._toggle_status_button(event.button)
    
    def _toggle_status_button(self, button: Button) -> None:
        """Toggle a status button's selected state."""
        status_value = button.id.replace("status_", "")
        
        # Toggle between selected and not selected
        if "selected" in button.classes:
            button.remove_class("selected")
            self._current_status = None
        else:
            # First remove selected class from all status buttons
            for status_btn in self.query("Button.status-button"):
                status_btn.remove_class("selected")
                
            # Then add selected class to this button
            button.add_class("selected")
            self._current_status = status_value
            
        self._emit_filter_changed()
    
    def _clear_all_filters(self) -> None:
        """Clear all active filters."""
        # Reset type dropdown
        type_select = self.query_one("#type_filter", Select)
        type_select.value = None
        
        # Clear search input
        search_input = self.query_one("#search_input", Input)
        search_input.value = ""
        
        # Deselect all status buttons
        for status_btn in self.query("Button.status-button"):
            status_btn.remove_class("selected")
            
        # Reset internal state
        self._current_type = None
        self._current_search = ""
        self._current_status = None
        self._current_priority = None
        
        # Emit event with cleared filters
        self._emit_filter_changed()
        
    def _emit_filter_changed(self) -> None:
        """Emit a FilterChanged event with current filter values."""
        self.post_message(
            self.FilterChanged(
                item_type=self._current_type,
                search_text=self._current_search,
                status=self._current_status,
                priority=self._current_priority
            )
        ) 