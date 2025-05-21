from __future__ import annotations

from datetime import datetime
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Input, Select, Static

from ...models import ItemStatus, ItemType, Priority


class ItemEntryForm(Static):
    """Form for creating new :class:`~src.models.WorkItem` instances."""

    def __init__(
        self, tag_options: Iterable[str] | None = None, *args, **kwargs
    ) -> None:
        """Initialize the form with optional tag suggestions."""
        super().__init__(*args, **kwargs)
        self.tag_options = sorted(set(tag_options or []))

    def compose(self) -> ComposeResult:
        """Create the layout for the entry form."""
        # ------------------------------------------------------------------
        # Basic information
        # ------------------------------------------------------------------
        yield Static("Basic Info", classes="section_title")
        with Container(id="basic_info"):
            yield Input(placeholder="Title", id="title_field")
            yield Input(placeholder="Description", id="description_field")

        # ------------------------------------------------------------------
        # Metadata fields
        # ------------------------------------------------------------------
        yield Static("Metadata", classes="section_title")
        with Container(id="metadata"):
            type_opts = [(t.name.title(), t.value) for t in ItemType]
            yield Select(type_opts, prompt="Type", id="type_selector")

            priority_opts = [(p.name.title(), str(p.value)) for p in Priority]
            yield Select(priority_opts, prompt="Priority", id="priority_selector")

            status_opts = [(s.name.title(), s.value) for s in ItemStatus]
            yield Select(status_opts, prompt="Status", id="status_selector")

        # ------------------------------------------------------------------
        # Additional section
        # ------------------------------------------------------------------
        yield Static("Additional", classes="section_title")
        with Container(id="additional"):
            yield Input(placeholder="Due Date YYYY-MM-DD", id="due_date_field")
            yield Input(placeholder="Tags", id="tags_field")
            yield Static("", id="tag_suggestions")

        # ------------------------------------------------------------------
        # Submit and feedback
        # ------------------------------------------------------------------
        yield Button(label="Submit", id="submit_button")
        yield Static("", id="validation_message")

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _clear_errors(self) -> None:
        for widget_id in [
            "title_field",
            "description_field",
            "due_date_field",
        ]:
            widget = self.query_one(f"#{widget_id}", Input, expect_none=True)
            if widget is not None:
                widget.remove_class("error")
        self.query_one("#validation_message", Static).update("")

    def _show_error(self, widget_id: str, message: str) -> None:
        self.query_one(f"#{widget_id}", Input).add_class("error")
        self.query_one("#validation_message", Static).update(message)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def on_input_changed(
        self, event: Input.Changed
    ) -> None:  # pragma: no cover - simple UI
        if event.input.id == "tags_field":
            text = event.value.lower()
            suggestions = [t for t in self.tag_options if t.startswith(text)]
            sug_widget = self.query_one("#tag_suggestions", Static)
            sug_widget.update(", ".join(suggestions[:5]))

    def on_button_pressed(
        self, event: Button.Pressed
    ) -> None:  # pragma: no cover - simple UI
        if event.button.id != "submit_button":
            return
        self._clear_errors()

        title = self.query_one("#title_field", Input).value.strip()
        if not title:
            self._show_error("title_field", "Title is required")
            return

        due_text = self.query_one("#due_date_field", Input).value.strip()
        if due_text:
            try:
                datetime.strptime(due_text, "%Y-%m-%d")
            except ValueError:
                self._show_error("due_date_field", "Invalid date format")
                return

        self.query_one("#validation_message", Static).update("Valid!")
