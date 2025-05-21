from __future__ import annotations

from typing import Callable, Iterable, List

from textual.reactive import reactive
from textual.widgets import DataTable

from ...models import ItemStatus, ItemType, Priority, WorkItem


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
        self._filtered: List[WorkItem] = []
        self.item_type_filter: ItemType | None = None
        self.status_filter: ItemStatus | None = None
        self.search_text: str = ""
        self.sort_key: Callable[[WorkItem], object] | None = None
        self.sort_reverse: bool = False

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
        self._apply_filters()
        items = self._filtered
        if self.sort_key:
            items = sorted(
                items,
                key=self.sort_key,  # type: ignore[arg-type]
                reverse=self.sort_reverse,
            )

        self.clear(columns=False)
        start = self.current_page * self.page_size
        end = start + self.page_size
        for item in items[start:end]:
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

    # Filtering and sorting
    # ------------------------------------------------------------------
    def _apply_filters(self) -> None:
        items = self._items
        if self.item_type_filter is not None:
            items = [i for i in items if i.item_type == self.item_type_filter]
        if self.status_filter is not None:
            items = [i for i in items if i.status == self.status_filter]
        if self.search_text:
            term = self.search_text.lower()
            items = [
                i
                for i in items
                if term in i.title.lower() or term in i.description.lower()
            ]
        self._filtered = items

    def set_filters(
        self,
        *,
        item_type: ItemType | None = None,
        status: ItemStatus | None = None,
        search_text: str | None = None,
    ) -> None:
        self.item_type_filter = item_type
        self.status_filter = status
        self.search_text = search_text or ""
        self.current_page = 0
        self.refresh_page()

    def sort_by(self, key: Callable[[WorkItem], object], reverse: bool = False) -> None:
        self.sort_key = key
        self.sort_reverse = reverse
        self.refresh_page()

    def on_data_table_header_pressed(
        self, event: DataTable.HeaderPressed
    ) -> None:  # pragma: no cover - simple UI
        label = event.column_label
        key_map = {
            "ID": lambda i: i.id,
            "Title": lambda i: i.title.lower(),
            "Type": lambda i: i.item_type.value,
            "Status": lambda i: i.status.value,
            "Priority": lambda i: i.priority.value,
            "Due Date": lambda i: getattr(i, "due_date", "") or "",
        }
        if label in key_map:
            if self.sort_key == key_map[label]:
                self.sort_reverse = not self.sort_reverse
            else:
                self.sort_key = key_map[label]
                self.sort_reverse = False
            self.refresh_page()
