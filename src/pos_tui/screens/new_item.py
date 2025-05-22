from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import LoadingIndicator, Static

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
        yield LoadingIndicator(id="screen_loading")
        yield Static("", id="screen_message")

    def on_mount(self) -> None:
        self.query_one("#screen_loading", LoadingIndicator).display = False

    def on_item_entry_form_save_started(
        self, event: ItemEntryForm.SaveStarted
    ) -> None:
        self.query_one("#screen_message", Static).update("")
        self.query_one("#screen_loading", LoadingIndicator).display = True

    def on_item_entry_form_save_result(
        self, event: ItemEntryForm.SaveResult
    ) -> None:
        loader = self.query_one("#screen_loading", LoadingIndicator)
        loader.display = False
        msg = self.query_one("#screen_message", Static)
        if event.success:
            msg.update("Saved!")
        else:
            msg.update(f"Error: {event.message}")

    def on_item_entry_form_cancelled(
        self, event: ItemEntryForm.Cancelled
    ) -> None:
        self.app.action_switch_tab("dashboard")
