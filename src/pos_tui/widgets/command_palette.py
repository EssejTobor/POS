"""Simple command palette widget."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, ListItem, ListView, Static

from ..commands import Command, CommandRegistry


class PaletteItem(ListItem):
    """List item storing a command reference."""

    def __init__(self, command: Command, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.command = command


class CommandPalette(Container):
    """UI widget for searching and executing commands."""

    CSS_PATH = Path(__file__).parent.parent / "styles" / "command_palette.css"
    DEFAULT_CSS = CSS_PATH.read_text()

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
        current_cat = None
        for cmd in commands:
            if cmd.category != current_cat:
                current_cat = cmd.category
                header = ListItem(Static(current_cat.title()), classes="category", disabled=True)
                self.results.append(header)
            item = PaletteItem(cmd, Static(f"{cmd.name} - {cmd.description}"))
            self.results.append(item)

    # --------------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------------
    def on_input_changed(self, event: Input.Changed) -> None:
        if not self.visible:
            return
        term = event.value.lower()
        cmds = self.registry.search(term)
        self._refresh_results(cmds)

    def on_input_key(self, event: Input.Key) -> None:
        if event.key == "down" and self.results is not None:
            self.results.focus()
            event.stop()
        elif event.key == "escape":
            self.close()
            event.stop()
        elif event.key == "enter" and self.results is not None:
            # if only one command, execute it
            items = [it for it in self.results.children if isinstance(it, PaletteItem)]
            if len(items) == 1:
                cmd = items[0].command
                cmd.action()
                self.registry.add_history(cmd.name)
                self.close()
            event.stop()

    def on_list_view_key(self, event: ListView.Key) -> None:
        if event.key == "escape":
            self.close()
            event.stop()
        elif event.key == "enter" and isinstance(event.item, PaletteItem):
            cmd = event.item.command
            cmd.action()
            self.registry.add_history(cmd.name)
            self.close()
