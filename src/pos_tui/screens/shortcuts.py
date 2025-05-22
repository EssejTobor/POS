"""
Keyboard shortcuts reference screen.

Provides a searchable, categorized display of all keyboard shortcuts.
"""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Static


class ShortcutGroup(Container):
    """A group of related keyboard shortcuts."""
    
    DEFAULT_CSS = """
    ShortcutGroup {
        width: 100%;
        margin-bottom: 1;
    }
    
    .group-header {
        background: $panel-darken-1;
        color: $text-muted;
        padding: 0 1;
        text-align: center;
    }
    
    .shortcut-item {
        height: 1;
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
        padding: 0 1;
    }
    
    .shortcut-item:hover {
        background: $boost;
    }
    
    .shortcut-key {
        background: $boost;
        color: $text;
        text-align: right;
        padding-right: 1;
    }
    
    .shortcut-description {
        color: $text-muted;
        padding-left: 1;
    }
    """
    
    def __init__(self, category: str, shortcuts: list[tuple[str, str]]) -> None:
        """Initialize a shortcut group.
        
        Args:
            category: The category name
            shortcuts: List of shortcuts in this group as (key, description) tuples
        """
        super().__init__()
        self.category = category
        self.shortcuts = shortcuts
        
    def compose(self) -> ComposeResult:
        """Compose the shortcut group."""
        yield Label(f"[b]{self.category}[/b]", classes="group-header")
        
        for key, description in self.shortcuts:
            with Container(classes="shortcut-item"):
                yield Label(f"[b]{key}[/b]", classes="shortcut-key")
                yield Label(description, classes="shortcut-description")


class ShortcutsScreen(Screen):
    """Screen displaying keyboard shortcuts and their descriptions."""
    
    DEFAULT_CSS = """
    ShortcutsScreen {
        layout: vertical;
        background: $surface;
        padding: 1 2;
    }
    
    #shortcuts_header {
        background: $primary;
        color: $text;
        height: 3;
        padding: 1 2;
        text-align: center;
    }
    
    #search_container {
        height: 3;
        margin: 0 0 1 0;
    }
    
    #search_input {
        width: 100%;
    }
    
    #shortcuts_container {
        height: 1fr;
    }
    
    #back_button {
        dock: bottom;
        width: 100%;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("/", "focus_search", "Search"),
    ]
    
    def __init__(self) -> None:
        """Initialize the shortcuts screen."""
        super().__init__()
        self.shortcuts = self._get_shortcuts()
        
    def compose(self) -> ComposeResult:
        """Compose the shortcuts screen."""
        yield Static("[b]Keyboard Shortcuts[/b]", id="shortcuts_header")
        
        with Container(id="search_container"):
            yield Input(placeholder="Search shortcuts...", id="search_input")
        
        with VerticalScroll(id="shortcuts_container"):
            self._render_shortcuts("")
            
        yield Button("Back", id="back_button", variant="primary")
    
    def _get_shortcuts(self) -> dict[str, list[tuple[str, str]]]:
        """Get all keyboard shortcuts grouped by category.
        
        Returns:
            Dictionary mapping category names to lists of (key, description) tuples
        """
        return {
            "Navigation": [
                ("Tab", "Move focus to next element"),
                ("Shift+Tab", "Move focus to previous element"),
                ("1", "Switch to Dashboard tab"),
                ("2", "Switch to New Item tab"),
                ("3", "Switch to Link Tree tab"),
                ("Esc", "Close modal or go back"),
            ],
            "Command Palette": [
                ("Ctrl+P", "Open command palette"),
                ("Esc", "Close command palette"),
                ("Up/Down", "Navigate commands"),
                ("Enter", "Execute selected command"),
            ],
            "Dashboard": [
                ("N", "Create new item"),
                ("E", "Edit selected item"),
                ("D", "Delete selected item"),
                ("Enter", "View item details"),
                ("/", "Focus search box"),
            ],
            "Item Form": [
                ("Tab", "Move to next field"),
                ("Shift+Tab", "Move to previous field"),
                ("Enter", "Submit form"),
                ("Esc", "Cancel"),
            ],
            "Link Tree": [
                ("Arrow keys", "Navigate tree"),
                ("+", "Expand node"),
                ("-", "Collapse node"),
                ("Home", "Go to root node"),
                ("End", "Go to last visible node"),
            ],
        }
    
    def _render_shortcuts(self, search_query: str) -> None:
        """Render shortcuts filtered by the search query.
        
        Args:
            search_query: Text to filter shortcuts by
        """
        container = self.query_one("#shortcuts_container")
        
        # Remove existing shortcut groups
        for child in container.children:
            if isinstance(child, ShortcutGroup):
                child.remove()
        
        # Filter shortcuts by search query
        if not search_query:
            filtered_shortcuts = self.shortcuts
        else:
            search_query = search_query.lower()
            filtered_shortcuts = {}
            
            for category, shortcuts in self.shortcuts.items():
                matching_shortcuts = []
                
                for key, description in shortcuts:
                    if (search_query in key.lower() or 
                        search_query in description.lower() or
                        search_query in category.lower()):
                        matching_shortcuts.append((key, description))
                
                if matching_shortcuts:
                    filtered_shortcuts[category] = matching_shortcuts
        
        # Display message if no shortcuts match
        if not filtered_shortcuts:
            container.mount(Static("[i]No matching shortcuts found[/i]", classes="no-results"))
            return
        
        # Render filtered shortcuts
        for category, shortcuts in filtered_shortcuts.items():
            container.mount(ShortcutGroup(category, shortcuts))
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle changes to the search input."""
        if event.input.id == "search_input":
            self._render_shortcuts(event.value)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back_button":
            self.app.pop_screen()
    
    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search_input").focus() 