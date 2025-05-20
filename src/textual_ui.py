"""
Textual UI for the Personal Operating System (POS).

This module provides the Terminal User Interface (TUI) for the POS application
using the Textual framework. It is the primary interface for interacting
with the application's functionality.
"""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, TabPane, TabbedContent

from .storage import WorkSystem


class POSTUI(App):
    """Main Textual UI application for the Personal Operating System."""
    
    CSS_PATH = "textual_ui.css"
    TITLE = "Personal Operating System (POS)"
    
    def __init__(self, *args, **kwargs):
        """Initialize the Textual UI application."""
        super().__init__(*args, **kwargs)
        self.work_system = WorkSystem()
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()
        
        with TabbedContent():
            with TabPane("Dashboard", id="dashboard"):
                yield Static("Dashboard - Items overview will display here")
            
            with TabPane("New Item", id="new-item"):
                yield Static("Item entry form will be implemented here")
            
            with TabPane("Link Tree", id="link-tree"):
                yield Static("Link visualization will be implemented here")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the app mount event."""
        self.title = f"POS v{self._get_version()}"
    
    def _get_version(self) -> str:
        """Get the application version."""
        try:
            from . import __version__
            return __version__
        except (ImportError, AttributeError):
            return "0.2.0"


def main() -> None:
    """Run the Textual UI application."""
    app = POSTUI()
    app.run()


if __name__ == "__main__":
    main() 