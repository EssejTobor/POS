"""Simple command registry and data structures for the POS TUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Callable, Dict, Iterable, List


@dataclass
class Command:
    """A single executable command."""

    name: str
    description: str
    action: Callable[[], None]
    category: str = "general"
    aliases: list[str] = field(default_factory=list)


class CommandRegistry:
    """Registry for storing and retrieving commands."""

    def __init__(self) -> None:
        self.commands: Dict[str, Command] = {}
        self.alias_map: Dict[str, str] = {}
        self.history: List[str] = []

    # --------------------------------------------------------------
    # Registration helpers
    # --------------------------------------------------------------
    def register(self, command: Command) -> None:
        """Register a command with the registry."""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.alias_map[alias] = command.name

    def register_many(self, commands: Iterable[Command]) -> None:
        for cmd in commands:
            self.register(cmd)

    # --------------------------------------------------------------
    # Retrieval helpers
    # --------------------------------------------------------------
    def get(self, name: str) -> Command | None:
        if name in self.commands:
            return self.commands[name]
        alias_target = self.alias_map.get(name)
        if alias_target:
            return self.commands.get(alias_target)
        return None

    def get_commands_by_category(self, category: str) -> List[Command]:
        return [c for c in self.commands.values() if c.category == category]

    def all_commands(self) -> List[Command]:
        return list(self.commands.values())

    def search(self, term: str) -> List[Command]:
        """Return commands matching ``term`` using fuzzy search."""
        if not term:
            return self.all_commands()

        def score(cmd: Command) -> float:
            texts = [cmd.name, *cmd.aliases]
            return max(
                SequenceMatcher(None, term, t.lower()).ratio() for t in texts
            )

        scored = [(score(cmd), cmd) for cmd in self.commands.values()]
        scored = [pair for pair in scored if pair[0] > 0]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [cmd for _, cmd in scored]

    # --------------------------------------------------------------
    # History helpers
    # --------------------------------------------------------------
    def add_history(self, name: str) -> None:
        if name in self.commands:
            self.history.append(name)

    def recent_history(self, limit: int = 10) -> List[str]:
        return self.history[-limit:]
