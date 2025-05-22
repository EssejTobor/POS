from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Static

from ...storage import WorkSystem
from ...models import WorkItem
from .link_utils import format_link_type, link_type_icon, link_type_color


class LinkedItemsWidget(Static):
    """Display linked items grouped by relationship type."""

    def __init__(self, item_id: str, work_system: WorkSystem, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.item_id = item_id
        self.work_system = work_system
        self.links: dict[str, list[dict]] = {}

    def compose(self) -> ComposeResult:
        yield Vertical(id="linked_items_container")

    def on_mount(self) -> None:
        # ``UIComponentSimulator`` does not run ``compose`` automatically,
        # so guard against missing containers during validation.
        try:
            container = self.query_one("#linked_items_container", Vertical)
        except Exception:
            container = None
        if container is not None:
            self.refresh_links()

    # --------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------
    def refresh_links(self) -> None:
        try:
            container = self.query_one("#linked_items_container", Vertical)
        except Exception:
            return
        container.clear()
        links = self.work_system.get_links(self.item_id)
        grouped: dict[str, list[dict]] = defaultdict(list)
        for link in links.get("outgoing", []):
            grouped[f"outgoing:{link['link_type']}"].append(link)
        for link in links.get("incoming", []):
            grouped[f"incoming:{link['link_type']}"].append(link)
        self.links = grouped
        for group, items in grouped.items():
            direction, ltype = group.split(":")
            header = Static(
                f"{link_type_icon(ltype)} {direction.title()} {format_link_type(ltype)}",
                classes="link_group_header",
            )
            container.mount(header)
            for idx, link in enumerate(items):
                target_id = link["target_id"] if direction == "outgoing" else link["source_id"]
                title = link.get("title", "")
                item_text = f"{target_id} - {title}"
                item_row = Container(
                    Static(item_text, classes="linked_item", id=f"label_{direction}_{idx}"),
                    Button("Open", id=f"open_{target_id}"),
                    Button("Remove", id=f"remove_{direction}_{target_id}"),
                )
                container.mount(item_row)

    # --------------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI event
        if event.button.id is None:
            return
        if event.button.id.startswith("open_"):
            item_id = event.button.id.split("_", 1)[1]
            self.post_message(self.NavigateRequested(self, item_id))
        elif event.button.id.startswith("remove_outgoing_"):
            target = event.button.id.split("_", 2)[2]
            self.work_system.remove_link(self.item_id, target)
            self.refresh_links()
            self.post_message(self.LinkRemoved(self, self.item_id, target))
        elif event.button.id.startswith("remove_incoming_"):
            source = event.button.id.split("_", 2)[2]
            self.work_system.remove_link(source, self.item_id)
            self.refresh_links()
            self.post_message(self.LinkRemoved(self, source, self.item_id))

    # --------------------------------------------------------------
    # Messages
    # --------------------------------------------------------------
    class NavigateRequested(Button.Pressed):
        def __init__(self, sender: "LinkedItemsWidget", item_id: str) -> None:
            super().__init__(sender)
            self.item_id = item_id

    class LinkRemoved(Button.Pressed):
        def __init__(self, sender: "LinkedItemsWidget", source: str, target: str) -> None:
            super().__init__(sender)
            self.source = source
            self.target = target
