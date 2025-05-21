from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.events import Mount

from ..widgets import ItemTable


class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    BINDINGS = [("r", "refresh", "Refresh Data")]

    def compose(self) -> ComposeResult:
        yield ItemTable(id="dashboard_table")

    async def on_mount(self, event: Mount) -> None:
        table = self.query_one(ItemTable)
        await table.refresh_data()

    async def action_refresh(self) -> None:
        table = self.query_one(ItemTable)
        await table.refresh_data()
