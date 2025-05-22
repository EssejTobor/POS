from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, DataTable, LoadingIndicator, Static
from ..widgets import (
    DashboardStatus,
    FilterBar,
    ItemFormModal,
    ItemTable,
    ConfirmModal,
    ToastNotification,
)
from ...models import ItemStatus, WorkItem, ItemType, Priority
from ..widgets.item_form import ItemEntryForm
from ..workers import ItemFetchWorker
from ..workers.db import ItemFetchWorker as DBItemFetchWorker, ItemSaveWorker
from .detail import ItemDetailScreen



class DashboardScreen(Container):
    """Screen displaying an overview of work items."""

    last_deleted: tuple[WorkItem, int] | None = None
    last_edit: tuple[WorkItem, WorkItem] | None = None

    BINDINGS = [
        ("r", "refresh", "Refresh Items"),
        ("n", "create", "New Item"),
        ("u", "undo_last", "Undo"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="dashboard_header"):
            yield Static("Dashboard", id="dashboard_title")
            yield Button("Refresh", id="refresh_button")
            yield Button("Create", id="create_button")

        yield FilterBar(id="filter_bar")
        yield LoadingIndicator(id="loading")
        yield ItemTable(id="dashboard_table")
        yield DashboardStatus(id="dashboard_status")
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
        filters = self.query_one(FilterBar)
        table.display = False
        loading.display = True
        worker = ItemFetchWorker(
            self.app,
            self.app.work_system,
            item_type=filters.item_type,
            status=filters.status,
            search_text=filters.search_text,
            sort_key=table.sort_key,
            sort_reverse=table.sort_reverse,
            page=table.current_page,
            page_size=table.page_size,
            callback=self._apply_items,
        )
        self.run_worker(worker, thread=True)
        query = (
            "SELECT * FROM work_items WHERE status != ? "
            "ORDER BY priority DESC, created_at DESC"
        )
        worker = DBItemFetchWorker(
            "fetch_items",
            self.app,
            self.app.connection_manager,
            query,
            [ItemStatus.COMPLETED.value],
            on_success=lambda result: self.call_from_thread(self._apply_items, result),
        )
        self.app.schedule_worker(worker)

    def _apply_items(self, items) -> None:
        table = self.query_one(ItemTable)
        loading = self.query_one(LoadingIndicator)
        work_items = [
            WorkItem.from_dict(row) if isinstance(row, dict) else row for row in items
        ]
        table.load_items(work_items)
        loading.display = False
        table.display = True
        self._update_status_bar(items)

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
        self.app.push_screen(ItemDetailScreen(event.item, self.app.work_system))

    def on_item_table_edit_requested(
        self, event: ItemTable.EditRequested
    ) -> None:  # pragma: no cover - UI action
        self.app.push_screen(ItemFormModal(event.item, self.app.work_system))

    def on_item_entry_form_save_started(
        self, event: ItemEntryForm.SaveStarted
    ) -> None:
        form = event.sender
        if form.item is None:
            return
        import copy
        from textual.widgets import Input, Select
        original = copy.deepcopy(form.item)
        updated = copy.deepcopy(form.item)
        updated.title = form.query_one("#title_field", Input).value.strip()
        updated.description = form.query_one("#description_field", Input).value
        updated.item_type = ItemType(
            form.query_one("#type_selector", Select).value or ItemType.TASK.value
        )
        updated.priority = Priority(
            int(form.query_one("#priority_selector", Select).value or 2)
        )
        updated.status = ItemStatus(
            form.query_one("#status_selector", Select).value
            or ItemStatus.NOT_STARTED.value
        )
        self.app.work_system.items[updated.id] = updated
        table = self.query_one(ItemTable)
        table.update_item(updated)
        self.last_edit = (original, updated)
        self.query_one("#status_bar", Static).update(
            "Item updated. Press 'u' to undo."
        )

    def on_item_entry_form_save_result(
        self, event: ItemEntryForm.SaveResult
    ) -> None:
        if not self.last_edit:
            return
        original, updated = self.last_edit
        if not event.success:
            self.app.work_system.items[original.id] = original
            table = self.query_one(ItemTable)
            table.update_item(original)
            self.query_one("#status_bar", Static).update(
                f"Edit failed: {event.message}"
            )
            self.last_edit = None
        else:
            self.query_one("#status_bar", Static).update(
                "Edit saved. Press 'u' to undo."
            )

    def on_item_table_delete_requested(
        self, event: ItemTable.DeleteRequested
    ) -> None:  # pragma: no cover - UI action
        modal = ConfirmModal(
            f"Delete '{event.item.title}'?",
            variant="danger",
        )

        def _on_result(result: bool) -> None:
            if result:
                self._perform_delete(event.item)

        self.app.push_screen(modal, callback=_on_result)

    def _perform_delete(self, item: WorkItem) -> None:
        table = self.query_one(ItemTable)
        index = table.remove_item(item.id)

        if index is None:
            index = -1

        self.last_deleted = (item, index)

        if item.id in self.app.work_system.items:
            del self.app.work_system.items[item.id]



        def op(conn):
            self.app.work_system.db.delete_item(item.id)
            return 1

        from ..error import log_error

        worker = ItemSaveWorker(
            "delete_item",
            self.app,
            self.app.connection_manager,
            op,
            on_error=lambda e: (
                log_error(e),
                self.call_from_thread(self._restore_deleted, item, index),
            ),
        )
        self.app.schedule_worker(worker)

    def _restore_deleted(self, item: WorkItem, index: int) -> None:
        """Reinsert a deleted item if the delete worker fails."""
        self.app.work_system.items[item.id] = item
        table = self.query_one(ItemTable)
        table.load_items(self.app.work_system.items.values())
        self.last_deleted = None
        self.query_one("#status_bar", Static).update("Delete failed; item restored")

    def action_undo_last(self) -> None:  # pragma: no cover - simple UI
        if self.last_edit:
            original, updated = self.last_edit
            try:
                self.app.work_system.update_item(
                    updated.id,
                    title=original.title,
                    description=original.description,
                    item_type=original.item_type,
                    priority=original.priority,
                    status=original.status,
                )
                table = self.query_one(ItemTable)
                table.update_item(self.app.work_system.items[updated.id])
                self.query_one("#status_bar", Static).update("Undo successful")
            except Exception as e:
                self.query_one("#status_bar", Static).update(f"Undo failed: {e}")
            finally:
                self.last_edit = None
            return

        if self.last_deleted:
            item, index = self.last_deleted
            try:
                self.app.work_system.db.add_item(item)
                self.app.work_system.items[item.id] = item
            except Exception as e:  # pragma: no cover - basic error
                self.query_one("#status_bar", Static).update(f"Undo failed: {e}")
                self.last_deleted = None
                return

            table = self.query_one(ItemTable)
            table.load_items(self.app.work_system.items.values())
            self.query_one("#status_bar", Static).update("Undo successful")
            self.last_deleted = None

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
