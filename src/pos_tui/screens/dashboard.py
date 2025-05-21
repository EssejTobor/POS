from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, LoadingIndicator

from ..widgets import (DashboardStatus, FilterBar, ItemDetailsModal,
                       ItemFormModal, ItemTable)


class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    BINDINGS = [
        ("r", "refresh", "Refresh Items"),
    ]

    def compose(self) -> ComposeResult:
        yield FilterBar(id="filter_bar")
        yield LoadingIndicator(id="loading")
        yield ItemTable(id="dashboard_table")
        yield DashboardStatus(id="dashboard_status")

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

        status = self.query_one(DashboardStatus)
        total = len(self.app.work_system.items)
        status.set_counts(incomplete=len(items), total=total)

    def on_filter_bar_filter_changed(
        self, event: FilterBar.FilterChanged
    ) -> None:  # pragma: no cover - simple UI
        table = self.query_one(ItemTable)
        table.set_filters(
            item_type=event.item_type,
            status=event.status,
            search_text=event.search_text,
        )

    def on_data_table_cell_selected(
        self, event: DataTable.CellSelected
    ) -> None:  # pragma: no cover - simple UI
        table = self.query_one(ItemTable)
        if event.sender is table and event.column_label == "Actions":
            table.open_context_menu(event.coordinate.row)

    def on_item_table_view_requested(
        self, event: ItemTable.ViewRequested
    ) -> None:  # pragma: no cover - UI action
        self.app.push_screen(ItemDetailsModal(event.item, self.app.work_system))

    def on_item_table_edit_requested(
        self, event: ItemTable.EditRequested
    ) -> None:  # pragma: no cover - UI action
        self.app.push_screen(ItemFormModal(event.item, self.app.work_system))

    def on_item_table_delete_requested(
        self, event: ItemTable.DeleteRequested
    ) -> None:  # pragma: no cover - UI action
        self.app.work_system.delete_item(event.item.id)
        self.refresh()
