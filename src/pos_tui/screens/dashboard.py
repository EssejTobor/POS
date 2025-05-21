from textual.app import ComposeResult
from textual.containers import Container

from ..models import ItemStatus, ItemType
from ..widgets import FilterBar, ItemTable


class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    def compose(self) -> ComposeResult:
        yield FilterBar(id="filter_bar")
        yield ItemTable(id="dashboard_table")

    def on_mount(self) -> None:
        self._load_items()

    def _load_items(self) -> None:
        filters = self.query_one("#filter_bar", FilterBar).get_filters()
        ws = self.app.work_system
        items = ws.get_filtered_items(
            item_type=ItemType(filters["item_type"]) if filters["item_type"] else None,
            status=ItemStatus(filters["status"]) if filters["status"] else None,
            search_text=filters["search_text"],
        )
        self.query_one(ItemTable).load_items(items)

    def on_filter_bar_filters_changed(self, message: FilterBar.FiltersChanged) -> None:
        self._load_items()

    def on_item_table_sort_requested(self, message: ItemTable.SortRequested) -> None:
        table = self.query_one(ItemTable)
        table.sort_by(message.column)
