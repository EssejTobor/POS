"""
Main application file for the POS Textual UI.

This module contains the POSTUI class which is the main entry point
for the Textual-based interface.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from ..storage import WorkSystem
from ..models import WorkItem
from .commands import Command, CommandRegistry
from .screens import DashboardScreen, LinkTreeScreen, NewItemScreen
from .widgets import CommandPalette
from .preferences import load_preferences, save_preferences
from .workers import WorkerPool, DatabaseWorker, ItemFetchWorker
from .workers.base import BaseWorker
from .workers.db import DBConnectionManager


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
        self.worker_pool = WorkerPool()
        self.connection_manager = DBConnectionManager(self.work_system.db.db_path)
        self.breadcrumb_history: list[WorkItem] = []
        prefs = load_preferences()
        self._theme_name = prefs.get("theme", "dark")

    BINDINGS = [
        ("1", "switch_tab('dashboard')", "Dashboard"),
        ("2", "switch_tab('new-item')", "New Item"),
        ("3", "switch_tab('link-tree')", "Link Tree"),
        ("ctrl+p", "toggle_palette()", "Command Palette"),
        ("ctrl+t", "toggle_theme()", "Theme"),
        ("?", "open_help()", "Help"),
    ]

    def schedule_worker(self, worker: BaseWorker, name: str | None = None) -> str:
        """Run a worker and track it in the worker pool."""
        worker_id = self.run_worker(worker, name or worker.name)
        self.worker_pool.add(worker)
        return worker_id

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

    def register_detail(self, item: WorkItem) -> None:
        """Add ``item`` to breadcrumb history."""
        if self.breadcrumb_history and self.breadcrumb_history[-1].id == item.id:
            return
        self.breadcrumb_history.append(item)

    def unregister_detail(self, item: WorkItem) -> None:
        """Remove ``item`` from breadcrumb history if it's the current entry."""
        if self.breadcrumb_history and self.breadcrumb_history[-1].id == item.id:
            self.breadcrumb_history.pop()

    def action_toggle_theme(self) -> None:
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        prefs = load_preferences()
        prefs["theme"] = self._theme_name
        save_preferences(prefs)
        theme_file = Path(__file__).parent / "styles" / f"theme_{self._theme_name}.css"
        if theme_file.is_file():
            self.load_css(theme_file)
            self.refresh()

    def action_open_help(self) -> None:
        from .screens.shortcuts import ShortcutHelpScreen

        self.push_screen(ShortcutHelpScreen())

    def on_mount(self) -> None:
        """Handle the app mount event."""
        self.title = f"POS v{self._get_version()}"
        theme_file = Path(__file__).parent / "styles" / f"theme_{self._theme_name}.css"
        if theme_file.is_file():
            self.load_css(theme_file)
        # Register some basic commands
        self.command_registry.register_many(
            [
                Command(
                    "dashboard",
                    "Switch to Dashboard",
                    lambda: self.action_switch_tab("dashboard"),
                    "navigation",
                    aliases=["home"],
                ),
                Command(
                    "new_item",
                    "Create New Item",
                    lambda: self.action_switch_tab("new-item"),
                    "navigation",
                    aliases=["task", "new"],
                ),
                Command(
                    "link_tree",
                    "View Link Tree",
                    lambda: self.action_switch_tab("link-tree"),
                    "navigation",
                ),
                Command(
                    "toggle_theme",
                    "Toggle Theme",
                    self.action_toggle_theme,
                    "system",
                ),
                Command(
                    "help",
                    "Keyboard Shortcuts",
                    self.action_open_help,
                    "system",
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
