from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable


class ShortcutHelpScreen(Screen):
    """Screen listing common keyboard shortcuts."""

    BINDINGS = [("escape", "app.pop_screen", "Close")]

    def compose(self) -> ComposeResult:
        table = DataTable(id="shortcut_table")
        table.add_columns("Key", "Description")
        rows = [
            ("1", "Switch to Dashboard"),
            ("2", "Switch to New Item"),
            ("3", "Switch to Link Tree"),
            ("Ctrl+P", "Toggle Command Palette"),
            ("Ctrl+T", "Toggle Theme"),
            ("?", "Show this help"),
            ("Ctrl+S", "Save Item Form"),
            ("Ctrl+C/Esc", "Cancel Form"),
            ("V/E/D", "Table row actions"),
        ]
        for key, desc in rows:
            table.add_row(key, desc)
        yield table
