from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Button, Input, Select, Static

from ...models import ItemStatus, ItemType


class FilterBar(Static):
    """Widget providing filtering controls for the dashboard."""

    class FiltersChanged(Message):
        """Posted when the user changes any filter."""

        def __init__(self, filter_bar: "FilterBar") -> None:
            self.filter_bar = filter_bar
            super().__init__()

    def compose(self) -> ComposeResult:
        type_options = [(it.name.title(), it.value) for it in ItemType]
        type_options.insert(0, ("All", ""))
        yield Select(options=type_options, id="type_filter")
        yield Input(placeholder="Search", id="search_filter")
        yield Button(label="Not Started", id="status_not_started")
        yield Button(label="In Progress", id="status_in_progress")
        yield Button(label="Completed", id="status_completed")

    def get_filters(self) -> dict[str, str | None]:
        select = self.query_one("#type_filter", Select)
        search = self.query_one("#search_filter", Input)
        status = None
        if self.query_one("#status_not_started", Button).pressed:
            status = ItemStatus.NOT_STARTED.value
        elif self.query_one("#status_in_progress", Button).pressed:
            status = ItemStatus.IN_PROGRESS.value
        elif self.query_one("#status_completed", Button).pressed:
            status = ItemStatus.COMPLETED.value
        return {
            "item_type": select.value or None,
            "search_text": search.value or None,
            "status": status,
        }

    def on_select_changed(self, event: Select.Changed) -> None:  # noqa: D401
        self.post_message(self.FiltersChanged(self))

    def on_input_changed(self, event: Input.Changed) -> None:  # noqa: D401
        self.post_message(self.FiltersChanged(self))

    def on_button_pressed(self, event: Button.Pressed) -> None:  # noqa: D401
        button = event.button
        for other in self.query(Button):
            other.pressed = False
        button.pressed = True
        self.post_message(self.FiltersChanged(self))
