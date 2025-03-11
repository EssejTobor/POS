"""
List component for viewing and filtering thoughts.
"""
from typing import List, Dict, Optional, Callable
import logging
from textual.widgets import Static, Button, Input, Label
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.app import ComposeResult
from textual import events
from rich.text import Text
from textual.message import Message

from ..models import ThoughtNode, ThoughtStatus
from .thought_widgets import ThoughtNodeWidget, ThoughtSelected

logger = logging.getLogger(__name__)

class FilterChanged(Message):
    """Event fired when a filter is changed"""
    def __init__(self, filter_type: str, value: str):
        self.filter_type = filter_type
        self.value = value
        super().__init__()
        
class ThoughtFilterBar(Container):
    """Filter bar for thoughts"""
    
    def compose(self) -> ComposeResult:
        # Status filters
        with Horizontal(classes="filter-group"):
            yield Label("Status:", classes="filter-label")
            yield Button("All", id="filter-status-all", classes="filter-button selected")
            for status in ThoughtStatus:
                yield Button(status.value.title(), 
                             id=f"filter-status-{status.value}", 
                             classes="filter-button")
                
        # Branch filter
        with Horizontal(classes="filter-group"):
            yield Label("Branch:", classes="filter-label")
            yield Input(placeholder="Filter by branch", id="filter-branch")
            
        # Tag filter
        with Horizontal(classes="filter-group"):
            yield Label("Tag:", classes="filter-label")
            yield Input(placeholder="Filter by tag", id="filter-tag")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for filters"""
        button_id = event.button.id
        if button_id and button_id.startswith("filter-status-"):
            # Deselect all status filter buttons
            for button in self.query(".filter-button.selected"):
                button.remove_class("selected")
                
            # Select the clicked button
            event.button.add_class("selected")
            
            # Extract the status value
            status = button_id.replace("filter-status-", "")
            self.post_message(FilterChanged("status", status))
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for filters"""
        input_id = event.input.id
        if input_id == "filter-branch":
            self.post_message(FilterChanged("branch", event.value))
        elif input_id == "filter-tag":
            self.post_message(FilterChanged("tag", event.value))

class ThoughtList(Container):
    """List of thought nodes with filtering"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thoughts: List[ThoughtNode] = []
        self.filters = {
            "status": "all",
            "branch": "",
            "tag": ""
        }
        
    def compose(self) -> ComposeResult:
        # Filter bar
        yield ThoughtFilterBar(id="thought-filters")
        
        # List of thoughts in a scrollable container
        yield Label("Thoughts:", classes="section-title")
        yield VerticalScroll(
            Vertical(id="thought-list-container"),
            id="thought-list-scroll"
        )
        
        # Action buttons
        with Horizontal(classes="action-buttons"):
            yield Button("Add Thought", id="add-thought")
            yield Button("Refresh", id="refresh-thoughts")
    
    def update_thoughts(self, thoughts: List[ThoughtNode]) -> None:
        """Update the list of thoughts"""
        self.thoughts = thoughts
        self._apply_filters_and_refresh()
    
    def _apply_filters_and_refresh(self) -> None:
        """Apply current filters and refresh the display"""
        filtered_thoughts = self.thoughts
        
        # Apply status filter
        if self.filters["status"] != "all":
            filtered_thoughts = [
                t for t in filtered_thoughts 
                if t.status.value == self.filters["status"]
            ]
        
        # Apply branch filter
        if self.filters["branch"]:
            branch_filter = self.filters["branch"].lower()
            filtered_thoughts = [
                t for t in filtered_thoughts 
                if branch_filter in t.branch_name.lower()
            ]
        
        # Apply tag filter
        if self.filters["tag"]:
            tag_filter = self.filters["tag"].lower()
            filtered_thoughts = [
                t for t in filtered_thoughts 
                if any(tag_filter in tag.lower() for tag in (t.tags or []))
            ]
        
        # Clear existing list
        container = self.query_one("#thought-list-container")
        container.remove_children()
        
        # Add filtered thoughts
        for thought in filtered_thoughts:
            container.mount(ThoughtNodeWidget(
                thought_id=thought.id,
                title=thought.title,
                status=thought.status.value,
                tags=thought.tags
            ))
            
        # Show empty state if needed
        if not filtered_thoughts:
            container.mount(Static("No thoughts match your filters.", classes="empty-state"))
    
    def on_filter_changed(self, event: FilterChanged) -> None:
        """Handle filter change events"""
        logger.debug(f"Filter changed: {event.filter_type} = {event.value}")
        self.filters[event.filter_type] = event.value
        self._apply_filters_and_refresh()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "add-thought":
            logger.debug("Add thought button pressed")
            self.post_message(AddThought())
        elif event.button.id == "refresh-thoughts":
            logger.debug("Refresh thoughts button pressed")
            self.post_message(RefreshRequested())
    
    def on_thought_selected(self, event: ThoughtSelected) -> None:
        """Handle thought selection from the list"""
        # Forward the event up
        self.post_message(event)
    
    class AddThought(Message):
        """Event fired when add thought button is pressed"""
        
    class RefreshRequested(Message):
        """Event fired when refresh button is pressed""" 