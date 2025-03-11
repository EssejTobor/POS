from textual.widgets import Static, Button, Input, Select, TextArea, Label
from textual.containers import Container, VerticalScroll, Horizontal
from textual import events
from textual.app import ComposeResult
import logging

from .base_screen import BaseScreen
from ..database import Database
from ..models import WorkItem, ItemType, ItemStatus, Priority
from ..config import Config

logger = logging.getLogger(__name__)

class WorkItemScreen(BaseScreen):
    """Work item management screen"""
    
    def __init__(self):
        super().__init__()
        self.db = Database(Config.DB_PATH)
        self.current_item = None
        self.current_goal = None
        logger.info("Work item screen initialized")
    
    def compose(self) -> ComposeResult:
        """Compose the work item screen layout"""
        yield Container(
            Static("Work Items", classes="title"),
            
            # Action buttons
            Container(
                Button("New Item", id="new-item"),
                Button("Edit Item", id="edit-item", disabled=True),
                Button("Complete Item", id="complete-item", disabled=True),
                Button("Link to Thought", id="link-thought", disabled=True),
                classes="button-row"
            ),
            
            # Filter controls
            Container(
                Static("Filter by Goal:", classes="label"),
                Input(placeholder="All Goals", id="goal-filter"),
                Button("Apply Filter", id="apply-filter"),
                classes="filter-controls"
            ),
            
            # Work items list and details
            Container(
                # Left side - work item list
                Container(
                    Static("Items", classes="section-title"),
                    VerticalScroll(
                        Static("No work items to display", id="item-list"),
                        id="item-list-scroll"
                    ),
                    id="item-list-container"
                ),
                
                # Right side - work item details
                Container(
                    Static("Item Details", classes="section-title"),
                    Static("No item selected", id="item-title"),
                    Static("Status: None", id="item-status"),
                    Static("Priority: None", id="item-priority"),
                    Static("Type: None", id="item-type"),
                    TextArea("", id="item-description", read_only=True),
                    id="item-details-container"
                ),
                id="work-item-container"
            ),
            id="work-items"
        )
    
    def on_mount(self):
        """Load data when screen is mounted"""
        self.load_items()
    
    def on_button_pressed(self, event: events.Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        try:
            if button_id == "new-item":
                self.show_new_item_dialog()
            elif button_id == "edit-item":
                if self.current_item:
                    self.show_edit_item_dialog(self.current_item)
            elif button_id == "complete-item":
                if self.current_item:
                    self.complete_item(self.current_item.id)
            elif button_id == "link-thought":
                if self.current_item:
                    self.show_link_thought_dialog(self.current_item)
            elif button_id == "apply-filter":
                goal = self.query_one("#goal-filter").value
                self.load_items(goal)
        except Exception as e:
            logger.error(f"Error handling button press: {e}", exc_info=True)
            self.show_error(f"Error: {str(e)}")
    
    def load_items(self, goal: str = None):
        """Load work items, optionally filtered by goal"""
        try:
            self.current_goal = goal
            
            if goal:
                items = self.db.get_items_by_goal(goal)
            else:
                items = self.db.get_incomplete_items()
            
            if items:
                # Update item list
                item_list = "\n".join([
                    f"• {item.title} ({item.status.value})" 
                    for item in items
                ])
                self.query_one("#item-list").update(item_list)
            else:
                filter_text = f" for goal '{goal}'" if goal else ""
                self.query_one("#item-list").update(f"No work items{filter_text}")
            
            # Clear current item selection
            self.current_item = None
            self.query_one("#item-title").update("No item selected")
            self.query_one("#item-status").update("Status: None")
            self.query_one("#item-priority").update("Priority: None")
            self.query_one("#item-type").update("Type: None")
            self.query_one("#item-description").value = ""
            self.query_one("#edit-item").disabled = True
            self.query_one("#complete-item").disabled = True
            self.query_one("#link-thought").disabled = True
            
            logger.info(f"Loaded {len(items)} work items{' for goal ' + goal if goal else ''}")
        except Exception as e:
            logger.error(f"Error loading work items: {e}", exc_info=True)
            self.show_error(f"Failed to load work items: {str(e)}")
    
    def show_new_item_dialog(self):
        """Show dialog to create a new work item"""
        # This would be implemented with a modal dialog in a full implementation
        # For now, we'll just log that this would happen
        logger.info("New work item dialog would be shown here")
    
    def show_edit_item_dialog(self, item: WorkItem):
        """Show dialog to edit a work item"""
        logger.info(f"Edit work item dialog would be shown here for {item.id}")
    
    def show_link_thought_dialog(self, item: WorkItem):
        """Show dialog to link a work item to a thought"""
        logger.info(f"Link thought dialog would be shown here for {item.id}")
    
    def complete_item(self, item_id: str):
        """Mark a work item as completed"""
        try:
            item = self.db.get_item(item_id)
            if item:
                item.update_status(ItemStatus.COMPLETED)
                self.db.update_item(item)
                logger.info(f"Work item {item_id} marked as completed")
                # Reload items to reflect changes
                self.load_items(self.current_goal)
            else:
                logger.error(f"Work item {item_id} not found")
                self.show_error("Work item not found")
        except Exception as e:
            logger.error(f"Error completing work item: {e}", exc_info=True)
            self.show_error(f"Error: {str(e)}") 