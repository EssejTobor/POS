from __future__ import annotations

from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Input, Select, Static


class LinkEditor(Static):
    """Widget for selecting and managing item links."""

    def __init__(
        self, link_options: Iterable[tuple[str, str]] | None = None, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.link_options = list(link_options or [])
        self.filtered_options = self.link_options.copy()
        self.links: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        with Container(id="link_controls"):
            yield Input(placeholder="Search", id="link_search")
            yield Select(self.filtered_options, prompt="Target", id="link_target_selector")
            yield Select(
                [
                    ("References", "references"),
                    ("Evolves From", "evolves-from"),
                ],
                prompt="Type",
                id="link_type_selector",
            )
            yield Button("Add Link", id="add_link_button")
        yield Container(id="linked_items")

    # --------------------------------------------------------------
    # Link management helpers
    # --------------------------------------------------------------
    def _refresh_links(self) -> None:
        container = self.query_one("#linked_items", Container)
        container.clear()
        icons = {"references": "🔗", "evolves-from": "↩"}
        for idx, (target, link_type) in enumerate(self.links):
            icon = icons.get(link_type, "→")
            container.mount(
                Container(
                    Static(f"{icon} {target} ({link_type})"),
                    Button("Remove", id=f"remove_link_{idx}"),
                )
            )

    # --------------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------------
    def on_button_pressed(
        self, event: Button.Pressed
    ) -> None:  # pragma: no cover - UI event
        if event.button.id == "add_link_button":
            target = self.query_one("#link_target_selector", Select).value
            link_type = (
                self.query_one("#link_type_selector", Select).value or "references"
            )
            if target:
                self.links.append((target, link_type))
                self._refresh_links()
        elif event.button.id and event.button.id.startswith("remove_link_"):
            idx = int(event.button.id.split("_")[-1])
            if 0 <= idx < len(self.links):
                self.links.pop(idx)
                self._refresh_links()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "link_search":
            text = event.value.lower()
            self.filtered_options = [
                opt for opt in self.link_options if text in opt[0].lower()
            ]
            self.query_one("#link_target_selector", Select).options = self.filtered_options
