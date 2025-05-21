"""Interactive table widget for work items."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, ContextMenu, DataTable, MenuItem


class RowActions(Horizontal):
    """Action buttons used within a table row."""

    def __init__(self, item_id: str) -> None:
        super().__init__()
        self.item_id = item_id

    def compose(self) -> ComposeResult:
        yield Button("View", id=f"view_{self.item_id}")
        yield Button("Edit", id=f"edit_{self.item_id}")
        yield Button("Delete", id=f"delete_{self.item_id}")

    class ViewClicked(Message):
        """Posted when the view button is pressed."""

        def __init__(self, item_id: str) -> None:
            super().__init__()
            self.item_id = item_id

    class EditClicked(Message):
        """Posted when the edit button is pressed."""

        def __init__(self, item_id: str) -> None:
            super().__init__()
            self.item_id = item_id

    class DeleteClicked(Message):
        """Posted when the delete button is pressed."""

        def __init__(self, item_id: str) -> None:
            super().__init__()
            self.item_id = item_id

    def on_button_pressed(self, event: Button.Pressed) -> None:  # noqa: D401
        """Relay button presses as messages."""

        button_id = event.button.id or ""
        if button_id.startswith("view_"):
            self.post_message(self.ViewClicked(self.item_id))
        elif button_id.startswith("edit_"):
            self.post_message(self.EditClicked(self.item_id))
        elif button_id.startswith("delete_"):
            self.post_message(self.DeleteClicked(self.item_id))


class ItemTable(DataTable):
    """Table for displaying work items with row-level actions."""

    BINDINGS = [
        ("v", "view_item", "View"),
        ("e", "edit_item", "Edit"),
        ("d", "delete_item", "Delete"),
        ("m", "open_actions_menu", "Menu"),
    ]

    def on_mount(self) -> None:
        self.add_columns("ID", "Title", "Type", "Status", "Priority", "Actions")

    def add_item_row(self, item) -> None:
        """Add a work item row with action buttons."""

        actions = RowActions(item.id)
        self.add_row(
            item.id,
            item.title,
            getattr(item.item_type, "value", item.item_type),
            getattr(item.status, "value", item.status),
            getattr(item.priority, "name", item.priority),
            actions,
        )

    def _get_selected_id(self) -> str | None:
        if self.cursor_row is None:
            return None
        return str(self.get_row(self.cursor_row)[0])

    def action_view_item(self) -> None:
        if item_id := self._get_selected_id():
            self.post_message(RowActions.ViewClicked(item_id))

    def action_edit_item(self) -> None:
        if item_id := self._get_selected_id():
            self.post_message(RowActions.EditClicked(item_id))

    def action_delete_item(self) -> None:
        if item_id := self._get_selected_id():
            self.post_message(RowActions.DeleteClicked(item_id))

    def action_open_actions_menu(self) -> None:
        if not (item_id := self._get_selected_id()):
            return
        menu = ContextMenu(
            MenuItem("View", id="view"),
            MenuItem("Edit", id="edit"),
            MenuItem("Delete", id="delete"),
        )
        self.app.open_menu(menu)

    def on_context_menu_item_selected(self, event: ContextMenu.ItemSelected) -> None:
        if not (item_id := self._get_selected_id()):
            return
        if event.item.id == "view":
            self.post_message(RowActions.ViewClicked(item_id))
        elif event.item.id == "edit":
            self.post_message(RowActions.EditClicked(item_id))
        elif event.item.id == "delete":
            self.post_message(RowActions.DeleteClicked(item_id))
