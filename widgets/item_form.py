"""Simple Item Entry Form widget using Textual."""

from __future__ import annotations

from typing import Dict, Optional

from textual import events
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Label, Select, TextArea


class ItemEntryForm(Container):
    """Form for entering basic item data."""

    class ItemSubmitted(Message):
        """Posted when the form is saved."""

        def __init__(self, data: Dict[str, str]) -> None:
            self.data = data
            super().__init__()

    def __init__(self, item: Optional[Dict[str, str]] = None) -> None:
        super().__init__()
        self.item = item or {}

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label("Goal:")
                yield Input(id="goal")
            with Horizontal():
                yield Label("Item Type:")
                yield Select(
                    options=[("Task", "t"), ("Thought", "th"), ("Goal", "g")],
                    id="item_type",
                )
            with Horizontal():
                yield Label("Priority:")
                yield Select(
                    options=[("LOW", "LOW"), ("MED", "MED"), ("HIGH", "HIGH")],
                    id="priority",
                )
            with Horizontal():
                yield Label("Title:")
                yield Input(id="title", placeholder="Required")
            with Horizontal():
                yield Label("Description:")
                yield TextArea(id="description")
            with Horizontal():
                yield Button("Save", id="save", variant="success")
                yield Button("Cancel", id="cancel", variant="error")

    def on_mount(self) -> None:
        if self.item:
            self.query_one("#goal", Input).value = self.item.get("goal", "")
            self.query_one("#item_type", Select).value = self.item.get("item_type", "t")
            self.query_one("#priority", Select).value = self.item.get("priority", "MED")
            self.query_one("#title", Input).value = self.item.get("title", "")
            self.query_one("#description", TextArea).value = self.item.get("description", "")
        self.query_one("#goal", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        if event.button.id == "save":
            self._submit()
        elif event.button.id == "cancel":
            for widget in self.query(Input, Select, TextArea):
                widget.value = ""

    def _submit(self) -> None:
        title = self.query_one("#title", Input).value
        if not title:
            return
        data = {
            "goal": self.query_one("#goal", Input).value,
            "item_type": self.query_one("#item_type", Select).value,
            "priority": self.query_one("#priority", Select).value,
            "title": title,
            "description": self.query_one("#description", TextArea).value,
        }
        if self.item.get("id"):
            data["id"] = self.item["id"]
        self.post_message(self.ItemSubmitted(data))

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter" and self.focused is not None:
            if self.focused.id in {"description", "save"}:
                self._submit()
