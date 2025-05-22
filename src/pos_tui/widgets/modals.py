"""
Modals for the POS TUI application.

Contains modal screens for various interactive dialogs.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
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
        
        # Hide the cancel button in the form and use our own handlers
        form.query_one("#cancel_btn").display = False
    
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