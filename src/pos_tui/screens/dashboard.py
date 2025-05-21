from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import LoadingIndicator

from ..widgets import FilterBar, ItemTable


class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    BINDINGS = [
        ("r", "refresh", "Refresh Items"),
    ]

    def compose(self) -> ComposeResult:

        yield LoadingIndicator(id="loading")
        yield ItemTable(id="dashboard_table")

    def on_mount(self) -> None:
        self.query_one(LoadingIndicator).display = False
        self.refresh()

    def action_refresh(self) -> None:
        self.refresh()

    # --------------------------------------------------------------
    # Data Loading
    # --------------------------------------------------------------
    def refresh(self) -> None:
        """Fetch items from the database asynchronously."""
        loading = self.query_one(LoadingIndicator)
        table = self.query_one(ItemTable)
        table.display = False
        loading.display = True
        self.run_worker(self._fetch_items, thread=True)

    def _fetch_items(self) -> None:
        items = self.app.work_system.get_incomplete_items()
        self.call_from_thread(self._apply_items, items)

    def _apply_items(self, items) -> None:
        table = self.query_one(ItemTable)
        loading = self.query_one(LoadingIndicator)
        table.load_items(items)
        loading.display = False
        table.display = True
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
        main
