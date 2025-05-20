"""
Main application file for the POS Textual UI.

This module contains the POSTUI class which is the main entry point
for the Textual-based interface.
"""

import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, TabPane, TabbedContent

from ..storage import WorkSystem


class POSTUI(App):
    """Main Textual UI application for the Personal Operating System."""
    
    # Path to CSS file relative to this file
    CSS_PATH = Path(__file__).parent / "styles" / "app.css"
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
            from .. import __version__
            return __version__
        except (ImportError, AttributeError):
            return "0.2.0"


def main() -> None:
    """Run the Textual UI application."""
    app = POSTUI()
    app.run()


if __name__ == "__main__":
    main() 