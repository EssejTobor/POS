"""
UI components for the Thought Evolution Tracker.
"""
from textual.widgets import Static, Input, TextArea, Button, Label
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.app import ComposeResult
from textual import events
from rich.text import Text
from rich.syntax import Syntax
import logging

from ..models import ThoughtStatus, BranchType, ThoughtNode

logger = logging.getLogger(__name__)

class ThoughtSelected(events.Message):
    """Event fired when a thought is selected"""
    def __init__(self, thought_id: str):
        self.thought_id = thought_id
        super().__init__()

class ThoughtNodeWidget(Static):
    """Widget representing a thought node in visualizations"""
    
    def __init__(self, thought_id: str, title: str, status: str, tags=None, **kwargs):
        super().__init__(**kwargs)
        self.thought_id = thought_id
        self.title = title
        self.status = status
        self.tags = tags or []
        
    def compose(self) -> ComposeResult:
        # Status indicator with color
        status_color = {
            "draft": "yellow",
            "evolving": "blue",
            "crystallized": "green"
        }.get(self.status, "white")
        
        # Format tags
        tag_text = " ".join([f"#{tag}" for tag in self.tags]) if self.tags else ""
        
        # Create styled text
        node_text = Text()
        node_text.append("● ", style=status_color)
        node_text.append(self.title, style="bold")
        
        if tag_text:
            node_text.append(" ")
            node_text.append(tag_text, style="italic dim")
        
        yield Static(node_text, id=f"thought-{self.thought_id}")
        
    def on_click(self) -> None:
        """Handle click to select this thought"""
        logger.debug(f"Thought selected: {self.thought_id}")
        self.app.post_message(ThoughtSelected(self.thought_id))

class ThoughtForm(Container):
    """Form for adding or editing thoughts"""
    
    def __init__(self, thought=None, **kwargs):
        super().__init__(**kwargs)
        self.thought = thought
        
    def compose(self) -> ComposeResult:
        # Title for the form
        if self.thought:
            yield Label("Edit Thought", classes="form-title")
        else:
            yield Label("New Thought", classes="form-title")
        
        # Fields
        yield Label("Title:")
        yield Input(
            value=self.thought.title if self.thought else "", 
            id="thought-title",
            placeholder="Enter thought title"
        )
        
        yield Label("Content:")
        yield TextArea(
            text=self.thought.content if self.thought else "",
            id="thought-content",
            placeholder="Enter thought content"
        )
        
        yield Label("Branch Name:")
        yield Input(
            value=self.thought.branch_name if self.thought else "main",
            id="thought-branch",
            placeholder="main"
        )
        
        yield Label("Tags (comma separated):")
        yield Input(
            value=",".join(self.thought.tags) if self.thought and self.thought.tags else "",
            id="thought-tags",
            placeholder="tag1, tag2, tag3"
        )
        
        # Status selection
        yield Label("Status:")
        with Horizontal(classes="status-buttons"):
            for status in ThoughtStatus:
                is_selected = self.thought and self.thought.status == status
                yield Button(
                    status.value.title(), 
                    id=f"status-{status.value}",
                    classes="selected" if is_selected else ""
                )
        
        # Buttons
        with Horizontal(classes="button-row"):
            yield Button("Cancel", id="cancel-thought")
            if self.thought:
                yield Button("Update", id="update-thought")
            else:
                yield Button("Create", id="create-thought")

class ThoughtBranchForm(Container):
    """Form for creating a branch from an existing thought"""
    
    def __init__(self, parent_thought: ThoughtNode, **kwargs):
        super().__init__(**kwargs)
        self.parent_thought = parent_thought
        
    def compose(self) -> ComposeResult:
        yield Label(f"Branch from: {self.parent_thought.title}", classes="form-title")
        
        # Fields
        yield Label("Branch Title:")
        yield Input(
            value="", 
            id="branch-title",
            placeholder="Enter branch title"
        )
        
        yield Label("Content:")
        yield TextArea(
            text=self.parent_thought.content,
            id="branch-content",
            placeholder="Enter branch content"
        )
        
        yield Label("Branch Name:")
        yield Input(
            value=f"{self.parent_thought.branch_name}-branch",
            id="branch-name",
            placeholder="branch-name"
        )
        
        # Branch type selection
        yield Label("Branch Type:")
        with Horizontal(classes="branch-type-buttons"):
            for branch_type in BranchType:
                yield Button(
                    branch_type.value.title(), 
                    id=f"branch-type-{branch_type.value}"
                )
        
        # Inherit tags checkbox
        yield Container(
            Label("Inherit tags from parent:"),
            Switch(value=True, id="inherit-tags"),
            classes="form-option"
        )
        
        # Buttons
        with Horizontal(classes="button-row"):
            yield Button("Cancel", id="cancel-branch")
            yield Button("Create Branch", id="create-branch")

class ThoughtVisualizer(Container):
    """Widget for visualizing thought trees"""
    
    def __init__(self, ascii_tree="", **kwargs):
        super().__init__(**kwargs)
        self.ascii_tree = ascii_tree
        
    def compose(self) -> ComposeResult:
        yield Label("Thought Evolution", classes="section-title")
        
        if self.ascii_tree:
            yield Static(self.ascii_tree, id="ascii-tree")
        else:
            yield Static("Select a thought to view its evolution", 
                         id="tree-placeholder")
            
        yield Button("Expand Tree", id="expand-tree")

class ThoughtSearchForm(Container):
    """Search interface for thoughts"""
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Input(placeholder="Search thoughts...", id="thought-search"),
            Button("Search", id="search-button"),
            classes="search-row"
        )
        
        yield Label("Search Results:", classes="section-title")
        yield VerticalScroll(
            Static("Enter search terms above", id="search-results"),
            id="results-container"
        )

class Switch(Static):
    """A simple toggle switch widget"""
    
    def __init__(self, value: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        
    def compose(self) -> ComposeResult:
        text = "[ON]" if self.value else "[OFF]"
        style = "bold green" if self.value else "bold red"
        yield Static(Text(text, style=style), id=f"{self.id}-text")
        
    def on_click(self) -> None:
        """Toggle the switch when clicked"""
        self.value = not self.value
        text = "[ON]" if self.value else "[OFF]"
        style = "bold green" if self.value else "bold red"
        
        # Update the switch text
        switch_text = self.query_one(f"#{self.id}-text")
        switch_text.update(Text(text, style=style))
        
        # Post a changed event
        self.post_message(Switch.Changed(self.value))
        
    class Changed(events.Message):
        """Event fired when the switch value changes"""
        def __init__(self, value: bool):
            self.value = value
            super().__init__() 