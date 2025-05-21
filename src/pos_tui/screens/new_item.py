from textual.app import ComposeResult
from textual.containers import Container

from ..widgets import ItemEntryForm


class NewItemScreen(Container):
    """Screen for entering new work items."""

    def compose(self) -> ComposeResult:
        ws = self.app.work_system
        link_opts = [(s, s) for s in ws.suggest_link_targets()] if ws else []
        yield ItemEntryForm(
            id="item_entry_form",
            tag_options=ws.get_all_tags() if ws else None,
            link_options=link_opts,
            work_system=ws,
        )
