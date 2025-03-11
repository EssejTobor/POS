from textual.screen import Screen
from textual.widgets import Static, Button, Label
from textual.containers import Container, VerticalScroll
from textual import events
import logging

logger = logging.getLogger(__name__)

class BaseScreen(Screen):
    """Base screen with common functionality for all screens"""
    
    def action_toggle_dark(self) -> None:
        """Toggle dark mode"""
        self.app.dark = not self.app.dark
        logger.info(f"Dark mode toggled to {self.app.dark}")
    
    def action_quit(self) -> None:
        """Quit the application"""
        logger.info("Quitting application")
        self.app.exit()
    
    def action_back(self) -> None:
        """Go back to previous screen"""
        logger.info("Going back to previous screen")
        self.app.pop_screen()
    
    def show_error(self, message: str, error_type: str = "Error") -> None:
        """Show error message using the app's error handler"""
        logger.error(f"{error_type}: {message}")
        self.app.handle_error(Exception(message), error_type) 