"""
Dashboard screen for displaying and managing work items.

Provides an overview of work items with filtering, sorting and action capabilities.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Union

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, LoadingIndicator, Select, Static
from textual.notifications import Notification
from textual.worker import Worker, get_current_worker

from ...models import ItemStatus, ItemType, Priority, WorkItem
from ..widgets import FilterBar, ItemDetailsModal, ItemTable
from ..widgets.modals import EditItemModal


class DashboardScreen(Screen):
    """Screen displaying an overview of work items with filtering and management capabilities."""

    BINDINGS = [
        ("e", "edit_selected_row", "Edit"),
        ("d", "delete_selected_row", "Delete"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        # Header section
        yield Header(show_clock=True)
        
        # Main content area
        with Container(id="dashboard-content"):
            # Filter and search section
            yield FilterBar(id="filter_bar")
            
            # Work items table
            yield ItemTable(id="dashboard_table")
            
            # Status message
            yield Static("Loading items...", id="status_message")
            
            # Loading indicator
            yield LoadingIndicator(id="loading_indicator")
            
            # Action buttons section
            with Horizontal(id="action_buttons"):
                yield Button("Refresh", id="refresh_btn", variant="primary")
                yield Button("New Item", id="new_item_btn", variant="success")
                yield Button("Details", id="details_btn", variant="default", disabled=True)
                yield Button("Edit", id="edit_btn", variant="default", disabled=True)
                yield Button("Delete", id="delete_btn", variant="error", disabled=True)
        
        # Footer with helpful information
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the dashboard after it's mounted."""
        # Hide loading indicator initially
        self.query_one("#loading_indicator").display = False
        
        # Start loading data
        self.load_data()
    
    def on_item_table_item_selected(self, event: ItemTable.ItemSelected) -> None:
        """Handle item selection in the table."""
        # Enable action buttons when an item is selected
        self._update_action_buttons(True)

        # Store the selected item ID
        self._selected_item_id = event.item_id
        self._launch_edit_screen(event.item_id)
    
    def on_filter_bar_filter_changed(self, event: FilterBar.FilterChanged) -> None:
        """Handle filter change events from the filter bar."""
        # Update status message
        status = self.query_one("#status_message", Static)
        status.update("Applying filters...")
        
        # Show loading indicator
        self.query_one("#loading_indicator").display = True
        
        # Schedule async task to fetch filtered items
        asyncio.create_task(
            self.fetch_filtered_items(
                item_type=event.item_type,
                search_text=event.search_text,
                status=event.status,
                goal_filter=event.goal_filter
            )
        )
    
    async def fetch_filtered_items(
        self,
        item_type: Optional[str] = None,
        search_text: Optional[str] = None,
        status: Optional[str] = None,
        goal_filter: Optional[str] = None,
    ) -> None:
        """Fetch items from database with filters applied."""
        # Get reference to the app and work system
        app = self.app
        if not hasattr(app, "work_system"):
            return
            
        work_system = app.work_system
        
        # Convert string values to enum types if needed
        status_enum = None
        if status:
            for s in ItemStatus:
                if s.value == status:
                    status_enum = s
                    break
        
        type_enum = None
        if item_type:
            for t in ItemType:
                if t.value == item_type:
                    type_enum = t
                    break
        
        # Get filtered items
        items = work_system.get_filtered_items(
            goal=goal_filter,
            item_type=type_enum,
            status=status_enum,
            search_text=search_text,
        )
        
        # Simulate a delay to show loading (remove in production)
        await asyncio.sleep(0.5)
        
        # Hide loading indicator and update UI
        self.query_one("#loading_indicator").display = False
        status = self.query_one("#status_message", Static)
        status.update(f"{len(items)} items found")
        
        # Populate the table
        self.populate_table(items)
    
    def load_data(self) -> None:
        """Load work items data from the database."""
        # Update status message
        status = self.query_one("#status_message", Static)
        status.update("Loading items...")
        
        # Show loading indicator
        self.query_one("#loading_indicator").display = True
        
        # Disable action buttons while loading
        self._update_action_buttons(False)
        
        # Schedule async task to fetch items
        asyncio.create_task(self.fetch_items())
    
    async def fetch_items(self) -> None:
        """Fetch items from database asynchronously."""
        # Get reference to the app and work system
        app = self.app
        if not hasattr(app, "work_system"):
            return
            
        work_system = app.work_system
        # Fetch incomplete items as the default view
        items = work_system.get_incomplete_items()
        
        # Simulate a delay to show loading (remove in production)
        await asyncio.sleep(0.5)
        
        # Hide loading indicator and update UI
        self.query_one("#loading_indicator").display = False
        status = self.query_one("#status_message", Static)
        status.update(f"{len(items)} items found")
        
        # Populate the table
        self.populate_table(items)
    
    def populate_table(self, items: List[WorkItem]) -> None:
        """Populate the table with work items."""
        table = self.query_one("#dashboard_table", ItemTable)
        table.clear()
        
        # Add items to the table
        for item in items:
            # Format the due date (if we had one)
            due_date = datetime.now().strftime("%Y-%m-%d") if hasattr(item, "due_date") else ""
            
            # Add the row with appropriate styling based on priority and status
            table.add_row(
                item.id,
                item.title,
                item.goal,
                item.item_type.value,
                item.status.value,
                str(item.priority.value),
                due_date,
                key=item.id,
            )
        
        # Update pagination info
        table.update_pagination_info(len(items))

    def refresh_items(self) -> None:
        """Refresh the dashboard data."""
        self.load_data()
    
    def _update_action_buttons(self, enabled: bool) -> None:
        """Enable or disable action buttons."""
        self.query_one("#details_btn").disabled = not enabled
        self.query_one("#edit_btn").disabled = not enabled
        self.query_one("#delete_btn").disabled = not enabled
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "refresh_btn":
            self.load_data()
        
        elif button_id == "new_item_btn":
            # Switch to the New Item tab
            app = self.app
            app.action_switch_tab("new-item")
            
        elif button_id == "details_btn":
            # Show item details modal
            if hasattr(self, "_selected_item_id"):
                self._show_item_details(self._selected_item_id)
                
        elif button_id == "edit_btn":
            # Show the edit item modal for the selected item
            if hasattr(self, "_selected_item_id"):
                self._edit_item(self._selected_item_id)
            
        elif button_id == "delete_btn":
            # Delete the selected item
            if hasattr(self, "_selected_item_id"):
                self._delete_item(self._selected_item_id)
    
    def _show_item_details(self, item_id: str) -> None:
        """Show the item details modal for the selected item."""
        # Get reference to the app and work system
        app = self.app
        if not hasattr(app, "work_system"):
            return
            
        work_system = app.work_system
        item = work_system.items.get(item_id)
        
        if item:
            # Show the modal with item details
            self.app.push_screen(ItemDetailsModal(item))

    def _launch_edit_screen(self, item_id: str) -> None:
        """Open the NewItemScreen pre-filled with the selected item."""
        app = self.app
        if not hasattr(app, "work_system"):
            return
        work_system = app.work_system
        item = work_system.items.get(item_id)
        if item:
            self.app.push_screen(NewItemScreen(item=item.to_dict()))
            
    def _edit_item(self, item_id: str) -> None:
        """Show the edit item modal for the selected item."""
        # Get reference to the app and work system
        app = self.app
        if not hasattr(app, "work_system"):
            return
            
        work_system = app.work_system
        item = work_system.items.get(item_id)
        
        if item:
            # Cache the original item for potential undo
            original_item = item.copy()
            
            # Show the modal with edit form
            def handle_edit_result(result):
                if result:
                    # Optimistically update the UI
                    table = self.query_one("#dashboard_table", ItemTable)
                    
                    # Prepare row data for the updated item
                    updated_item = original_item.copy()
                    for key, value in result.items():
                        setattr(updated_item, key, value)
                    
                    # Find the row index with the item_id
                    row_index = None
                    for i, row_key in enumerate(table.row_keys):
                        if str(row_key) == item_id:
                            row_index = i
                            break
                    
                    if row_index is not None:
                        # Update the row directly (optimistically)
                        table.update_cell(item_id, 1, updated_item.title)
                        table.update_cell(item_id, 2, updated_item.item_type.value if hasattr(updated_item, "item_type") else "")
                        table.update_cell(item_id, 3, updated_item.status.value if hasattr(updated_item, "status") else "")
                        table.update_cell(item_id, 4, str(updated_item.priority.value) if hasattr(updated_item, "priority") else "")
                        
                        # Apply styling based on new values
                        table.apply_row_styling()
                        
                        # Show success notification with undo option
                        def undo_edit():
                            # Revert to original values in UI
                            table.update_cell(item_id, 1, original_item.title)
                            table.update_cell(item_id, 2, original_item.item_type.value)
                            table.update_cell(item_id, 3, original_item.status.value)
                            table.update_cell(item_id, 4, str(original_item.priority.value))
                            
                            # Revert in database
                            work_system.update_item(item_id, {
                                "title": original_item.title,
                                "item_type": original_item.item_type.value,
                                "status": original_item.status.value,
                                "priority": original_item.priority.value,
                                "description": original_item.description,
                                "tags": getattr(original_item, "tags", [])
                            })
                            
                            # Show confirmation of undo
                            self.notify("Edit undone", severity="information")
                        
                        self.notify("Item updated successfully", severity="success", timeout=5.0, buttons=[("Undo", undo_edit)])
                    
                    # Actually update the database in the background
                    asyncio.create_task(self._update_item_async(item_id, result))
            
            self.app.push_screen(EditItemModal(item), callback=handle_edit_result)
    
    async def _update_item_async(self, item_id: str, item_data: Dict[str, Union[str, int, bool]]) -> None:
        """Update an item in the database asynchronously."""
        # Get reference to the app and work system
        app = self.app
        if not hasattr(app, "work_system"):
            return
            
        work_system = app.work_system
        
        try:
            # Update the item
            work_system.update_item(item_id, item_data)
        except Exception as e:
            # If there was an error, show notification
            self.notify(f"Error updating item: {str(e)}", severity="error")
            # Refresh to show accurate data
            self.load_data()
    
    def _delete_item(self, item_id: str) -> None:
        """Delete the selected item after confirmation."""
        from ..widgets import ConfirmModal
        
        # Get reference to the app and work system
        app = self.app
        if not hasattr(app, "work_system"):
            return
            
        work_system = app.work_system
        
        # Get a copy of the item for potential undo
        original_item = None
        if item_id in work_system.items:
            original_item = work_system.items[item_id].copy()
        
        if not original_item:
            self.notify("Item not found", severity="error")
            return
        
        # Show the confirmation modal with callback
        def handle_delete_confirmation(confirmed: bool) -> None:
            if confirmed:
                # Get the dashboard screen and table
                dashboard = self.app.query_one("DashboardScreen")
                table = dashboard.query_one("#dashboard_table", ItemTable)
                
                # Remove the row from the table (optimistic UI update)
                table.remove_row(item_id)
                
                # Show success notification with undo option
                def undo_delete():
                    # Restore the item in the database
                    work_system.items[item_id] = original_item
                    work_system.save_item(original_item)
                    
                    # Refresh the display to show the restored item
                    dashboard.load_data()
                    
                    # Show confirmation of undo
                    dashboard.notify("Delete undone", severity="information")
                
                dashboard.notify("Item deleted", severity="success", timeout=5.0, buttons=[("Undo", undo_delete)])
                
                # Run the actual delete operation asynchronously
                asyncio.create_task(dashboard._delete_item_async(item_id))
        
        self.app.push_screen(ConfirmModal("Delete this item?", variant="danger"), callback=handle_delete_confirmation)
    
    async def _delete_item_async(self, item_id: str) -> None:
        """Delete an item from the database asynchronously."""
        # Get reference to the app and work system
        app = self.app
        if not hasattr(app, "work_system"):
            return
            
        work_system = app.work_system
        
        try:
            # Delete the item
            work_system.delete_item(item_id)
        except Exception as e:
            # If there was an error, show notification
            self.notify(f"Error deleting item: {str(e)}", severity="error")
            # Refresh to show accurate data
            self.load_data()
    
    def notify(self, message: str, severity: str = "information", timeout: float = 3.0, buttons: List = None) -> None:
        """Show a notification toast."""
        # Create a notification
        notification = Notification(message, title=None, timeout=timeout)
        
        # Add buttons if provided
        if buttons:
            for label, callback in buttons:
                notification.add_action(label, callback)
        
        # Show the notification
        self.app.notify(notification)

    def on_item_table_item_edit_requested(self, event: ItemTable.ItemEditRequested) -> None:
        """Handle edit request from the item table."""
        self._edit_item(event.item_id)
    
    def on_item_table_item_delete_requested(self, event: ItemTable.ItemDeleteRequested) -> None:
        """Handle delete request from the item table."""
        self._delete_item(event.item_id)

    def action_edit_selected_row(self) -> None:
        if hasattr(self, "_selected_item_id"):
            self._launch_edit_screen(self._selected_item_id)

    def action_delete_selected_row(self) -> None:
        if hasattr(self, "_selected_item_id"):
            self._delete_item(self._selected_item_id)
