from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen

from ...models import WorkItem
from ...storage import WorkSystem
from .item_form import ItemEntryForm


class ItemFormModal(ModalScreen[None]):
    """Modal wrapper for :class:`ItemEntryForm`."""

    def __init__(self, item: WorkItem, work_system: WorkSystem) -> None:
        super().__init__()
        self.item = item
        self.work_system = work_system

    def compose(self) -> ComposeResult:
        link_opts = [(s, s) for s in self.work_system.suggest_link_targets()]
        yield ItemEntryForm(
            work_system=self.work_system,
            tag_options=self.work_system.get_all_tags(),
            link_options=link_opts,
            item=self.item,
            id="edit_form",
        )
