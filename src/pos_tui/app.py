"""
Main application file for the POS Textual UI.

This module contains the POSTUI class which is the main entry point
for the Textual-based interface.
"""

import asyncio
from functools import partial
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane
from textual import log
from textual.binding import Binding

from ..storage import WorkSystem
from .screens import DashboardScreen, LinkTreeScreen, NewItemScreen, ShortcutsScreen
from .screens.debug_screen import DebugScreen
from .styles.theme import ThemeManager, ThemeType
from .widgets import CommandItem, CommandPalette, NotificationCenter
from .workers import DBConnectionManager


class POSTUI(App):
    """Main Textual UI application for the Personal Operating System."""

    # Path to CSS file relative to this file
    CSS_PATH = Path(__file__).parent / "styles" / "app.css"
    TITLE = "Personal Operating System (POS)"

    def __init__(self, *args, **kwargs):
        """Initialize the Textual UI application."""
        super().__init__(*args, **kwargs)
        self.work_system = WorkSystem()
        
        # Initialize database connection manager
        db_path = Path(__file__).parents[2] / "data" / "db" / "work_items.db"
        self.db_manager = DBConnectionManager(db_path)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self)
        
        # Initialize settings storage
        self._settings: Dict[str, Union[str, int, bool, dict]] = {}
        
    # Update bindings to Textual 3.x format
    BINDINGS = [
        Binding("1", "switch_tab('dashboard')", "Dashboard"),
        Binding("2", "switch_tab('new-item')", "New Item"),
        Binding("3", "switch_tab('link-tree')", "Link Tree"),
        Binding("ctrl+p", "toggle_command_palette", "Command Palette"),
        Binding("f1", "show_shortcuts", "Shortcuts"),
        Binding("t", "toggle_theme", "Toggle Theme"),
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
        
        # Re-enable command palette
        yield CommandPalette(id="command_palette")
        
        # Add notification center
        yield NotificationCenter(id="notification_center")

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to the given tab in TabbedContent."""
        log(f"action_switch_tab called with tab_id: {tab_id}")
        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = tab_id

    def on_mount(self) -> None:
        """Handle the app mount event."""
        self.title = f"POS v{self._get_version()}"
        
        # Register commands
        self._register_commands()
        
        # Load user settings
        self._load_settings()
        
        # Log app startup
        log("App mounted successfully")
        print("App mounted successfully")
    
    def _register_commands(self) -> None:
        """Register commands with the command palette."""
        command_palette = self.query_one("#command_palette", CommandPalette)
        
        # Navigation commands
        command_palette.register_commands([
            CommandItem(
                "Dashboard", 
                "Switch to the dashboard screen", 
                lambda: self.action_switch_tab("dashboard"),
                category="Navigation",
                shortcut="1"
            ),
            CommandItem(
                "New Item", 
                "Create a new work item", 
                lambda: self.action_switch_tab("new-item"),
                category="Navigation",
                shortcut="2"
            ),
            CommandItem(
                "Link Tree", 
                "View item relationships as a tree", 
                lambda: self.action_switch_tab("link-tree"),
                category="Navigation",
                shortcut="3"
            ),
            CommandItem(
                "Keyboard Shortcuts", 
                "View all keyboard shortcuts", 
                self.action_show_shortcuts,
                category="Help",
                shortcut="F1"
            ),
        ])
        
        # Theme commands
        command_palette.register_commands([
            CommandItem(
                "Toggle Theme", 
                "Switch between light and dark themes", 
                self.action_toggle_theme,
                category="Appearance",
                shortcut="T"
            ),
            CommandItem(
                "Dark Theme", 
                "Switch to dark theme", 
                lambda: self.theme_manager.set_theme(ThemeType.DARK),
                category="Appearance"
            ),
            CommandItem(
                "Light Theme", 
                "Switch to light theme", 
                lambda: self.theme_manager.set_theme(ThemeType.LIGHT),
                category="Appearance"
            ),
        ])
        
        # Item commands
        command_palette.register_commands([
            CommandItem(
                "New Item", 
                "Create a new work item", 
                lambda: self.action_switch_tab("new-item"),
                category="Items",
                aliases=["create", "add"],
                shortcut="2"
            ),
        ])

    def _get_version(self) -> str:
        """Get the application version."""
        try:
            from .. import __version__

            return __version__
        except (ImportError, AttributeError):
            return "0.2.0"
    
    def _load_settings(self) -> None:
        """Load user settings from storage."""
        # In a real implementation, this would load from a settings file
        # For now, we'll just use defaults
        self._settings = {
            "theme": "dark",
            "filters": {},
            "recent_items": [],
        }
        
    def _save_settings(self) -> None:
        """Save user settings to storage."""
        # In a real implementation, this would save to a settings file
        pass
    
    def action_toggle_command_palette(self) -> None:
        """Toggle the command palette visibility."""
        log("action_toggle_command_palette called")
        command_palette = self.query_one("#command_palette", CommandPalette)
        command_palette.toggle_visibility()
    
    def action_show_shortcuts(self) -> None:
        """Show the keyboard shortcuts screen."""
        log("action_show_shortcuts called")
        self.push_screen(ShortcutsScreen())
    
    def action_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        log("action_toggle_theme called")
        self.theme_manager.toggle_theme()
        
        # Update settings
        theme_name = "light" if self.theme_manager.current_theme == ThemeType.LIGHT else "dark"
        self._settings["theme"] = theme_name
        self._save_settings()
        
        # Show notification
        self.notify_info(f"Switched to {theme_name} theme")
    
    def notify_error(self, message: str, auto_dismiss: Optional[float] = 8.0) -> None:
        """Show an error notification.
        
        Args:
            message: The error message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
        """
        notification_center = self.query_one("#notification_center", NotificationCenter)
        notification_center.error(message, auto_dismiss)
    
    def notify_warning(self, message: str, auto_dismiss: Optional[float] = 5.0) -> None:
        """Show a warning notification.
        
        Args:
            message: The warning message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
        """
        notification_center = self.query_one("#notification_center", NotificationCenter)
        notification_center.warning(message, auto_dismiss)
    
    def notify_success(self, message: str, auto_dismiss: Optional[float] = 3.0) -> None:
        """Show a success notification.
        
        Args:
            message: The success message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
        """
        notification_center = self.query_one("#notification_center", NotificationCenter)
        notification_center.success(message, auto_dismiss)
    
    def notify_info(self, message: str, auto_dismiss: Optional[float] = 5.0) -> None:
        """Show an info notification.
        
        Args:
            message: The info message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
        """
        notification_center = self.query_one("#notification_center", NotificationCenter)
        notification_center.info(message, auto_dismiss)
            
    async def run_worker(self, worker_class, callback=None, error_callback=None, **kwargs):
        """Run a worker thread and handle its result via callbacks.
        
        This method creates and runs a worker in a background thread, then
        processes the result asynchronously without blocking the UI.
        
        Args:
            worker_class: The worker class to instantiate
            callback: Function to call with the worker's result
            error_callback: Function to call if the worker raises an exception
            **kwargs: Parameters to pass to the worker's run method
            
        Returns:
            The created worker instance
        """
        # Create the worker with callbacks
        worker = worker_class(
            callback=partial(self._handle_worker_result, callback),
            error_callback=partial(self._handle_worker_error, error_callback),
        )
        
        # Start the worker with the provided parameters
        worker.start(**kwargs)
        
        return worker
    
    def _handle_worker_result(self, callback, result):
        """Handle worker results by dispatching to the provided callback.
        
        Args:
            callback: The callback function to call with the result
            result: The result returned by the worker
        """
        if callback:
            # Schedule the callback on the event loop
            asyncio.create_task(self._call_callback(callback, result))
    
    def _handle_worker_error(self, error_callback, error, traceback_str):
        """Handle worker errors by dispatching to the provided error callback.
        
        Args:
            error_callback: The error callback function to call
            error: The exception raised by the worker
            traceback_str: The traceback as a string
        """
        # Show error notification
        self.notify_error(f"Error: {str(error)}")
        
        if error_callback:
            # Schedule the error callback on the event loop
            asyncio.create_task(self._call_callback(error_callback, error, traceback_str))
    
    async def _call_callback(self, callback, *args, **kwargs):
        """Call a callback function, handling both sync and async callbacks.
        
        Args:
            callback: The callback function to call
            *args: Positional arguments for the callback
            **kwargs: Keyword arguments for the callback
        """
        if asyncio.iscoroutinefunction(callback):
            await callback(*args, **kwargs)
        else:
            callback(*args, **kwargs)
            
    def on_unmount(self) -> None:
        """Close database connections when the app is unmounted."""
        self.db_manager.close_all()
        
        # Save settings
        self._save_settings()


def main() -> None:
    """Run the Textual UI application."""
    app = POSTUI()
    app.run()


if __name__ == "__main__":
    main()
