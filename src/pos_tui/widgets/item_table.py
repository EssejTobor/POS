from __future__ import annotations

from typing import Callable, Iterable, List

from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, OptionList
from textual.widgets.option_list import Option

from ...models import ItemStatus, ItemType, Priority, WorkItem


class ItemTable(DataTable):
    """Table for displaying work items with pagination and styling."""

    current_page: int = reactive(0)
    context_menu_row: int | None = None
    context_menu_open: bool = False
    context_menu: OptionList | None = None
    last_action: str | None = None

    BINDINGS = [
        ("v", "view_selected", "View"),
        ("e", "edit_selected", "Edit"),
        ("d", "delete_selected", "Delete"),
    ]

    class ItemSelected(Message):
        def __init__(self, sender: "ItemTable", item: WorkItem) -> None:
            super().__init__(sender)
            self.item = item

    class ItemEditRequested(Message):
        def __init__(self, sender: "ItemTable", item: WorkItem) -> None:
            super().__init__(sender)
            self.item = item

    class ItemDeleteRequested(Message):
        def __init__(self, sender: "ItemTable", item: WorkItem) -> None:
            super().__init__(sender)
            self.item = item

    def __init__(self, page_size: int = 20, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.page_size = page_size
        self._items: List[WorkItem] = []
        self._filtered: List[WorkItem] = []
        self._row_items: List[WorkItem] = []
        self.item_type_filter: ItemType | None = None
        self.status_filter: ItemStatus | None = None
        self.search_text: str = ""
        self.sort_key: Callable[[WorkItem], object] | None = None
        self.sort_reverse: bool = False
        self._last_click_time: float = 0.0
        self._last_click_coord: tuple[int, int] | None = None

    def _selected_item(self) -> WorkItem | None:
        if self.cursor_row is None:
            return None
        if 0 <= self.cursor_row < len(self._row_items):
            return self._row_items[self.cursor_row]
        return None

    def _add_column_fallback(self, label: str, index: int) -> None:
        """Add a column without relying on an active Textual app."""
        from rich.text import Text
        from textual.widgets._data_table import Column, ColumnKey

        key = ColumnKey(str(index))
        column = Column(
            key,
            Text(label),
            width=len(label),
            content_width=len(label),
        )
        self.columns[key] = column
        self._column_locations[key] = index

    def on_mount(self) -> None:  # pragma: no cover - simple setup
        labels = [
            "ID",
            "Title",
            "Type",
            "Status",
            "Priority",
            "Due Date",
            "Actions",
        ]
        try:
            self.add_columns(*labels)
        except Exception:
            for i, label in enumerate(labels):
                self._add_column_fallback(label, i)

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
        self._row_items = []
        start = self.current_page * self.page_size
        end = start + self.page_size
        page_items = items[start:end]
        if not page_items:
            placeholder = [
                "No items found",
                *["" for _ in range(len(self.columns) - 1)],
            ]
            self.add_row(*placeholder, style="dim")
            return
        for item in page_items:
            self.add_row(*self._item_to_row(item), style=self._row_style(item))
            self._row_items.append(item)

    def update_item(self, item: WorkItem) -> None:
        """Update the table row for the given item."""
        for i, existing in enumerate(self._items):
            if existing.id == item.id:
                self._items[i] = item
                break
        for row_index, row_item in enumerate(self._row_items):
            if row_item.id == item.id:
                self._row_items[row_index] = item
                cells = self._item_to_row(item)
                for col, value in enumerate(cells):
                    super().update_cell(row_index, col, value)
                break

    def remove_item(self, item_id: str) -> int | None:
        """Remove the item from the table and return its row index."""
        index = None
        for i, existing in enumerate(self._items):
            if existing.id == item_id:
                index = i
                del self._items[i]
                break
        if index is None:
            return None
        for row_index, row_item in enumerate(self._row_items):
            if row_item.id == item_id:
                del self._row_items[row_index]
                self.remove_row(row_index)
                break
        return index

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
        item = self._selected_item()
        if item is None:
            return
        self.last_action = "view"
        self.post_message(self.ItemSelected(self, item))

    def action_edit_selected(self) -> None:  # pragma: no cover - simple action
        item = self._selected_item()
        if item is None:
            return
        self.last_action = "edit"
        self.post_message(self.ItemEditRequested(self, item))

    def action_delete_selected(self) -> None:  # pragma: no cover - simple action
        item = self._selected_item()
        if item is None:
            return
        self.last_action = "delete"
        self.post_message(self.ItemDeleteRequested(self, item))

    def open_context_menu(self, row_index: int) -> None:
        """Open a simple context menu for the given row."""
        self.context_menu_row = row_index
        if self.context_menu_open:
            self.close_context_menu()
        menu = OptionList(
            Option("View", id="view"),
            Option("Edit", id="edit"),
            Option("Delete", id="delete"),
            id="item_context_menu",
        )
        self.context_menu = menu
        self.mount(menu)
        self.focus()  # Ensure keyboard focus
        self.context_menu_open = True

    def close_context_menu(self) -> None:
        """Close the context menu if open."""
        if self.context_menu is not None:
            self.context_menu.remove()
            self.context_menu = None
        self.context_menu_open = False

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:  # pragma: no cover - simple UI
        if not self.context_menu_open or self.context_menu is None:
            return
        option_id = event.option.id
        if option_id == "view":
            self.action_view_selected()
        elif option_id == "edit":
            self.action_edit_selected()
        elif option_id == "delete":
            self.action_delete_selected()
        self.close_context_menu()

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

    def on_data_table_cell_selected(
        self, event: DataTable.CellSelected
    ) -> None:
        """Detect double-clicks on a row to open details."""
        if event.coordinate == self._last_click_coord and event.time - self._last_click_time < 0.5:
            item = self._selected_item()
            if item is not None:
                self.post_message(self.ItemSelected(self, item))
        self._last_click_coord = event.coordinate
        self._last_click_time = event.time
