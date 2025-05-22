"""
Screen for visualizing item links in a tree structure.

This screen displays work items and their relationships in an
interactive tree visualization with controls for filtering and
navigation.
"""

from typing import Dict, List, Optional, Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

from ...storage import WorkSystem
from ..workers import ItemFetchWorker, LinkWorker
from ..widgets import LinkTree
from ..widgets.link_tree import LinkTreeControls


class LinkTreeScreen(Screen):
    """Screen for visualizing item links in a tree structure."""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.root_id: Optional[str] = None
        self.max_depth: int = 3
        self.loading: bool = False
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        
        with Vertical(id="link-tree-container"):
            # Controls for the tree
            yield LinkTreeControls(id="tree-controls")
            
            # Status message
            yield Static("Select a root item or use all items", id="tree-status")
            
            # The tree itself
            yield LinkTree(id="link-tree")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        # Load initial items for the controls
        worker = ItemFetchWorker()
        worker.start(callback=self._on_items_loaded)
        
        # Set up the tree with default settings
        self._refresh_tree()
    
    def _on_items_loaded(self, result: Dict[str, Any]) -> None:
        """Handle the result of the item fetch worker."""
        if not result.get("success", False):
            self.query_one("#tree-status", Static).update(
                f"Error: {result.get('message', 'Failed to load items')}"
            )
            return
        
        items = result.get("items", [])
        if not items:
            self.query_one("#tree-status", Static).update("No items found")
            return
        
        # Update the controls with the loaded items
        controls = self.query_one("#tree-controls", LinkTreeControls)
        controls.update_items(items)
    
    def _refresh_tree(self) -> None:
        """Refresh the tree with current settings."""
        tree = self.query_one("#link-tree", LinkTree)
        tree.load_tree(self.root_id, self.max_depth)
        
        # Update status message
        status = self.query_one("#tree-status", Static)
        if self.root_id:
            status.update(f"Showing links for item: {self.root_id} (depth: {self.max_depth})")
        else:
            status.update(f"Showing links for all root items (depth: {self.max_depth})")
    
    @on(LinkTreeControls.RootChanged)
    def handle_root_changed(self, event: LinkTreeControls.RootChanged) -> None:
        """Handle root item selection."""
        self.root_id = event.root_id
        self._refresh_tree()
    
    @on(LinkTreeControls.DepthChanged)
    def handle_depth_changed(self, event: LinkTreeControls.DepthChanged) -> None:
        """Handle depth slider change."""
        self.max_depth = event.depth
        self._refresh_tree()
    
    @on(LinkTreeControls.RefreshRequested)
    def handle_refresh(self, event: LinkTreeControls.RefreshRequested) -> None:
        """Handle refresh button press."""
        self._refresh_tree()
    
    @on(LinkTree.NodeSelected)
    def handle_node_selected(self, event: LinkTree.NodeSelected) -> None:
        """Handle node selection in the tree."""
        # Display information about the selected item
        status = self.query_one("#tree-status", Static)
        status.update(f"Selected item: {event.item_id}")
    
    @on(LinkTree.NodeFocusRequested)
    def handle_node_focus(self, event: LinkTree.NodeFocusRequested) -> None:
        """Handle focusing on a node (making it the root)."""
        self.root_id = event.item_id
        self._refresh_tree()
