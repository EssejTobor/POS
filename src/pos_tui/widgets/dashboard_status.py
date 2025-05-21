from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static


class DashboardStatus(Static):
    """Display counts for incomplete and total items."""

    incomplete: int = reactive(0)
    total: int = reactive(0)

    def render(self) -> str:  # pragma: no cover - simple rendering
        return f"Incomplete: {self.incomplete} / {self.total}"

    def set_counts(self, *, incomplete: int, total: int) -> None:
        """Update the displayed counts."""
        self.incomplete = incomplete
        self.total = total
