"""
Command palette widget for the Textual UI.

Provides a searchable, keyboard-activated command interface.
"""

from typing import Callable, Dict, List, Optional, Union

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.widgets import Input, Label, Static
from textual.css.query import NoMatches
from textual import log


class CommandItem:
    """A command that can be executed from the command palette."""
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        callback: Callable, 
        category: str = "General", 
        aliases: List[str] = None,
        shortcut: str = None
    ):
        """Initialize a command item.
        
        Args:
            name: The name of the command
            description: A brief description of what the command does
            callback: Function to call when the command is executed
            category: Category for grouping commands
            aliases: Alternative names that can be used to find this command
            shortcut: Keyboard shortcut for this command (if any)
        """
        self.name = name
        self.description = description
        self.callback = callback
        self.category = category
        self.aliases = aliases or []
        self.shortcut = shortcut
        
    def matches(self, query: str) -> bool:
        """Check if this command matches the search query.
        
        Args:
            query: The search string to match against
            
        Returns:
            True if the command matches the query
        """
        query = query.lower()
        
        # Check name
        if query in self.name.lower():
            return True
            
        # Check description
        if query in self.description.lower():
            return True
            
        # Check aliases
        for alias in self.aliases:
            if query in alias.lower():
                return True
                
        # Check category
        if query in self.category.lower():
            return True
                
        return False


class CommandGroup(Static):
    """A group of related commands displayed in the command palette."""
    
    DEFAULT_CSS = """
    CommandGroup {
        width: 100%;
    }
    
    .group-header {
        background: $panel-darken-1;
        color: $text-muted;
        padding: 0 1;
    }
    
    .command-item {
        padding: 0 1;
        height: 1;
    }
    
    .command-item:hover {
        background: $boost;
    }
    
    .command-item.selected {
        background: $accent;
        color: $text;
    }
    
    .command-shortcut {
        color: $text-muted;
        text-align: right;
    }
    """
    
    def __init__(self, category: str, commands: List[CommandItem]) -> None:
        """Initialize a command group.
        
        Args:
            category: The category name
            commands: List of commands in this group
        """
        super().__init__()
        self.category = category
        self.commands = commands
        
    def compose(self) -> ComposeResult:
        """Compose the command group."""
        yield Label(f"[b]{self.category}[/b]", classes="group-header")
        
        for command in self.commands:
            shortcut_text = f"[{command.shortcut}]" if command.shortcut else ""
            yield Static(
                f"{command.name} - {command.description} {shortcut_text}",
                classes="command-item",
                id=f"cmd_{id(command)}"
            )


class CommandPalette(Container):
    """A searchable command palette activated by keyboard shortcut."""
    
    DEFAULT_CSS = """
    CommandPalette {
        background: $surface;
        border: round $primary;
        width: 60;
        height: auto;
        max-height: 20;
        padding: 1;
        margin: 1 0;
        dock: top;
        display: none;
    }
    
    CommandPalette.visible {
        display: block;
    }
    
    #search_input {
        width: 100%;
        margin-bottom: 1;
    }
    
    #commands_container {
        height: auto;
        max-height: 15;
    }
    
    #no_results {
        text-align: center;
        padding: 1;
        color: $text-muted;
    }
    """
    
    class CommandExecuted(Message):
        """Message sent when a command is executed."""
        
        def __init__(self, command: CommandItem) -> None:
            self.command = command
            super().__init__()
    
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the command palette."""
        super().__init__(*args, **kwargs)
        self.commands: List[CommandItem] = []
        self._visible = False
        self._selected_index = 0
        self._filtered_commands: List[CommandItem] = []
    
    def compose(self) -> ComposeResult:
        """Compose the command palette widgets."""
        yield Input(placeholder="Search commands... (Esc to close)", id="search_input")
        
        with VerticalScroll(id="commands_container"):
            # Commands will be populated dynamically
            yield Static("[i]No commands registered[/i]", id="no_results")
    
    def toggle_visibility(self) -> None:
        """Toggle the visibility of the command palette."""
        if self._visible:
            self.hide()
        else:
            self.show()
    
    def show(self) -> None:
        """Show the command palette and focus the search input."""
        if not self._visible:
            self.add_class("visible")
            self._visible = True
            self.query_one("#search_input").focus()
            # Reset search on show
            self.query_one("#search_input").value = ""
            self._update_command_list("")
    
    def hide(self) -> None:
        """Hide the command palette."""
        if self._visible:
            self.remove_class("visible")
            self._visible = False
    
    def register_command(self, command: CommandItem) -> None:
        """Register a command with the palette.
        
        Args:
            command: The command to register
        """
        self.commands.append(command)
        
    def register_commands(self, commands: List[CommandItem]) -> None:
        """Register multiple commands with the palette.
        
        Args:
            commands: List of commands to register
        """
        self.commands.extend(commands)
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle changes to the search input."""
        if event.input.id == "search_input":
            self._update_command_list(event.value)
    
    def _update_command_list(self, query: str) -> None:
        """Update the displayed commands based on the search query.
        
        Args:
            query: The search string
        """
        # Reset selected index
        self._selected_index = 0
        
        # Filter commands by query
        if not query:
            self._filtered_commands = self.commands
        else:
            self._filtered_commands = [cmd for cmd in self.commands if cmd.matches(query)]
            
        # Remove existing command groups
        commands_container = self.query_one("#commands_container")
        for child in commands_container.children:
            if isinstance(child, (CommandGroup, Static)):
                child.remove()
                
        # If no commands found, show message
        if not self._filtered_commands:
            commands_container.mount(Static("[i]No matching commands[/i]", id="no_results"))
            return
            
        # Group commands by category
        grouped_commands: Dict[str, List[CommandItem]] = {}
        for command in self._filtered_commands:
            if command.category not in grouped_commands:
                grouped_commands[command.category] = []
            grouped_commands[command.category].append(command)
            
        # Create and mount command groups
        for category, commands in grouped_commands.items():
            commands_container.mount(CommandGroup(category, commands))
            
        # Select the first command
        if self._filtered_commands:
            self._select_command_at_index(0)
    
    def _select_command_at_index(self, index: int) -> None:
        """Select the command at the given index.
        
        Args:
            index: The index of the command to select
        """
        # Limit index to valid range
        if not self._filtered_commands:
            return
            
        index = max(0, min(index, len(self._filtered_commands) - 1))
        self._selected_index = index
        
        # Remove selected class from all items
        try:
            for item in self.query(".command-item"):
                item.remove_class("selected")
        except NoMatches:
            return
            
        # Add selected class to current item
        selected_command = self._filtered_commands[self._selected_index]
        try:
            item = self.query_one(f"#cmd_{id(selected_command)}")
            item.add_class("selected")
            
            # Ensure the selected item is visible
            commands_container = self.query_one("#commands_container")
            commands_container.scroll_to_widget(item)
        except NoMatches:
            pass
    
    def on_key(self, event) -> None:
        """Handle key events for navigation and execution."""
        log(f"CommandPalette received key: {event.key}, visible: {self._visible}")
        
        if not self._visible:
            return
            
        if event.key == "escape":
            self.hide()
            event.prevent_default()
        elif event.key == "up":
            self._select_command_at_index(self._selected_index - 1)
            event.prevent_default()
        elif event.key == "down":
            self._select_command_at_index(self._selected_index + 1)
            event.prevent_default()
        elif event.key == "enter":
            self._execute_selected_command()
            event.prevent_default()
    
    def _execute_selected_command(self) -> None:
        """Execute the currently selected command."""
        if not self._filtered_commands or self._selected_index >= len(self._filtered_commands):
            return
            
        command = self._filtered_commands[self._selected_index]
        self.hide()
        
        # Execute the command
        command.callback()
        
        # Post message about execution
        self.post_message(self.CommandExecuted(command))
    
    def on_click(self, event) -> None:
        """Handle mouse clicks on command items."""
        if not self._visible:
            return
            
        target = event.target
        if hasattr(target, "id") and target.id and target.id.startswith("cmd_"):
            # Find the corresponding command
            cmd_id = int(target.id.replace("cmd_", ""))
            for i, command in enumerate(self._filtered_commands):
                if id(command) == cmd_id:
                    self._selected_index = i
                    self._execute_selected_command()
                    break 