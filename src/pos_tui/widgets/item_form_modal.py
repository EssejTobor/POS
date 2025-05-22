from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Select

from .modals import ConfirmModal

from ...models import WorkItem
from ...storage import WorkSystem
from .item_form import ItemEntryForm


class ItemFormModal(ModalScreen[None]):
    """Modal wrapper for :class:`ItemEntryForm`."""

    def __init__(self, item: WorkItem, work_system: WorkSystem) -> None:
        super().__init__()
        self.item = item
        self.work_system = work_system
        self.dirty = False
        self._original_data: dict[str, str] = {
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type.value,
            "priority": str(item.priority.value),
            "status": item.status.value,
        }

    def compose(self) -> ComposeResult:
        link_opts = [(s, s) for s in self.work_system.suggest_link_targets()]
        yield ItemEntryForm(
            work_system=self.work_system,
            tag_options=self.work_system.get_all_tags(),
            link_options=link_opts,
            item=self.item,
            id="edit_form",
        )

    # --------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------
    def _current_form_data(self) -> dict[str, str]:
        form = self.query_one("#edit_form", ItemEntryForm)
        return {
            "title": form.query_one("#title_field", Input).value,
            "description": form.query_one("#description_field", Input).value,
            "item_type": form.query_one("#type_selector", Select).value or "",
            "priority": form.query_one("#priority_selector", Select).value or "",
            "status": form.query_one("#status_selector", Select).value or "",
        }

    def _update_dirty(self) -> None:
        self.dirty = self._current_form_data() != self._original_data

    def _attempt_close(self) -> None:
        if self.dirty:
            modal = ConfirmModal("Discard changes?")

            def _cb(result: bool) -> None:
                if result:
                    self.dismiss(None)

            self.app.push_screen(modal, callback=_cb)
        else:
            self.dismiss(None)

    # --------------------------------------------------------------
    # Event Handlers
    # --------------------------------------------------------------
    def on_input_changed(self, event: Input.Changed) -> None:  # pragma: no cover - simple
        self._update_dirty()

    def on_select_changed(self, event: Select.Changed) -> None:  # pragma: no cover - simple
        self._update_dirty()

    def on_item_entry_form_save_result(self, event: ItemEntryForm.SaveResult) -> None:
        if event.success:
            self.dirty = False
            updated_item = self.work_system.items.get(self.item.id, self.item)
            self.dismiss(updated_item)

    def on_item_entry_form_cancelled(self, event: ItemEntryForm.Cancelled) -> None:
        self._attempt_close()
