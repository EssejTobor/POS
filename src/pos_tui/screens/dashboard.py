from textual.app import ComposeResult
from textual.containers import Container

from ..widgets import ItemTable


class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    def compose(self) -> ComposeResult:
        yield ItemTable(id="dashboard_table")
