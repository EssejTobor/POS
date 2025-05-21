"""
Main application file for the POS Textual UI.

This module contains the POSTUI class which is the main entry point
for the Textual-based interface.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from ..storage import WorkSystem
from .commands import Command, CommandRegistry
from .screens import DashboardScreen, LinkTreeScreen, NewItemScreen
from .widgets import CommandPalette


class POSTUI(App):
    """Main Textual UI application for the Personal Operating System."""

    # Path to CSS file relative to this file
    CSS_PATH = Path(__file__).parent / "styles" / "app.css"
    TITLE = "Personal Operating System (POS)"

    def __init__(self, *args, **kwargs):
        """Initialize the Textual UI application."""
        super().__init__(*args, **kwargs)
        self.work_system = WorkSystem()
        self.command_registry = CommandRegistry()

    BINDINGS = [
        ("1", "switch_tab('dashboard')", "Dashboard"),
        ("2", "switch_tab('new-item')", "New Item"),
        ("3", "switch_tab('link-tree')", "Link Tree"),
        ("ctrl+p", "toggle_palette()", "Command Palette"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()

        with TabbedContent(id="tabs"):
            with TabPane("Dashboard", id="dashboard"):
                yield DashboardScreen()

            with TabPane("New Item", id="new-item"):
                yield NewItemScreen()

            with TabPane("Link Tree", id="link-tree"):
                yield LinkTreeScreen()

        yield Footer()
        self.palette = CommandPalette(self.command_registry, id="command_palette")
        yield self.palette

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to the given tab in TabbedContent."""
        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = tab_id

    def action_toggle_palette(self) -> None:
        if self.palette.visible:
            self.palette.close()
        else:
            self.palette.open()

    def on_mount(self) -> None:
        """Handle the app mount event."""
        self.title = f"POS v{self._get_version()}"
        # Register some basic commands
        self.command_registry.register_many(
            [
                Command(
                    "dashboard",
                    "Switch to Dashboard",
                    lambda: self.action_switch_tab("dashboard"),
                    "navigation",
                ),
                Command(
                    "new_item",
                    "Create New Item",
                    lambda: self.action_switch_tab("new-item"),
                    "navigation",
                ),
                Command(
                    "link_tree",
                    "View Link Tree",
                    lambda: self.action_switch_tab("link-tree"),
                    "navigation",
                ),
            ]
        )

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
