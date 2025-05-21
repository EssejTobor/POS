from textual.message import Message
from textual.widgets import DataTable

from ...models import WorkItem


class ItemTable(DataTable):
    """Table for displaying work items."""

    class SortRequested(Message):
        """Posted when the user requests sorting by a column."""

        def __init__(self, column: str) -> None:
            self.column = column
            super().__init__()

    def __init__(self, *args, **kwargs) -> None:  # noqa: D401
        super().__init__(*args, **kwargs)
        self.items: list[WorkItem] = []
        self.sort_column = ""
        self.sort_reverse = False

    def on_mount(self) -> None:
        self.add_columns("ID", "Title", "Type", "Status", "Priority")

    def load_items(self, items: list[WorkItem]) -> None:
        self.items = items
        self._refresh_table()

    def _refresh_table(self) -> None:
        self.clear()
        for item in self.items:
            self.add_row(
                item.id,
                item.title,
                item.item_type.value,
                item.status.value,
                str(item.priority.value),
            )

    def sort_by(self, column: str) -> None:
        reverse = False
        if self.sort_column == column:
            reverse = not self.sort_reverse
        self.sort_column = column
        self.sort_reverse = reverse

        key_map = {
            "ID": lambda i: i.id,
            "Title": lambda i: i.title.lower(),
            "Type": lambda i: i.item_type.value,
            "Status": lambda i: i.status.value,
            "Priority": lambda i: i.priority.value,
        }
        key_func = key_map.get(column, lambda i: i.id)
        self.items.sort(key=key_func, reverse=reverse)
        self._refresh_table()

    def on_datatable_header_selected(self, event: DataTable.HeaderSelected) -> None:
        self.post_message(self.SortRequested(event.column_label))
