"""Simple command registry and data structures for the POS TUI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List


@dataclass
class Command:
    """A single executable command."""

    name: str
    description: str
    action: Callable[[], None]
    category: str = "general"


class CommandRegistry:
    """Registry for storing and retrieving commands."""

    def __init__(self) -> None:
        self.commands: Dict[str, Command] = {}
        self.history: List[str] = []

    # --------------------------------------------------------------
    # Registration helpers
    # --------------------------------------------------------------
    def register(self, command: Command) -> None:
        """Register a command with the registry."""
        self.commands[command.name] = command

    def register_many(self, commands: Iterable[Command]) -> None:
        for cmd in commands:
            self.register(cmd)

    # --------------------------------------------------------------
    # Retrieval helpers
    # --------------------------------------------------------------
    def get(self, name: str) -> Command | None:
        return self.commands.get(name)

    def get_commands_by_category(self, category: str) -> List[Command]:
        return [c for c in self.commands.values() if c.category == category]

    def all_commands(self) -> List[Command]:
        return list(self.commands.values())

    # --------------------------------------------------------------
    # History helpers
    # --------------------------------------------------------------
    def add_history(self, name: str) -> None:
        if name in self.commands:
            self.history.append(name)

    def recent_history(self, limit: int = 10) -> List[str]:
        return self.history[-limit:]
