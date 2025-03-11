from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Container
from textual import events
import logging

logger = logging.getLogger(__name__)

class ErrorScreen(Screen):
    """Error display screen"""
    
    def __init__(self, message: str, error_type: str = "Error"):
        super().__init__()
        self.message = message
        self.error_type = error_type
        logger.debug(f"Error screen created: {error_type} - {message}")
    
    def compose(self):
        """Compose the error screen layout"""
        yield Container(
            Static(f"{self.error_type}", classes="title error-title"),
            Static(self.message, classes="error-message"),
            Button("Close", id="close-error"),
            id="error-screen"
        )
    
    def on_button_pressed(self, event: events.Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "close-error":
            logger.debug("Error screen closed")
            self.app.pop_screen() 