"""
Table widget for displaying work items with advanced features.

Provides a sortable, filterable table with pagination and row styling based on item properties.
"""

from typing import Dict, List, Optional, Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Button, DataTable, Label, Static
from textual.widgets.data_table import RowKey
from textual.coordinate import Coordinate


class ItemTable(DataTable):
    """Table for displaying work items with sorting, styling, and pagination."""
    
    DEFAULT_CSS = """
    ItemTable {
        height: 1fr;
    }
    
    ItemTable > .high {
        background: $error-darken-1;
    }
    
    ItemTable > .medium {
        background: $warning-darken-1;
    }
    
    ItemTable > .low {
        background: $surface;
    }
    
    ItemTable > .completed {
        text-style: strike;
    }
    
    ItemTable > .in-progress {
        background: $primary-darken-1;
    }
    """
    
    class ItemSelected(Message):
        """Message sent when an item is selected."""
        def __init__(self, item_id: str) -> None:
            self.item_id = item_id
            super().__init__()
    
    class ItemEditRequested(Message):
        """Message sent when an item edit is requested."""
        def __init__(self, item_id: str) -> None:
            self.item_id = item_id
            super().__init__()
    
    class ItemDeleteRequested(Message):
        """Message sent when an item deletion is requested."""
        def __init__(self, item_id: str) -> None:
            self.item_id = item_id
            super().__init__()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self._page_size = 15
        self._current_page = 1
        self._total_items = 0
        self._total_pages = 1
        
    def on_mount(self) -> None:
        """Set up the table when mounted."""
        # Add columns with sorting enabled
        self.add_column("ID", width=12)
        self.add_column("Title", width=30) 
        self.add_column("Type", width=10)
        self.add_column("Status", width=12)
        self.add_column("Priority", width=8)
        self.add_column("Due Date", width=10)
        self.add_column("Actions", width=10)
        
        # Make columns sortable
        for column_key in self.columns.keys():
            if column_key != 6:  # Skip Actions column
                self.columns[column_key].sortable = True
    
    @on(DataTable.HeaderSelected)
    def handle_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header selection for sorting."""
        # Don't sort the action column
        if event.column_index == 6:
            event.stop()
            return
            
        self.sort(event.column_index)
        # Prevent event bubbling
        event.stop()
    
    @on(DataTable.RowSelected)    
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection to show item details."""
        if event.row_key is not None:
            self.post_message(self.ItemSelected(str(event.row_key)))
    
    @on(DataTable.CellSelected)
    def handle_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Handle cell selection in the actions column."""
        if event.coordinate.column == 6 and event.value == "✏️":
            # Edit button clicked
            if event.row_key is not None:
                self.post_message(self.ItemEditRequested(str(event.row_key)))
                event.stop()
    
    def on_mouse_down(self, event) -> None:
        """Handle mouse down events."""
        # Only handle right clicks
        if event.button != 3:  # 3 is right button
            return
            
        # Get the coordinate of the cell that was clicked
        coordinate = self.get_cell_at(event.screen_x, event.screen_y)
        if coordinate is not None:
            self.show_context_menu(coordinate)
            event.stop()
    
    def show_context_menu(self, coordinate: Coordinate) -> None:
        """Show a context menu for the given coordinate."""
        row_key = self.coordinate_to_row_key(coordinate)
        if row_key is None:
            return
            
        # Create a context menu for this item
        from textual.widgets import ContextMenu
        menu = ContextMenu()
        
        menu.add_item("View Details", id=f"view_details:{row_key}")
        menu.add_item("Edit Item", id=f"edit_item:{row_key}")
        menu.add_item("Delete Item", id=f"delete_item:{row_key}")
        
        self.app.push_screen(menu)
    
    def on_context_menu_item_selected(self, event) -> None:
        """Handle context menu item selection."""
        menu_id = event.item_id
        
        if ":" not in menu_id:
            return
            
        action, item_id = menu_id.split(":", 1)
        
        if action == "view_details":
            self.post_message(self.ItemSelected(item_id))
        elif action == "edit_item":
            self.post_message(self.ItemEditRequested(item_id))
        elif action == "delete_item":
            self.post_message(self.ItemDeleteRequested(item_id))
    
    def apply_row_styling(self) -> None:
        """Apply styling to rows based on priority and status."""
        for row_key in self.row_keys:
            row = self.get_row(row_key)
            if row is None:
                continue
                
            # Apply priority styling
            priority = row[4]
            status = row[3]
            
            # Priority styles
            if priority == "3":
                self.add_row_class(row_key, "high")
            elif priority == "2":
                self.add_row_class(row_key, "medium")
            else:
                self.add_row_class(row_key, "low")
                
            # Status styles
            if status == "completed":
                self.add_row_class(row_key, "completed")
            elif status == "in_progress":
                self.add_row_class(row_key, "in-progress")
                
    def add_row(self, *args, **kwargs) -> Optional[RowKey]:
        """Override add_row to apply styling after adding a row and add action buttons."""
        # Add edit button to actions column
        if len(args) == 6:  # If no action cell provided
            args = list(args)  # Convert to list so we can modify
            args.append("✏️")  # Add edit button
        
        row_key = super().add_row(*args, **kwargs)
        self.apply_row_styling()
        return row_key
    
    def update_cell(self, row_key: RowKey, column_index: int, value: Any) -> None:
        """Update a specific cell in the table.
        
        Args:
            row_key: The key of the row to update
            column_index: The index of the column to update
            value: The new value for the cell
        """
        if row_key not in self.row_keys:
            return
            
        # Update the cell with the new value
        self.update_cell_at(Coordinate(row=self.row_keys.index(row_key), column=column_index), value)
        
        # If we're updating a cell that affects styling, reapply styling
        if column_index in [3, 4]:  # Status or Priority columns
            self.apply_row_styling()
    
    def next_page(self) -> None:
        """Go to the next page of items."""
        if self._current_page < self._total_pages:
            self._current_page += 1
            self.emit_page_changed()
    
    def prev_page(self) -> None:
        """Go to the previous page of items."""
        if self._current_page > 1:
            self._current_page -= 1
            self.emit_page_changed()
    
    def set_page(self, page_number: int) -> None:
        """Set the current page."""
        if 1 <= page_number <= self._total_pages:
            self._current_page = page_number
            self.emit_page_changed()
    
    def emit_page_changed(self) -> None:
        """Emit event when the page changes."""
        # This would be implemented to notify parent components
        # about pagination changes
        pass
    
    def update_pagination_info(self, total_items: int) -> None:
        """Update pagination information."""
        self._total_items = total_items
        self._total_pages = max(1, (total_items + self._page_size - 1) // self._page_size)
        
        if self._current_page > self._total_pages:
            self._current_page = self._total_pages
