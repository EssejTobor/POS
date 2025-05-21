from textual.app import ComposeResult
from textual.containers import Container

from ..widgets import ItemEntryForm


class NewItemScreen(Container):
    """Screen for entering new work items."""

    def compose(self) -> ComposeResult:
        yield ItemEntryForm(id="item_entry_form")
