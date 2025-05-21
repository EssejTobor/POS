from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Input, Select, Static

from ...models import ItemStatus, ItemType, Priority


class ItemEntryForm(Static):
    """Form for creating new :class:`~src.models.WorkItem` instances."""

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
            yield Input(placeholder="Due Date", id="due_date_field")
            yield Input(placeholder="Tags", id="tags_field")

        # ------------------------------------------------------------------
        # Submit and feedback
        # ------------------------------------------------------------------
        yield Button(label="Submit", id="submit_button")
        yield Static("", id="validation_message")
