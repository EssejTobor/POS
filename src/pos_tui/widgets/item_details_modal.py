from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ...models import WorkItem
from ...storage import WorkSystem


class ItemDetailsModal(ModalScreen[None]):
    """Modal dialog for displaying details for a work item."""

    def __init__(self, item: WorkItem, work_system: WorkSystem) -> None:
        super().__init__()
        self.item = item
        self.work_system = work_system

    def _build_details_text(self) -> str:
        details = [
            f"ID: {self.item.id}",
            f"Title: {self.item.title}",
            f"Goal: {self.item.goal}",
            f"Type: {self.item.item_type.name}",
            f"Description: {self.item.description}",
            f"Priority: {self.item.priority.name}",
            f"Status: {self.item.status.name}",
            f"Created At: {self.item.created_at}",
            f"Updated At: {self.item.updated_at}",
        ]

        links = self.work_system.get_links(self.item.id)
        related: list[str] = ["Related Items:"]
        if links.get("outgoing"):
            related.append("Outgoing:")
            for link in links["outgoing"]:
                related.append(f" - {link['target_id']} ({link['link_type']})")
        if links.get("incoming"):
            related.append("Incoming:")
            for link in links["incoming"]:
                related.append(f" - {link['source_id']} ({link['link_type']})")
        if len(related) == 1:
            related.append(" None")

        return "\n".join(details + [""] + related)

    def compose(self) -> ComposeResult:
        text = self._build_details_text()
        yield VerticalScroll(Static(text, id="item_details"))
        yield Button("Close", id="close_button")

    def on_button_pressed(
        self, event: Button.Pressed
    ) -> None:  # pragma: no cover - UI event
        if event.button.id == "close_button":
            self.dismiss()
