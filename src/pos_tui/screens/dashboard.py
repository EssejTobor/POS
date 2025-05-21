from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, DataTable, LoadingIndicator, Static

from ..widgets import FilterBar, ItemDetailsModal, ItemFormModal, ItemTable


class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    BINDINGS = [
        ("r", "refresh", "Refresh Items"),
        ("n", "create", "New Item"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="dashboard_header"):
            yield Static("Dashboard", id="dashboard_title")
            yield Button("Refresh", id="refresh_button")
            yield Button("Create", id="create_button")

        yield FilterBar(id="filter_bar")
        yield LoadingIndicator(id="loading")
        yield ItemTable(id="dashboard_table")
        with Container(id="dashboard_footer"):
            yield Static("", id="status_bar")

    def on_mount(self) -> None:
        self.query_one(LoadingIndicator).display = False
        self.refresh()

    def action_refresh(self) -> None:
        self.refresh()

    def action_create(self) -> None:  # pragma: no cover - simple UI
        self.app.action_switch_tab("new-item")

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
        self._update_status_bar(items)

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

    def _update_status_bar(self, items) -> None:
        from ...models import ItemStatus

        counts = {
            status: len([i for i in items if i.status == status])
            for status in ItemStatus
        }
        total = len(items)
        text = (
            f"Total: {total} | Not Started: {counts[ItemStatus.NOT_STARTED]} | "
            f"In Progress: {counts[ItemStatus.IN_PROGRESS]} | "
            f"Completed: {counts[ItemStatus.COMPLETED]}"
        )
        self.query_one("#status_bar", Static).update(text)
