from textual.widgets import Static, Button, Input, TextArea, Label
from textual.containers import Container, VerticalScroll, Horizontal
from textual import events
from textual.app import ComposeResult
import logging

from .base_screen import BaseScreen
from ..thought_manager import ThoughtManager
from ..models import ThoughtNode, ThoughtStatus, BranchType
from ..config import Config

logger = logging.getLogger(__name__)

class ThoughtScreen(BaseScreen):
    """Thought Evolution Tracker screen for managing thoughts"""
    
    def __init__(self):
        super().__init__()
        self.thought_manager = ThoughtManager(Config.DB_PATH)
        self.current_thought = None
        self.current_branch = "main"
        logger.info("Thought screen initialized")
    
    def compose(self) -> ComposeResult:
        """Compose the thought screen layout"""
        yield Container(
            Static("Thought Evolution Tracker", classes="title"),
            
            # Action buttons
            Container(
                Button("New Thought", id="new-thought"),
                Button("Branch Thought", id="branch-thought", disabled=True),
                Button("Merge Thoughts", id="merge-thoughts"),
                Button("Crystallize", id="crystallize-thought", disabled=True),
                classes="button-row"
            ),
            
            # Branch selector
            Container(
                Static("Branch:", classes="label"),
                Input(placeholder="main", id="branch-input", value="main"),
                Button("Load Branch", id="load-branch"),
                classes="branch-selector"
            ),
            
            # Thought list and details
            Container(
                # Left side - thought list
                Container(
                    Static("Thoughts", classes="section-title"),
                    VerticalScroll(
                        Static("No thoughts to display", id="thought-list"),
                        id="thought-list-scroll"
                    ),
                    id="thought-list-container"
                ),
                
                # Right side - thought details
                Container(
                    Static("Thought Details", classes="section-title"),
                    Static("No thought selected", id="thought-title"),
                    Static("Status: None", id="thought-status"),
                    TextArea("", id="thought-content", read_only=True),
                    Container(
                        Button("Edit", id="edit-thought", disabled=True),
                        Button("View Lineage", id="view-lineage", disabled=True),
                        classes="button-row"
                    ),
                    id="thought-details-container"
                ),
                id="thought-container"
            ),
            id="thoughts"
        )
    
    def on_mount(self):
        """Load data when screen is mounted"""
        self.load_branch("main")
    
    def on_button_pressed(self, event: events.Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        try:
            if button_id == "new-thought":
                self.show_new_thought_dialog()
            elif button_id == "branch-thought":
                if self.current_thought:
                    self.show_branch_thought_dialog(self.current_thought)
            elif button_id == "merge-thoughts":
                self.show_merge_thoughts_dialog()
            elif button_id == "crystallize-thought":
                if self.current_thought:
                    self.crystallize_thought(self.current_thought.id)
            elif button_id == "load-branch":
                branch_name = self.query_one("#branch-input").value
                self.load_branch(branch_name)
            elif button_id == "edit-thought":
                if self.current_thought:
                    self.show_edit_thought_dialog(self.current_thought)
            elif button_id == "view-lineage":
                if self.current_thought:
                    self.show_thought_lineage(self.current_thought.id)
        except Exception as e:
            logger.error(f"Error handling button press: {e}", exc_info=True)
            self.show_error(f"Error: {str(e)}")
    
    def load_branch(self, branch_name: str):
        """Load thoughts from a specific branch"""
        try:
            self.current_branch = branch_name
            thoughts = self.thought_manager.get_thoughts_by_branch(branch_name)
            
            if thoughts:
                # Update thought list
                thought_list = "\n".join([
                    f"• {thought.title} ({thought.status.value})" 
                    for thought in thoughts
                ])
                self.query_one("#thought-list").update(thought_list)
            else:
                self.query_one("#thought-list").update(f"No thoughts in branch '{branch_name}'")
            
            # Clear current thought selection
            self.current_thought = None
            self.query_one("#thought-title").update("No thought selected")
            self.query_one("#thought-status").update("Status: None")
            self.query_one("#thought-content").value = ""
            self.query_one("#edit-thought").disabled = True
            self.query_one("#branch-thought").disabled = True
            self.query_one("#crystallize-thought").disabled = True
            self.query_one("#view-lineage").disabled = True
            
            logger.info(f"Loaded {len(thoughts)} thoughts from branch '{branch_name}'")
        except Exception as e:
            logger.error(f"Error loading branch '{branch_name}': {e}", exc_info=True)
            self.show_error(f"Failed to load branch: {str(e)}")
    
    def show_new_thought_dialog(self):
        """Show dialog to create a new thought"""
        # This would be implemented with a modal dialog in a full implementation
        # For now, we'll just log that this would happen
        logger.info("New thought dialog would be shown here")
        # In a real implementation, this would create a new ThoughtNode and add it to the database
    
    def show_branch_thought_dialog(self, parent_thought: ThoughtNode):
        """Show dialog to create a branch from an existing thought"""
        logger.info(f"Branch thought dialog would be shown here for {parent_thought.id}")
    
    def show_merge_thoughts_dialog(self):
        """Show dialog to merge multiple thoughts"""
        logger.info("Merge thoughts dialog would be shown here")
    
    def show_edit_thought_dialog(self, thought: ThoughtNode):
        """Show dialog to edit a thought"""
        logger.info(f"Edit thought dialog would be shown here for {thought.id}")
    
    def show_thought_lineage(self, thought_id: str):
        """Show the lineage of a thought"""
        logger.info(f"Thought lineage would be shown here for {thought_id}")
    
    def crystallize_thought(self, thought_id: str):
        """Mark a thought as crystallized"""
        try:
            result = self.thought_manager.crystallize_thought(thought_id)
            if result:
                logger.info(f"Thought {thought_id} crystallized")
                # Reload the current branch to reflect changes
                self.load_branch(self.current_branch)
            else:
                logger.error(f"Failed to crystallize thought {thought_id}")
                self.show_error("Failed to crystallize thought")
        except Exception as e:
            logger.error(f"Error crystallizing thought: {e}", exc_info=True)
            self.show_error(f"Error: {str(e)}") 