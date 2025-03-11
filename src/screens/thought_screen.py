"""
Main screen for the Thought Evolution Tracker.
"""
from typing import Optional, Dict, Any, List
import logging
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Label, Header, Footer
from textual import events, work

from ..models import ThoughtNode, ThoughtStatus, BranchType
from ..thought_manager import ThoughtManager
from ..ui.thought_list import ThoughtList, ThoughtSelected
from ..ui.thought_widgets import ThoughtVisualizer
from ..ui.thought_dialogs import (
    AddThoughtDialog, EditThoughtDialog, BranchThoughtDialog,
    VisualizeThoughtDialog, ConfirmDeleteDialog, DialogResult
)

logger = logging.getLogger(__name__)

class ThoughtScreen(Screen):
    """Main screen for the Thought Evolution Tracker"""
    
    BINDINGS = [
        ("a", "add_thought", "Add Thought"),
        ("e", "edit_thought", "Edit Thought"),
        ("d", "delete_thought", "Delete Thought"),
        ("b", "branch_thought", "Branch Thought"),
        ("v", "visualize", "Visualize"),
        ("r", "refresh", "Refresh"),
        ("f", "focus_search", "Search"),
        ("escape", "back", "Back")
    ]
    
    CSS_PATH = "../assets/thought.tcss"
    
    def __init__(self, thought_manager: ThoughtManager, **kwargs):
        super().__init__(**kwargs)
        self.thought_manager = thought_manager
        self.selected_thought: Optional[ThoughtNode] = None
        
    def compose(self) -> ComposeResult:
        """Compose the screen layout"""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            # Left panel - Thought list
            with Vertical(id="left-panel"):
                yield ThoughtList(id="thought-list")
            
            # Right panel - Thought details and visualization
            with Vertical(id="right-panel"):
                # Thought details
                yield Label("Thought Details", classes="section-title")
                yield Static("Select a thought to view details", id="thought-details")
                
                # Thought visualization
                yield ThoughtVisualizer(id="thought-visualizer")
                
                # Action buttons
                with Horizontal(classes="action-buttons"):
                    yield Button("Edit", id="edit-button", disabled=True)
                    yield Button("Branch", id="branch-button", disabled=True)
                    yield Button("Delete", id="delete-button", disabled=True)
                    yield Button("Visualize", id="visualize-button", disabled=True)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Load thoughts when the screen is mounted"""
        self.refresh_thoughts()
    
    @work(thread=True)
    def refresh_thoughts(self) -> None:
        """Refresh the list of thoughts"""
        try:
            thoughts = self.thought_manager.get_all_thoughts()
            self.update_thought_list(thoughts)
        except Exception as e:
            logger.error(f"Error loading thoughts: {e}")
            self.notify(f"Error loading thoughts: {e}", severity="error")
    
    def update_thought_list(self, thoughts: List[ThoughtNode]) -> None:
        """Update the thought list with the provided thoughts"""
        thought_list = self.query_one("#thought-list", ThoughtList)
        thought_list.update_thoughts(thoughts)
    
    def update_thought_details(self) -> None:
        """Update the thought details panel"""
        details = self.query_one("#thought-details", Static)
        
        if not self.selected_thought:
            details.update("Select a thought to view details")
            return
        
        # Format the thought details
        thought = self.selected_thought
        status_color = {
            ThoughtStatus.DRAFT: "yellow",
            ThoughtStatus.EVOLVING: "blue",
            ThoughtStatus.CRYSTALLIZED: "green"
        }.get(thought.status, "white")
        
        details_text = f"""[bold]Title:[/bold] {thought.title}
[bold]Status:[/bold] [{status_color}]{thought.status.value.title()}[/{status_color}]
[bold]Branch:[/bold] {thought.branch_name}
[bold]Created:[/bold] {thought.created_at.strftime('%Y-%m-%d %H:%M')}
[bold]Updated:[/bold] {thought.updated_at.strftime('%Y-%m-%d %H:%M')}
"""
        
        if thought.tags:
            details_text += f"[bold]Tags:[/bold] {', '.join(['#' + tag for tag in thought.tags])}\n"
        
        details_text += f"\n[bold]Content:[/bold]\n{thought.content}"
        
        details.update(details_text)
        
        # Update the visualizer
        self.update_visualizer()
        
        # Enable action buttons
        self.query_one("#edit-button").disabled = False
        self.query_one("#branch-button").disabled = False
        self.query_one("#delete-button").disabled = False
        self.query_one("#visualize-button").disabled = False
    
    @work(thread=True)
    def update_visualizer(self) -> None:
        """Update the thought visualizer"""
        if not self.selected_thought:
            return
            
        try:
            # Get the ASCII tree for the selected thought
            ascii_tree = self.thought_manager.visualize_thought_tree(
                self.selected_thought.id, 
                max_depth=3,  # Limit depth for the preview
                include_content=False
            )
            
            # Update the visualizer
            visualizer = self.query_one("#thought-visualizer", ThoughtVisualizer)
            visualizer.ascii_tree = ascii_tree
            visualizer.refresh()
        except Exception as e:
            logger.error(f"Error updating visualizer: {e}")
            self.notify(f"Error updating visualizer: {e}", severity="error")
    
    def on_thought_selected(self, event: ThoughtSelected) -> None:
        """Handle thought selection"""
        try:
            # Load the selected thought
            thought = self.thought_manager.get_thought_by_id(event.thought_id)
            if thought:
                self.selected_thought = thought
                self.update_thought_details()
        except Exception as e:
            logger.error(f"Error loading thought: {e}")
            self.notify(f"Error loading thought: {e}", severity="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "edit-button" and self.selected_thought:
            self.action_edit_thought()
        elif button_id == "branch-button" and self.selected_thought:
            self.action_branch_thought()
        elif button_id == "delete-button" and self.selected_thought:
            self.action_delete_thought()
        elif button_id == "visualize-button" and self.selected_thought:
            self.action_visualize()
    
    def on_thought_list_add_thought(self) -> None:
        """Handle add thought event from the list"""
        self.action_add_thought()
    
    def on_thought_list_refresh_requested(self) -> None:
        """Handle refresh request from the list"""
        self.refresh_thoughts()
    
    def action_add_thought(self) -> None:
        """Show dialog to add a new thought"""
        self.app.push_screen(AddThoughtDialog("add-thought"))
    
    def action_edit_thought(self) -> None:
        """Show dialog to edit the selected thought"""
        if self.selected_thought:
            self.app.push_screen(EditThoughtDialog("edit-thought", self.selected_thought))
    
    def action_branch_thought(self) -> None:
        """Show dialog to create a branch from the selected thought"""
        if self.selected_thought:
            self.app.push_screen(BranchThoughtDialog("branch-thought", self.selected_thought))
    
    def action_delete_thought(self) -> None:
        """Show dialog to confirm deletion of the selected thought"""
        if self.selected_thought:
            self.app.push_screen(ConfirmDeleteDialog("delete-thought", self.selected_thought))
    
    def action_visualize(self) -> None:
        """Show dialog with full visualization of the thought tree"""
        if not self.selected_thought:
            return
            
        try:
            # Get the full ASCII tree for the selected thought
            ascii_tree = self.thought_manager.visualize_thought_tree(
                self.selected_thought.id, 
                max_depth=None,  # No depth limit
                include_content=True
            )
            
            # Show the visualization dialog
            self.app.push_screen(VisualizeThoughtDialog("visualize-thought", ascii_tree))
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            self.notify(f"Error creating visualization: {e}", severity="error")
    
    def action_refresh(self) -> None:
        """Refresh the thoughts list"""
        self.refresh_thoughts()
    
    def action_focus_search(self) -> None:
        """Focus the search input"""
        # If we have a search input, focus it
        search_input = self.query("#thought-search")
        if search_input:
            search_input.focus()
    
    def action_back(self) -> None:
        """Go back to the main screen"""
        self.app.switch_screen("main")
    
    def on_dialog_result(self, event: DialogResult) -> None:
        """Handle dialog results"""
        dialog_id = event.dialog_id
        result = event.result
        action = event.action
        
        if action == "dismiss":
            return
            
        try:
            if dialog_id == "add-thought" and action == "create":
                # Create a new thought
                self.thought_manager.add_thought(
                    title=result["title"],
                    content=result["content"],
                    branch_name=result["branch_name"],
                    tags=result["tags"],
                    status=ThoughtStatus(result["status"])
                )
                self.notify("Thought created successfully")
                
            elif dialog_id == "edit-thought" and action == "update":
                # Update the thought
                self.thought_manager.update_thought(
                    thought_id=result["id"],
                    title=result["title"],
                    content=result["content"],
                    branch_name=result["branch_name"],
                    tags=result["tags"],
                    status=ThoughtStatus(result["status"])
                )
                self.notify("Thought updated successfully")
                
            elif dialog_id == "branch-thought" and action == "branch":
                # Create a branch
                self.thought_manager.branch_thought(
                    parent_id=result["parent_id"],
                    title=result["title"],
                    content=result["content"],
                    branch_name=result["branch_name"],
                    branch_type=BranchType(result["branch_type"]),
                    tags=result["tags"],
                    status=ThoughtStatus(result["status"])
                )
                self.notify("Branch created successfully")
                
            elif dialog_id == "delete-thought" and action == "delete":
                # Delete the thought
                self.thought_manager.delete_thought(result["id"])
                self.selected_thought = None
                self.query_one("#thought-details").update("Select a thought to view details")
                self.query_one("#edit-button").disabled = True
                self.query_one("#branch-button").disabled = True
                self.query_one("#delete-button").disabled = True
                self.query_one("#visualize-button").disabled = True
                self.notify("Thought deleted successfully")
                
            # Refresh the thoughts list
            self.refresh_thoughts()
            
        except Exception as e:
            logger.error(f"Error processing dialog result: {e}")
            self.notify(f"Error: {e}", severity="error") 