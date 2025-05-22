"""
Modals for the POS TUI application.

Contains modal screens for various interactive dialogs.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Center
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from ...models import WorkItem
from .item_form import ItemEntryForm


class EditItemModal(ModalScreen):
    """Modal screen for editing work items."""
    
    DEFAULT_CSS = """
    EditItemModal {
        align: center middle;
    }
    
    #edit-container {
        background: $surface;
        border: thick $primary;
        width: 90%;
        height: 90%;
        padding: 1 2;
    }
    
    #edit-title {
        text-style: bold;
        text-align: center;
        width: 100%;
        background: $primary;
        padding: 1 0;
        color: $text;
        margin-bottom: 1;
    }
    """
    
    def __init__(self, item: WorkItem, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
    
    def compose(self) -> ComposeResult:
        """Compose the edit item modal."""
        with Container(id="edit-container"):
            yield Static(f"Edit Item: {self.item.title}", id="edit-title")
            
            # Use the existing ItemEntryForm component
            form = ItemEntryForm(id="edit-item-form")
            yield form
    
    def on_mount(self) -> None:
        """Configure the form when the modal is mounted."""
        # Get the form and set it up for editing
        form = self.query_one("#edit-item-form", ItemEntryForm)
        form.edit_item(self.item)
        

        # Keep reference to form for dirty check
        self.form = form
    
    def on_item_entry_form_item_submitted(self, message: ItemEntryForm.ItemSubmitted) -> None:
        """Handle form submission from the edit form."""
        # Save the updated item data
        self.dismiss(message.item_data)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the form."""
        button_id = event.button.id
        
        if button_id == "clear_btn":
            # Just reset the form to the original item data
            form = self.query_one("#edit-item-form", ItemEntryForm)
            form.edit_item(self.item)
        elif button_id == "submit_btn":
            # The form's own submit handler will trigger item_submitted
            pass
        elif button_id == "cancel_btn":
            if self.form.is_dirty():
                def _done(result: bool) -> None:
                    if result:
                        self.dismiss(None)
                self.app.push_screen(
                    ConfirmModal("Discard changes?", variant="warning"),
                    callback=_done,
                )
            else:
                self.dismiss(None)


class ConfirmModal(ModalScreen[bool]):
    """Simple yes/no confirmation modal."""

    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
    }

    #confirm-container {
        background: $surface;
        border: tall $primary;
        width: 40%;
        height: auto;
        padding: 1 2;
    }

    #confirm-message {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }

    #confirm-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #confirm-buttons Button {
        margin: 0 1;
    }
    """

    def __init__(self, message: str, variant: str | None = None) -> None:
        super().__init__()
        self.message = message
        self.variant = variant

    def compose(self) -> ComposeResult:
        with Center():
            with Container(id="confirm-container"):
                yield Static(self.message, id="confirm-message")
                with Horizontal(id="confirm-buttons"):
                    yield Button("Cancel", id="cancel_btn", variant="primary")
                    yield Button("OK", id="ok_btn", variant=self.variant or "success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok_btn":
            self.dismiss(True)
        elif event.button.id == "cancel_btn":
            self.dismiss(False)
