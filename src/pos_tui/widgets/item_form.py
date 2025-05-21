from textual.app import ComposeResult
from textual.widgets import Button, Input, Static


class ItemEntryForm(Static):
    """Simple form for creating work items."""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Title", id="title_field")
        yield Input(placeholder="Description", id="description_field")
        yield Button(label="Submit", id="submit_button")
