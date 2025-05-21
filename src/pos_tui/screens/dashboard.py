from textual.app import ComposeResult
from textual.containers import Container

from ..widgets import FilterBar, ItemTable


class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    def compose(self) -> ComposeResult:
        yield FilterBar(id="filter_bar")
        yield ItemTable(id="dashboard_table")

    def on_filter_bar_filter_changed(
        self, event: FilterBar.FilterChanged
    ) -> None:  # pragma: no cover - simple UI
        table = self.query_one(ItemTable)
        table.set_filters(
            item_type=event.item_type,
            status=event.status,
            search_text=event.search_text,
        )
