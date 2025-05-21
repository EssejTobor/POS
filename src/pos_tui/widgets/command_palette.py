"""Simple command palette widget."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, ListItem, ListView, Static

from ..commands import Command, CommandRegistry


class CommandPalette(Container):
    """UI widget for searching and executing commands."""

    DEFAULT_CSS = Path(__file__).with_name("command_palette.css")

    def __init__(self, registry: CommandRegistry, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.registry = registry
        self.results: ListView | None = None
        self.visible = False

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type a command", id="palette_input")
        self.results = ListView(id="palette_results")
        yield self.results

    def on_mount(self) -> None:
        self.display = False

    # --------------------------------------------------------------
    # Palette control
    # --------------------------------------------------------------
    def open(self) -> None:
        self.display = True
        self.visible = True
        self.query_one("#palette_input", Input).value = ""
        self.query_one("#palette_input", Input).focus()
        self._refresh_results(self.registry.all_commands())

    def close(self) -> None:
        self.display = False
        self.visible = False

    # --------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------
    def _refresh_results(self, commands: Iterable[Command]) -> None:
        assert self.results is not None
        self.results.clear()
        for cmd in commands:
            self.results.append(ListItem(Static(f"{cmd.name} - {cmd.description}")))

    # --------------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------------
    def on_input_changed(self, event: Input.Changed) -> None:
        if not self.visible:
            return
        term = event.value.lower()
        cmds = [c for c in self.registry.all_commands() if term in c.name.lower()]
        self._refresh_results(cmds)
