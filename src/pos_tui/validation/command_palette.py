from __future__ import annotations

from src.pos_tui.validation import ValidationProtocol
from src.pos_tui.validation.ui_components import UIComponentSimulator
from src.pos_tui.commands import CommandRegistry, Command
from src.pos_tui.widgets.command_palette import CommandPalette


class CommandPaletteValidation(ValidationProtocol):
    """Validate command palette fuzzy search and alias behavior."""

    def __init__(self) -> None:
        super().__init__("command_palette")

    def _run_validation(self) -> None:
        registry = CommandRegistry()
        called = []
        registry.register(
            Command(
                "dashboard",
                "Open dashboard",
                lambda: called.append("dash"),
                "navigation",
                aliases=["home"],
            )
        )
        registry.register(
            Command(
                "new_item",
                "Create item",
                lambda: called.append("new"),
                "actions",
                aliases=["task"],
            )
        )

        results = registry.search("hme")
        if results and results[0].name == "dashboard":
            self.result.add_pass("Fuzzy search finds alias")
        else:
            self.result.add_fail("Fuzzy search failed")

        res2 = registry.search("task")
        if res2 and res2[0].name == "new_item":
            self.result.add_pass("Search by alias returns command")
        else:
            self.result.add_fail("Alias search failed")

