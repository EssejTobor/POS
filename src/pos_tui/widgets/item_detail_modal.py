from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ...models import WorkItem
from ...storage import WorkSystem


class ItemDetailModal(ModalScreen[None]):
    """Modal dialog displaying details for a work item."""

    def __init__(self, item: WorkItem, system: WorkSystem) -> None:
        super().__init__()
        self.item = item
        self.system = system

    def compose(self) -> ComposeResult:
        links = self.system.get_links(self.item.id)
        tags = self.system.get_tags_for_item(self.item.id)
        with Container(id="item_detail_container"):
            yield Static(f"ID: {self.item.id}")
            yield Static(f"Title: {self.item.title}")
            yield Static(f"Goal: {self.item.goal}")
            yield Static(f"Type: {self.item.item_type.name}")
            yield Static(f"Priority: {self.item.priority.name}")
            yield Static(f"Status: {self.item.status.name}")
            yield Static(f"Created: {self.item.created_at.isoformat()}")
            yield Static(f"Updated: {self.item.updated_at.isoformat()}")
            if tags:
                yield Static("Tags: " + ", ".join(tags))
            if links["outgoing"] or links["incoming"]:
                yield Static("Links:")
                for link in links["outgoing"]:
                    yield Static(f"-> {link['target_id']} [{link['link_type']}]")
                for link in links["incoming"]:
                    yield Static(f"<- {link['source_id']} [{link['link_type']}]")
        yield Button("Close", id="close_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover
        self.dismiss()
