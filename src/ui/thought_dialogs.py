"""
Dialog components for thought management.
"""
from typing import Optional, List, Dict, Any, Callable
import logging
from textual.widgets import Static, Button, Label
from textual.containers import Container, Horizontal, Vertical
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual import events
from rich.syntax import Syntax
from rich.text import Text

from ..models import ThoughtNode, ThoughtStatus, BranchType
from .thought_widgets import ThoughtForm, ThoughtBranchForm, ThoughtVisualizer

logger = logging.getLogger(__name__)

class DialogResult(events.Message):
    """Base class for dialog result messages"""
    def __init__(self, dialog_id: str, result: Dict[str, Any], action: str):
        self.dialog_id = dialog_id
        self.result = result
        self.action = action
        super().__init__()

class ThoughtDialog(ModalScreen):
    """Base class for thought-related dialogs"""
    
    BINDINGS = [("escape", "dismiss", "Dismiss")]
    
    def __init__(self, dialog_id: str, **kwargs):
        super().__init__(**kwargs)
        self.dialog_id = dialog_id
        
    def compose(self) -> ComposeResult:
        with Container(id="dialog-container"):
            yield self._compose_dialog_content()
            
    def _compose_dialog_content(self) -> ComposeResult:
        """Subclasses should override this to provide dialog content"""
        yield Label("Dialog content goes here")
        
    def action_dismiss(self) -> None:
        """Dismiss the dialog without action"""
        self.post_message(DialogResult(self.dialog_id, {}, "dismiss"))
        self.app.pop_screen()
        
    def _submit_dialog(self, result: Dict[str, Any], action: str) -> None:
        """Submit the dialog with a result and action"""
        self.post_message(DialogResult(self.dialog_id, result, action))
        self.app.pop_screen()

class AddThoughtDialog(ThoughtDialog):
    """Dialog for adding a new thought"""
    
    def _compose_dialog_content(self) -> ComposeResult:
        yield Container(
            ThoughtForm(id="add-thought-form"),
            id="dialog-content"
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the form"""
        button_id = event.button.id
        
        if button_id == "cancel-thought":
            self.action_dismiss()
        elif button_id == "create-thought":
            # Collect form data
            title = self.query_one("#thought-title").value
            content = self.query_one("#thought-content").text
            branch = self.query_one("#thought-branch").value
            tags_text = self.query_one("#thought-tags").value
            
            # Get selected status
            status_button = self.query(".selected")
            status = "draft"  # Default
            if status_button:
                status_id = status_button.id
                if status_id and status_id.startswith("status-"):
                    status = status_id.replace("status-", "")
            
            # Process tags (split by comma and strip)
            tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            
            # Submit form data
            self._submit_dialog({
                "title": title,
                "content": content,
                "branch_name": branch,
                "tags": tags,
                "status": status
            }, "create")

class EditThoughtDialog(ThoughtDialog):
    """Dialog for editing an existing thought"""
    
    def __init__(self, dialog_id: str, thought: ThoughtNode, **kwargs):
        super().__init__(dialog_id, **kwargs)
        self.thought = thought
        
    def _compose_dialog_content(self) -> ComposeResult:
        yield Container(
            ThoughtForm(thought=self.thought, id="edit-thought-form"),
            id="dialog-content"
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the form"""
        button_id = event.button.id
        
        if button_id == "cancel-thought":
            self.action_dismiss()
        elif button_id == "update-thought":
            # Collect form data
            title = self.query_one("#thought-title").value
            content = self.query_one("#thought-content").text
            branch = self.query_one("#thought-branch").value
            tags_text = self.query_one("#thought-tags").value
            
            # Get selected status
            status_button = self.query(".selected")
            status = self.thought.status.value  # Default to current
            if status_button:
                status_id = status_button.id
                if status_id and status_id.startswith("status-"):
                    status = status_id.replace("status-", "")
            
            # Process tags (split by comma and strip)
            tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
            
            # Submit form data
            self._submit_dialog({
                "id": self.thought.id,
                "title": title,
                "content": content,
                "branch_name": branch,
                "tags": tags,
                "status": status
            }, "update")

class BranchThoughtDialog(ThoughtDialog):
    """Dialog for creating a branch from an existing thought"""
    
    def __init__(self, dialog_id: str, parent_thought: ThoughtNode, **kwargs):
        super().__init__(dialog_id, **kwargs)
        self.parent_thought = parent_thought
        
    def _compose_dialog_content(self) -> ComposeResult:
        yield Container(
            ThoughtBranchForm(parent_thought=self.parent_thought, id="branch-thought-form"),
            id="dialog-content"
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the form"""
        button_id = event.button.id
        
        if button_id == "cancel-branch":
            self.action_dismiss()
        elif button_id == "create-branch":
            # Collect form data
            title = self.query_one("#branch-title").value
            content = self.query_one("#branch-content").text
            branch_name = self.query_one("#branch-name").value
            
            # Get selected branch type
            branch_type = "refinement"  # Default
            for bt in BranchType:
                bt_id = f"branch-type-{bt.value}"
                if self.query_one(f"#{bt_id}").has_class("selected"):
                    branch_type = bt.value
                    break
            
            # Check if inherit tags is enabled
            inherit_tags = self.query_one("#inherit-tags").value
            tags = self.parent_thought.tags.copy() if inherit_tags and self.parent_thought.tags else []
            
            # Submit form data
            self._submit_dialog({
                "parent_id": self.parent_thought.id,
                "title": title,
                "content": content,
                "branch_name": branch_name,
                "branch_type": branch_type,
                "tags": tags,
                "status": "draft"  # New branches start as draft
            }, "branch")

class VisualizeThoughtDialog(ThoughtDialog):
    """Dialog for visualizing a thought tree"""
    
    def __init__(self, dialog_id: str, ascii_tree: str, **kwargs):
        super().__init__(dialog_id, **kwargs)
        self.ascii_tree = ascii_tree
        
    def _compose_dialog_content(self) -> ComposeResult:
        yield Container(
            Label("Thought Evolution Tree", classes="dialog-title"),
            Static(self.ascii_tree, id="ascii-tree-full"),
            Button("Close", id="close-visualize"),
            id="dialog-content"
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "close-visualize":
            self.action_dismiss()

class ConfirmDeleteDialog(ThoughtDialog):
    """Dialog for confirming thought deletion"""
    
    def __init__(self, dialog_id: str, thought: ThoughtNode, **kwargs):
        super().__init__(dialog_id, **kwargs)
        self.thought = thought
        
    def _compose_dialog_content(self) -> ComposeResult:
        yield Container(
            Label(f"Delete Thought: {self.thought.title}", classes="dialog-title danger"),
            Static("Are you sure you want to delete this thought?"),
            Static("This action cannot be undone."),
            Horizontal(
                Button("Cancel", id="cancel-delete"),
                Button("Delete", id="confirm-delete", classes="danger"),
                classes="button-row"
            ),
            id="dialog-content"
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel-delete":
            self.action_dismiss()
        elif event.button.id == "confirm-delete":
            self._submit_dialog({
                "id": self.thought.id
            }, "delete")