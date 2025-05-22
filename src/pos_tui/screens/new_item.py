"""
Screen for creating and editing work items.

Provides a form-based interface for entering new work items and editing existing ones.
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import LoadingIndicator
from textual.notifications import Notification

from ...models import WorkItem
from ..widgets import ItemEntryForm
from ..workers import ItemSaveWorker


class NewItemScreen(Screen):
    """Screen for entering and editing work items."""

    def compose(self) -> ComposeResult:
        """Compose the new item screen layout."""
        yield ItemEntryForm(id="item_entry_form")
        yield LoadingIndicator(id="save_indicator")
    
    def on_mount(self) -> None:
        """Set up event handlers when the screen is mounted."""
        # Hide the loading indicator initially
        self.query_one("#save_indicator").display = False
    
    def edit_item(self, item: WorkItem) -> None:
        """Set up the form to edit an existing item."""
        form = self.query_one(ItemEntryForm)
        form.edit_item(item)
        
    def on_item_entry_form_item_submitted(self, message: ItemEntryForm.ItemSubmitted) -> None:
        """Handle item submission from the form."""
        # Show the loading indicator
        loading = self.query_one("#save_indicator")
        loading.display = True
        
        # Start a worker to save the item with links
        worker = ItemSaveWorker()
        worker.completed.connect(self._on_save_completed)
        
        # Get item data and links from the message
        item_data = message.item_data
        links = message.links
        
        # If editing an existing item, include the ID
        item_id = item_data.get("id")
        
        # Start the worker
        worker.start(item_data=item_data, links=links, item_id=item_id)
    
    def _on_save_completed(self, worker):
        """Handle completion of the save worker."""
        # Hide the loading indicator
        loading = self.query_one("#save_indicator")
        loading.display = False
        
        result = worker.result
        
        if result.get("success", False):
            # Determine if this was a new item or an update
            is_new = result.get("is_new", True)
            item = result.get("item", {})
            
            # Show success notification
            action = "created" if is_new else "updated"
            self.notify(f"Item {action} successfully", title="Success", severity="information")
            
            # Dismiss the screen and return to previous screen
            self.dismiss()
        else:
            # Show error notification
            error_message = result.get("message", "An unknown error occurred")
            self.notify(error_message, title="Error", severity="error")
    
    def on_item_entry_form_edit_cancelled(self, _):
        """Handle edit cancellation from the form."""
        # Dismiss the screen and return to previous screen
        self.dismiss()
