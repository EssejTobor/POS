from __future__ import annotations

from typing import Iterable, List

from textual.reactive import reactive
from textual.widgets import DataTable

from ...models import ItemStatus, Priority, WorkItem


class ItemTable(DataTable):
    """Table for displaying work items with pagination and styling."""

    current_page: int = reactive(0)
    context_menu_row: int | None = None
    context_menu_open: bool = False
    last_action: str | None = None

    BINDINGS = [
        ("v", "view_selected", "View"),
        ("e", "edit_selected", "Edit"),
        ("d", "delete_selected", "Delete"),
    ]

    def __init__(self, page_size: int = 20, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.page_size = page_size
        self._items: List[WorkItem] = []

    def on_mount(self) -> None:  # pragma: no cover - simple setup
        self.add_columns(
            "ID",
            "Title",
            "Type",
            "Status",
            "Priority",
            "Due Date",
            "Actions",
        )

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_items(self, items: Iterable[WorkItem]) -> None:
        """Load the given items into the table."""
        self._items = list(items)
        self.current_page = 0
        self.refresh_page()

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------
    def next_page(self) -> None:
        if (self.current_page + 1) * self.page_size < len(self._items):
            self.current_page += 1
            self.refresh_page()

    def previous_page(self) -> None:
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_page()

    def refresh_page(self) -> None:
        self.clear(columns=False)
        start = self.current_page * self.page_size
        end = start + self.page_size
        for item in self._items[start:end]:
            self.add_row(*self._item_to_row(item), style=self._row_style(item))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _item_to_row(self, item: WorkItem) -> list[str]:
        due = getattr(item, "due_date", "") or ""
        return [
            item.id,
            item.title,
            item.item_type.name.title(),
            item.status.name.title(),
            item.priority.name.title(),
            str(due),
            "View | Edit | Delete",
        ]

    def _row_style(self, item: WorkItem) -> str:
        priority_color = {
            Priority.HI: "bold red",
            Priority.MED: "",
            Priority.LOW: "dim",
        }.get(item.priority, "")
        status_color = {
            ItemStatus.COMPLETED: "green",
            ItemStatus.IN_PROGRESS: "yellow",
            ItemStatus.NOT_STARTED: "",
        }.get(item.status, "")
        return " ".join(filter(None, [priority_color, status_color]))

    # ------------------------------------------------------------------
    # Action handlers and context menu helpers
    # ------------------------------------------------------------------
    def action_view_selected(self) -> None:  # pragma: no cover - simple action
        self.last_action = "view"

    def action_edit_selected(self) -> None:  # pragma: no cover - simple action
        self.last_action = "edit"

    def action_delete_selected(self) -> None:  # pragma: no cover - simple action
        self.last_action = "delete"

    def open_context_menu(self, row_index: int) -> None:
        """Open a simple context menu for the given row."""
        self.context_menu_row = row_index
        self.context_menu_open = True

    def close_context_menu(self) -> None:
        """Close the context menu if open."""
        self.context_menu_open = False
