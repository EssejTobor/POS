from __future__ import annotations

from textual.app import ComposeResult
from textual._context import NoActiveAppError
from textual.containers import Container, VerticalScroll
from textual.widgets import Button, Static, TabbedContent, TabPane
from textual.screen import Screen

from ..widgets import LinkTree, ItemFormModal, ConfirmModal
from ...models import WorkItem
from ...storage import WorkSystem


class ItemDetailScreen(Screen):
    """Full screen view for inspecting a work item."""

    BINDINGS = [
        ("e", "edit", "Edit"),
        ("d", "delete", "Delete"),
        ("l", "link", "Link"),
        ("q", "close", "Close"),
    ]

    def __init__(self, item: WorkItem, work_system: WorkSystem) -> None:
        super().__init__()
        self.item = item
        self.work_system = work_system
        self._path: list[WorkItem] = []

    # --------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------
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
        return "\n".join(details)

    def _build_breadcrumb_items(self) -> list[WorkItem]:
        """Return the current breadcrumb history."""
        try:
            history = list(getattr(self.app, "breadcrumb_history", []))
        except NoActiveAppError:
            history = []
        if not history or history[-1].id != self.item.id:
            history.append(self.item)
        return history

    # --------------------------------------------------------------
    # Compose layout
    # --------------------------------------------------------------
    def compose(self) -> ComposeResult:
        if hasattr(self.app, "register_detail"):
            self.app.register_detail(self.item)
        self._path = self._build_breadcrumb_items()
        with Container(id="breadcrumbs"):
            for i, itm in enumerate(self._path):
                if i < len(self._path) - 1:
                    yield Button(itm.title or itm.id, id=f"crumb-{itm.id}")
                    yield Static(">", classes="crumb_sep")
                else:
                    yield Static(itm.title or itm.id, classes="crumb_current")
        with TabbedContent(id="detail_tabs"):
            with TabPane("Details", id="tab_details"):
                yield VerticalScroll(Static(self._build_details_text(), id="detail_text"))
            with TabPane("Links", id="tab_links"):
                yield LinkTree(id="detail_links", work_system=self.work_system)
            with TabPane("History", id="tab_history"):
                yield Static("No history available", id="detail_history")
        with Container(id="detail_actions"):
            yield Button("Edit", id="edit_button")
            yield Button("Link", id="link_button")
            yield Button("Delete", id="delete_button", variant="error")
            yield Button("Close", id="close_button")

    # --------------------------------------------------------------
    # Event handlers and actions
    # --------------------------------------------------------------
    def on_mount(self) -> None:
        tree = self.query_one("#detail_links", LinkTree)
        tree.load(self.item.id)

    def on_unmount(self) -> None:
        if hasattr(self.app, "unregister_detail"):
            self.app.unregister_detail(self.item)

    def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI actions
        if event.button.id == "edit_button":
            self.action_edit()
        elif event.button.id == "delete_button":
            self.action_delete()
        elif event.button.id == "link_button":
            self.action_link()
        elif event.button.id == "close_button":
            self.action_close()
        elif event.button.id and event.button.id.startswith("crumb-"):
            item_id = event.button.id.split("-", 1)[1]
            target = self.work_system.items.get(item_id)
            if target:
                self.app.push_screen(ItemDetailScreen(target, self.work_system))

    def action_edit(self) -> None:  # pragma: no cover - simple wrapper
        self.app.push_screen(ItemFormModal(self.item, self.work_system))

    def action_delete(self) -> None:  # pragma: no cover - simple wrapper
        modal = ConfirmModal(f"Delete '{self.item.title}'?", variant="danger")
        self.app.push_screen(modal, callback=self._on_delete_confirm)

    def action_link(self) -> None:  # pragma: no cover - simple wrapper
        self.app.push_screen(ItemFormModal(self.item, self.work_system))

    def action_close(self) -> None:  # pragma: no cover - simple wrapper
        self.app.pop_screen()

    def _on_delete_confirm(self, result: bool) -> None:
        if result:
            try:
                self.work_system.delete_item(self.item.id)
            except Exception:
                pass
        self.app.pop_screen()
