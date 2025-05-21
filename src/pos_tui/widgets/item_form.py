from __future__ import annotations

from datetime import datetime
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Input, LoadingIndicator, Select, Static

from ...models import ItemStatus, ItemType, Priority
from ...storage import WorkSystem
from .link_editor import LinkEditor


class ItemEntryForm(Static):
    """Form for creating new :class:`~src.models.WorkItem` instances."""

    BINDINGS = [
        ("ctrl+s", "submit", "Save"),
        ("ctrl+c", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        tag_options: Iterable[str] | None = None,
        link_options: Iterable[tuple[str, str]] | None = None,
        work_system: WorkSystem | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the form with optional tag and link suggestions."""
        super().__init__(*args, **kwargs)
        self.tag_options = sorted(set(tag_options or []))
        self.link_options = list(link_options or [])
        self.work_system = work_system
        self.link_editor: LinkEditor | None = None

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

        # --------------------------------------------------------------
        # Links section
        # --------------------------------------------------------------
        yield Static("Links", classes="section_title")
        self.link_editor = LinkEditor(self.link_options, id="link_editor")
        yield self.link_editor

        # ------------------------------------------------------------------
        # Submit and feedback
        # ------------------------------------------------------------------
        yield Button(label="Save", id="save_button")
        yield Button(label="Cancel", id="cancel_button")
        yield LoadingIndicator(id="save_loading")
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

    def reset_form(self) -> None:
        """Clear all input fields and link selections."""
        for field in [
            "title_field",
            "description_field",
            "due_date_field",
            "tags_field",
        ]:
            widget = self.query_one(f"#{field}", Input, expect_none=True)
            if widget is not None:
                widget.value = ""
        if self.link_editor is not None:
            self.link_editor.links = []
            self.link_editor._refresh_links()

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
        if event.button.id == "save_button":
            self.action_submit()
        elif event.button.id == "cancel_button":
            self.action_cancel()

    # --------------------------------------------------------------
    # Actions triggered by keyboard or buttons
    # --------------------------------------------------------------
    def action_submit(self) -> None:  # pragma: no cover - simple UI
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

        self.query_one("#save_loading", LoadingIndicator).display = True
        self.run_worker(self._save_item, thread=True)

    def action_cancel(self) -> None:  # pragma: no cover - simple UI
        self.reset_form()
        self.query_one("#validation_message", Static).update("Canceled")

    def _save_item(self) -> None:
        """Worker method to perform database save."""
        success = True
        message = ""
        try:
            if self.work_system is not None:
                item = self.work_system.add_item(
                    goal="default",
                    title=self.query_one("#title_field", Input).value.strip(),
                    item_type=ItemType(
                        self.query_one("#type_selector", Select).value
                        or ItemType.TASK.value
                    ),
                    description=self.query_one("#description_field", Input).value,
                    priority=Priority(
                        int(self.query_one("#priority_selector", Select).value or 2)
                    ),
                )
                for target, link_type in (
                    self.link_editor.links if self.link_editor else []
                ):
                    self.work_system.add_link(item.id, target.split()[0], link_type)
        except Exception as e:  # pragma: no cover - basic error handling
            success = False
            message = str(e)

        self.call_from_thread(self._finish_save, success, message)

    def _finish_save(self, success: bool, message: str) -> None:
        loader = self.query_one("#save_loading", LoadingIndicator)
        loader.display = False
        if success:
            self.query_one("#validation_message", Static).update("Saved!")
            self.reset_form()
        else:
            self.query_one("#validation_message", Static).update(f"Error: {message}")
