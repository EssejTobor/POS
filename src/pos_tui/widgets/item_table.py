from textual.widgets import DataTable


class ItemTable(DataTable):
    """Table for displaying work items."""

    def on_mount(self) -> None:
        self.add_columns("ID", "Title", "Type", "Status", "Priority")
