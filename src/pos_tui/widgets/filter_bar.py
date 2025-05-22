from __future__ import annotations

from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Input, Select, Checkbox

from ...models import ItemStatus, ItemType
from ..preferences import load_preferences, save_preferences


class FilterBar(Container):
    """Widget providing controls for filtering item tables."""

    class FilterChanged(Message):
        """Message emitted when any filter option changes."""

        def __init__(self, sender: "FilterBar") -> None:
            super().__init__(sender)
            self.item_types: set[ItemType] = sender.item_types
            self.statuses: set[ItemStatus] = sender.statuses
            self.search_text: str = sender.search_text
            self.start_date: str | None = sender.start_date
            self.end_date: str | None = sender.end_date

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.item_types: set[ItemType] = set()
        self.statuses: set[ItemStatus] = set()
        self.search_text: str = ""
        self.start_date: str | None = None
        self.end_date: str | None = None
        self.presets: dict[str, dict] = {}
        self.current_preset: str | None = None

    def on_mount(self) -> None:
        prefs = load_preferences()
        preset_data = prefs.get("filter_presets", {})
        self.presets.update(preset_data)
        filters = prefs.get("filters", {})
        self.current_preset = filters.get("preset")
        if self.current_preset and self.current_preset in self.presets:
            values = self.presets[self.current_preset]
        else:
            values = filters
        if values:
            types = values.get("item_types") or []
            self.item_types = {ItemType(t) for t in types}
            statuses = values.get("statuses") or []
            self.statuses = {ItemStatus(s) for s in statuses}
            self.search_text = values.get("search_text", "")
            self.start_date = values.get("start_date")
            self.end_date = values.get("end_date")
        # update widgets after compose

    def compose(self) -> ComposeResult:
        preset_options = [("None", "")] + [(name, name) for name in sorted(self.presets)]
        yield Select(preset_options, prompt="Preset", id="preset_select")
        yield Input(placeholder="Save preset as", id="preset_name")
        yield Button("Save", id="preset_save")
        yield Button("Delete", id="preset_delete")
        for t in ItemType:
            yield Checkbox(t.name.title(), id=f"type_{t.value}")
        for s in ItemStatus:
            yield Checkbox(s.name.replace("_", " ").title(), id=f"status_{s.value}")
        yield Input(placeholder="Start YYYY-MM-DD", id="start_date")
        yield Input(placeholder="End YYYY-MM-DD", id="end_date")
        yield Input(placeholder="Search", id="filter_search")

    def on_mount_post_layout(self) -> None:
        # update widget states after layout is ready
        for t in self.item_types:
            cb = self.query_one(f"#type_{t.value}", Checkbox)
            cb.value = True
        for s in self.statuses:
            cb = self.query_one(f"#status_{s.value}", Checkbox)
            cb.value = True
        if self.search_text:
            self.query_one("#filter_search", Input).value = self.search_text
        if self.start_date:
            self.query_one("#start_date", Input).value = self.start_date
        if self.end_date:
            self.query_one("#end_date", Input).value = self.end_date
        if self.current_preset:
            self.query_one("#preset_select", Select).value = self.current_preset

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:  # pragma: no cover - UI
        if event.checkbox.id.startswith("type_"):
            value = event.checkbox.id.split("_", 1)[1]
            t = ItemType(value)
            if event.value:
                self.item_types.add(t)
            else:
                self.item_types.discard(t)
        elif event.checkbox.id.startswith("status_"):
            value = event.checkbox.id.split("_", 1)[1]
            s = ItemStatus(value)
            if event.value:
                self.statuses.add(s)
            else:
                self.statuses.discard(s)
        self._save_preferences()
        self.post_message(self.FilterChanged(self))

    def on_input_changed(self, event: Input.Changed) -> None:  # pragma: no cover - UI
        if event.input.id == "filter_search":
            self.search_text = event.value
        elif event.input.id == "start_date":
            self.start_date = event.value or None
        elif event.input.id == "end_date":
            self.end_date = event.value or None
        elif event.input.id == "preset_name":
            return
        self._save_preferences()
        self.post_message(self.FilterChanged(self))

    def on_select_changed(self, event: Select.Changed) -> None:  # pragma: no cover - UI
        if event.select.id == "preset_select":
            name = event.value or None
            self.current_preset = name
            if name and name in self.presets:
                values = self.presets[name]
                self.item_types = {ItemType(t) for t in values.get("item_types", [])}
                self.statuses = {ItemStatus(s) for s in values.get("statuses", [])}
                self.search_text = values.get("search_text", "")
                self.start_date = values.get("start_date")
                self.end_date = values.get("end_date")
                self.on_mount_post_layout()
            self._save_preferences()
            self.post_message(self.FilterChanged(self))

    def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI
        if event.button.id == "preset_save":
            name = self.query_one("#preset_name", Input).value.strip()
            if not name:
                return
            self.presets[name] = {
                "item_types": [t.value for t in self.item_types],
                "statuses": [s.value for s in self.statuses],
                "search_text": self.search_text,
                "start_date": self.start_date,
                "end_date": self.end_date,
            }
            self.current_preset = name
            self._save_preferences()
            select = self.query_one("#preset_select", Select)
            select.add_option(name, name)
            select.value = name
            self.post_message(self.FilterChanged(self))
        elif event.button.id == "preset_delete":
            if self.current_preset and self.current_preset in self.presets:
                del self.presets[self.current_preset]
                select = self.query_one("#preset_select", Select)
                select.remove_option(self.current_preset)
                self.current_preset = None
                self._save_preferences()
                self.post_message(self.FilterChanged(self))

    def _save_preferences(self) -> None:
        prefs = load_preferences()
        prefs["filters"] = {
            "item_types": [t.value for t in self.item_types],
            "statuses": [s.value for s in self.statuses],
            "search_text": self.search_text,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "preset": self.current_preset,
        }
        prefs["filter_presets"] = self.presets
        save_preferences(prefs)
