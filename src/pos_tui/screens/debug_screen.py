"""
Debug screen for testing key events and interactions.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static
from textual import log
from textual.binding import Binding

class DebugScreen(Screen):
    """A simple screen for debugging key events and widget interactions."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "debug_key", "Debug Key Press"),
        Binding("f", "focus_button", "Focus Button"),
        Binding("escape", "app.pop_screen", "Return to Main"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        
        with Vertical(id="debug-container"):
            yield Static("Debug Screen - Press keys to test events", id="debug-title")
            yield Static("Key Events:", id="key-events-title")
            yield Static("No key events yet", id="key-events")
            yield Button("Test Button", id="test-button", variant="primary")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the screen mount event."""
        log("Debug screen mounted")
        print("Debug screen mounted")
        
        # Focus the button to make sure something has focus
        self.query_one("#test-button").focus()
        
        # Log a test event
        self.log_key_event("Screen mounted")
    
    def action_debug_key(self) -> None:
        """Test action for the 'd' key binding."""
        log("Debug key pressed")
        print("Debug key pressed")
        
        # Update the key events display
        self.log_key_event("d (via action)")
    
    def action_focus_button(self) -> None:
        """Action to focus the test button."""
        log("Focus button action called")
        print("Focus button action called")
        
        # Focus the button
        self.query_one("#test-button").focus()
        
        # Update the key events display
        self.log_key_event("f (via action)")
    
    def log_key_event(self, key: str) -> None:
        """Log a key event to the display."""
        key_events = self.query_one("#key-events", Static)
        current_text = key_events.renderable
        if current_text == "No key events yet":
            current_text = ""
        new_text = f"{current_text}\n{key}" if current_text else key
        key_events.update(new_text)
    
    def on_key(self, event) -> None:
        """Handle key events."""
        key_pressed = event.key
        log(f"Debug screen received key: {key_pressed}")
        print(f"Debug screen received key: {key_pressed}")
        
        # Log the key event
        self.log_key_event(f"Key: {key_pressed}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        log("Button pressed")
        print("Button pressed")
        
        # Update the key events display
        self.log_key_event("Button pressed") 