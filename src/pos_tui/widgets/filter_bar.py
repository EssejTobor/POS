from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Input, Select

from ...models import ItemStatus, ItemType
from ..preferences import load_preferences, save_preferences


class FilterBar(Container):
    """Widget providing controls for filtering item tables."""

    class FilterChanged(Message):
        """Message emitted when any filter option changes."""

        def __init__(self, sender: "FilterBar") -> None:
            super().__init__(sender)
            self.item_type: ItemType | None = sender.item_type
            self.status: ItemStatus | None = sender.status
            self.search_text: str = sender.search_text

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.item_type: ItemType | None = None
        self.status: ItemStatus | None = None
        self.search_text: str = ""

    def on_mount(self) -> None:
        prefs = load_preferences().get("filters", {})
        if prefs:
            self.item_type = ItemType(prefs.get("item_type")) if prefs.get("item_type") else None
            self.status = ItemStatus(prefs.get("status")) if prefs.get("status") else None
            self.search_text = prefs.get("search_text", "")
            select = self.query_one("#filter_type", Select)
            select.value = self.item_type.value if self.item_type else ""
            search = self.query_one("#filter_search", Input)
            search.value = self.search_text

    def compose(self) -> ComposeResult:
        type_options = [("All", "")] + [(t.name.title(), t.value) for t in ItemType]
        yield Select(type_options, prompt="Type", id="filter_type")
        yield Input(placeholder="Search", id="filter_search")
        yield Button("All", id="status_all")
        yield Button("Not Started", id="status_not_started")
        yield Button("In Progress", id="status_in_progress")
        yield Button("Completed", id="status_completed")

    def on_select_changed(
        self, event: Select.Changed
    ) -> None:  # pragma: no cover - simple UI
        if event.select.id == "filter_type":
            value = event.value or None
            self.item_type = ItemType(value) if value else None
            self._save_preferences()
            self.post_message(self.FilterChanged(self))

    def on_input_changed(
        self, event: Input.Changed
    ) -> None:  # pragma: no cover - simple UI
        if event.input.id == "filter_search":
            self.search_text = event.value
            self._save_preferences()
            self.post_message(self.FilterChanged(self))

    def on_button_pressed(
        self, event: Button.Pressed
    ) -> None:  # pragma: no cover - simple UI
        mapping = {
            "status_not_started": ItemStatus.NOT_STARTED,
            "status_in_progress": ItemStatus.IN_PROGRESS,
            "status_completed": ItemStatus.COMPLETED,
            "status_all": None,
        }
        if event.button.id in mapping:
            self.status = mapping[event.button.id]
            self._save_preferences()
            self.post_message(self.FilterChanged(self))

    def _save_preferences(self) -> None:
        prefs = load_preferences()
        prefs["filters"] = {
            "item_type": self.item_type.value if self.item_type else None,
            "status": self.status.value if self.status else None,
            "search_text": self.search_text,
        }
        save_preferences(prefs)
