"""
Tree visualization of linked work items.

This widget displays work items and their relationships in an
interactive tree format, with features for expansion, navigation,
and styling based on item properties.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union, cast

from rich.style import Style
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Label, Select, Static, Tree, Input
from textual.widgets.tree import TreeNode

from ...models import ItemStatus, ItemType, Priority, WorkItem, LinkType
from ..workers import LinkWorker, ItemFetchWorker


class LinkTree(Tree[Dict[str, Any]]):
    """Tree visualization of linked work items."""
    
    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("right", "expand_node", "Expand", show=False),
        Binding("left", "collapse_node", "Collapse", show=False),
        Binding("enter", "select_node", "Select", show=False),
        Binding("f", "focus_node", "Focus on Node", show=False),
    ]
    
    DEFAULT_CSS = """
    LinkTree {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }
    
    .node-TASK {
        color: $text;
    }
    
    .node-LEARNING {
        color: $accent;
    }
    
    .node-RESEARCH {
        color: $warning;
    }
    
    .node-THOUGHT {
        color: $success;
    }
    
    .node-completed {
        text-style: strike;
        color: $text-muted;
    }
    
    .node-in-progress {
        text-style: bold;
    }
    
    .node-selected {
        background: $primary;
        color: $text;
    }
    
    .link-references {
        color: $primary;
    }
    
    .link-evolves-from {
        color: $success;
    }
    
    .link-inspired-by {
        color: $warning;
    }
    
    .link-parent-child {
        color: $accent;
    }
    
    #tree-controls {
        height: auto;
        padding: 1;
        background: $panel;
    }
    
    #root-selector {
        width: 40%;
    }
    
    #depth-input {
        width: 10;
        margin-right: 1;
    }
    
    #depth-label {
        width: auto;
        margin-right: 1;
        content-align: center middle;
    }
    
    #tree-loading {
        background: $surface;
        color: $text;
        text-align: center;
        padding: 1;
    }
    """
    
    class NodeSelected(Message):
        """Message sent when a node is selected."""
        def __init__(self, item_id: str, item_data: Dict[str, Any]) -> None:
            self.item_id = item_id
            self.item_data = item_data
            super().__init__()
    
    class NodeFocusRequested(Message):
        """Message sent when focusing on a node is requested."""
        def __init__(self, item_id: str) -> None:
            self.item_id = item_id
            super().__init__()

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the link tree widget."""
        super().__init__("Item Relationships", data={"id": "root"}, *args, **kwargs)
        self.root_id: Optional[str] = None
        self.max_depth = 3
        self.current_depth = 0
        self.loading = False
        self.nodes_by_id: Dict[str, TreeNode] = {}
        self.expanded_nodes: Set[str] = set()
        # Color mapping for relationship types
        self.link_colors = {
            "references": "link-references",
            "evolves-from": "link-evolves-from",
            "inspired-by": "link-inspired-by",
            "parent-child": "link-parent-child",
        }

    def load_tree(self, root_id: Optional[str] = None, max_depth: int = 3) -> None:
        """Load the tree with the specified root item and depth.
        
        Args:
            root_id: ID of the root item (None for all roots)
            max_depth: Maximum depth to traverse
        """
        self.root_id = root_id
        self.max_depth = max_depth
        self.current_depth = 0
        self.loading = True
        self.nodes_by_id = {}
        self.expanded_nodes = set()
        
        # Clear the tree
        self.clear()
        self.root.label = "Loading..."
        self.root.data = {"id": "root"}
        
        # Start the worker to fetch items
        worker = ItemFetchWorker()
        worker.start(callback=self._on_items_loaded)
    
    def _on_items_loaded(self, result: Dict[str, Any]) -> None:
        """Handle the result of the item fetch worker."""
        if not result.get("success", False):
            self.root.label = f"Error: {result.get('message', 'Failed to load items')}"
            self.loading = False
            return
        
        items = result.get("items", [])
        if not items:
            self.root.label = "No items found"
            self.loading = False
            return
        
        # Convert items to a dictionary for easier access
        items_dict = {item["id"]: item for item in items}
        
        # Start link worker to fetch all links
        if self.root_id:
            # Just get links for the root item
            worker = LinkWorker()
            worker.start(
                operation="get",
                source_id=self.root_id,
                callback=lambda res: self._on_links_loaded(res, items_dict)
            )
        else:
            # Get links for all items (one by one to avoid overloading)
            self._fetch_all_links(list(items_dict.keys()), items_dict)
    
    def _fetch_all_links(self, item_ids: List[str], items_dict: Dict[str, Dict[str, Any]], index: int = 0, links_dict: Dict[str, Dict[str, List[Dict[str, Any]]]] = None) -> None:
        """Fetch links for all items one by one.
        
        Args:
            item_ids: List of item IDs to fetch links for
            items_dict: Dictionary of items by ID
            index: Current index in the item_ids list
            links_dict: Dictionary to store link results
        """
        if links_dict is None:
            links_dict = {}
        
        if index >= len(item_ids):
            # All links fetched, build the tree
            self._build_tree_from_links(items_dict, links_dict)
            return
        
        # Update loading message
        self.root.label = f"Loading links... ({index+1}/{len(item_ids)})"
        
        # Fetch links for the current item
        worker = LinkWorker()
        worker.start(
            operation="get",
            source_id=item_ids[index],
            callback=lambda res: self._on_single_item_links_loaded(
                res, items_dict, item_ids, index, links_dict
            )
        )
    
    def _on_single_item_links_loaded(
        self, 
        result: Dict[str, Any], 
        items_dict: Dict[str, Dict[str, Any]], 
        item_ids: List[str], 
        index: int, 
        links_dict: Dict[str, Dict[str, List[Dict[str, Any]]]]
    ) -> None:
        """Handle the result of a single item link fetch."""
        if result.get("success", False):
            source_id = result.get("source_id")
            links = result.get("links", {"outgoing": [], "incoming": []})
            links_dict[source_id] = links
        
        # Continue with the next item
        self._fetch_all_links(item_ids, items_dict, index + 1, links_dict)
    
    def _on_links_loaded(self, result: Dict[str, Any], items_dict: Dict[str, Dict[str, Any]]) -> None:
        """Handle the result of the link fetch worker."""
        if not result.get("success", False):
            self.root.label = f"Error: {result.get('message', 'Failed to load links')}"
            self.loading = False
            return
        
        source_id = result.get("source_id")
        links = result.get("links", {"outgoing": [], "incoming": []})
        
        # Build a dictionary of item links
        links_dict = {source_id: links}
        
        # Build the tree from the links
        self._build_tree_from_links(items_dict, links_dict)
    
    def _build_tree_from_links(self, items_dict: Dict[str, Dict[str, Any]], links_dict: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> None:
        """Build the tree from the fetched items and links.
        
        Args:
            items_dict: Dictionary of items by ID
            links_dict: Dictionary of links by item ID
        """
        self.loading = False
        
        # Clear the tree
        self.clear()
        
        if self.root_id:
            # Start with a specific root
            if self.root_id not in items_dict:
                self.root.label = f"Root item not found: {self.root_id}"
                return
            
            root_item = items_dict[self.root_id]
            self.root.label = self._format_item_label(root_item)
            self.root.data = root_item
            self.nodes_by_id[self.root_id] = self.root
            
            # Add children
            self._add_children(self.root, root_item["id"], items_dict, links_dict, 1)
        else:
            # Find items without incoming links to use as roots
            root_items = []
            for item_id, links in links_dict.items():
                if not links["incoming"] and item_id in items_dict:
                    root_items.append(items_dict[item_id])
            
            # If no roots found, use first few items
            if not root_items and items_dict:
                root_items = list(items_dict.values())[:5]
            
            if not root_items:
                self.root.label = "No items to display"
                return
            
            # Set root label
            self.root.label = f"Item Relationships ({len(root_items)} roots)"
            
            # Add each root as a child of the main root
            for item in root_items:
                node = self.root.add(
                    self._format_item_label(item), 
                    data=item
                )
                self.nodes_by_id[item["id"]] = node
                
                # Add children to this node
                self._add_children(node, item["id"], items_dict, links_dict, 1)
    
    def _add_children(
        self, 
        parent_node: TreeNode,
        parent_id: str, 
        items_dict: Dict[str, Dict[str, Any]], 
        links_dict: Dict[str, Dict[str, List[Dict[str, Any]]]],
        depth: int
    ) -> None:
        """Add child nodes to a parent node based on links.
        
        Args:
            parent_node: Parent tree node
            parent_id: ID of the parent item
            items_dict: Dictionary of items by ID
            links_dict: Dictionary of links by item ID
            depth: Current depth in the tree
        """
        # Stop if we've reached the maximum depth
        if depth > self.max_depth:
            return
        
        # Get links for this item
        if parent_id not in links_dict:
            return
        
        outgoing_links = links_dict[parent_id]["outgoing"]
        
        # Group links by link type
        links_by_type = {}
        for link in outgoing_links:
            link_type = link["link_type"]
            if link_type not in links_by_type:
                links_by_type[link_type] = []
            links_by_type[link_type].append(link)
        
        # Add child nodes grouped by link type
        for link_type, links in links_by_type.items():
            # Create a group node for this link type
            link_type_display = link_type.replace("-", " ").title()
            link_type_class = self.link_colors.get(link_type, "")
            
            # Only add the group if it has children
            if links:
                group_node = parent_node.add(
                    f"{link_type_display} ({len(links)})",
                    data={"type": "group", "link_type": link_type},
                    classes=link_type_class
                )
                
                # Add child nodes for this link type
                for link in links:
                    target_id = link["target_id"]
                    if target_id in items_dict:
                        target_item = items_dict[target_id]
                        child_node = group_node.add(
                            self._format_item_label(target_item),
                            data=target_item,
                            classes=self._get_item_classes(target_item)
                        )
                        self.nodes_by_id[target_id] = child_node
                        
                        # Add indicator if this has children but we're not showing them
                        if depth + 1 <= self.max_depth:
                            if target_id in links_dict and links_dict[target_id]["outgoing"]:
                                # This will be expanded on demand
                                child_node.expand_icon = "➕"
                                child_node.collapsed_icon = "➕"
                                child_node.expanded_icon = "➖"
    
    def _format_item_label(self, item: Dict[str, Any]) -> Text:
        """Format the label for an item node.
        
        Args:
            item: Item data dictionary
            
        Returns:
            Rich Text object with formatting
        """
        item_id = item["id"]
        title = item["title"]
        item_type = item["item_type"]
        
        # Create the label with ID and title
        label = Text()
        label.append(f"{item_id} - ", Style(color="cyan", dim=True))
        label.append(title)
        label.append(f" ({item_type})", Style(dim=True))
        
        return label
    
    def _get_item_classes(self, item: Dict[str, Any]) -> str:
        """Get CSS classes for an item based on its properties.
        
        Args:
            item: Item data dictionary
            
        Returns:
            Space-separated string of CSS classes
        """
        classes = []
        
        # Add class based on item type
        item_type = item["item_type"]
        if item_type:
            type_class = f"node-{ItemType(item_type).name}"
            classes.append(type_class)
        
        # Add class based on status
        status = item["status"]
        if status:
            status_name = ItemStatus(status).name.lower().replace("_", "-")
            status_class = f"node-{status_name}"
            classes.append(status_class)
        
        return " ".join(classes)
    
    def action_expand_node(self) -> None:
        """Expand the selected node and load its children."""
        if not self.cursor_node:
            return
        
        # Only expand if the node has data
        node_data = self.cursor_node.data
        if not node_data or not isinstance(node_data, dict) or "id" not in node_data:
            return
        
        # Expand the node
        item_id = node_data["id"]
        if not self.cursor_node.is_expanded:
            self.cursor_node.expand()
            self.expanded_nodes.add(item_id)
            
            # Check if we need to load children
            # This would be done in a real implementation
            # by checking if the node has any children yet
            has_children = len(self.cursor_node.children) > 0
            if not has_children:
                # Load children for this node
                self._load_node_children(item_id, self.cursor_node)
    
    def _load_node_children(self, item_id: str, node: TreeNode) -> None:
        """Load children for a node on demand.
        
        Args:
            item_id: ID of the item to load children for
            node: Tree node to add children to
        """
        # Show loading indicator
        loading_node = node.add("Loading...", data={"type": "loading"})
        
        # Start worker to fetch links
        worker = LinkWorker()
        worker.start(
            operation="get",
            source_id=item_id,
            callback=lambda res: self._on_node_links_loaded(res, node, loading_node)
        )
    
    def _on_node_links_loaded(self, result: Dict[str, Any], node: TreeNode, loading_node: TreeNode) -> None:
        """Handle the result of the link fetch for a node.
        
        Args:
            result: Worker result
            node: Parent node
            loading_node: Loading indicator node
        """
        # Remove loading indicator
        if loading_node in node.children:
            node.remove_child(loading_node)
        
        if not result.get("success", False):
            node.add(f"Error: {result.get('message', 'Failed to load links')}")
            return
        
        source_id = result.get("source_id")
        links = result.get("links", {"outgoing": [], "incoming": []})
        
        # We need the target items now
        target_ids = [link["target_id"] for link in links["outgoing"]]
        if not target_ids:
            return
        
        # Fetch the target items
        worker = ItemFetchWorker()
        worker.start(
            filters={"ids": target_ids},
            callback=lambda res: self._on_node_items_loaded(res, node, source_id, links)
        )
    
    def _on_node_items_loaded(
        self, 
        result: Dict[str, Any], 
        node: TreeNode, 
        source_id: str,
        links: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Handle the result of the item fetch for a node's children.
        
        Args:
            result: Worker result
            node: Parent node
            source_id: ID of the source item
            links: Links dictionary for the source item
        """
        if not result.get("success", False):
            node.add(f"Error: {result.get('message', 'Failed to load items')}")
            return
        
        items = result.get("items", [])
        if not items:
            return
        
        # Convert items to a dictionary for easier access
        items_dict = {item["id"]: item for item in items}
        
        # Group links by link type
        links_by_type = {}
        for link in links["outgoing"]:
            link_type = link["link_type"]
            if link_type not in links_by_type:
                links_by_type[link_type] = []
            links_by_type[link_type].append(link)
        
        # Add child nodes grouped by link type
        for link_type, type_links in links_by_type.items():
            # Create a group node for this link type
            link_type_display = link_type.replace("-", " ").title()
            link_type_class = self.link_colors.get(link_type, "")
            
            # Only add the group if it has children
            if type_links:
                group_node = node.add(
                    f"{link_type_display} ({len(type_links)})",
                    data={"type": "group", "link_type": link_type},
                    classes=link_type_class
                )
                
                # Add child nodes for this link type
                for link in type_links:
                    target_id = link["target_id"]
                    if target_id in items_dict:
                        target_item = items_dict[target_id]
                        child_node = group_node.add(
                            self._format_item_label(target_item),
                            data=target_item,
                            classes=self._get_item_classes(target_item)
                        )
                        self.nodes_by_id[target_id] = child_node
    
    def action_collapse_node(self) -> None:
        """Collapse the selected node."""
        if not self.cursor_node or self.cursor_node is self.root:
            return
        
        # Collapse the node
        if self.cursor_node.is_expanded:
            self.cursor_node.collapse()
            
            # Remove from expanded nodes set
            node_data = self.cursor_node.data
            if node_data and isinstance(node_data, dict) and "id" in node_data:
                item_id = node_data["id"]
                if item_id in self.expanded_nodes:
                    self.expanded_nodes.remove(item_id)
    
    def action_select_node(self) -> None:
        """Select the current node and emit an event."""
        if not self.cursor_node:
            return
        
        # Only select if the node has data
        node_data = self.cursor_node.data
        if not node_data or not isinstance(node_data, dict) or "id" not in node_data:
            return
        
        # Emit selection event
        self.post_message(self.NodeSelected(node_data["id"], node_data))
    
    def action_focus_node(self) -> None:
        """Focus on the current node (make it the root)."""
        if not self.cursor_node:
            return
        
        # Only focus if the node has data
        node_data = self.cursor_node.data
        if not node_data or not isinstance(node_data, dict) or "id" not in node_data:
            return
        
        # Emit focus event
        self.post_message(self.NodeFocusRequested(node_data["id"]))
    
    def refresh_tree(self) -> None:
        """Refresh the tree with current settings."""
        self.load_tree(self.root_id, self.max_depth)


class LinkTreeControls(Container):
    """Control panel for the link tree."""
    
    DEFAULT_CSS = """
    LinkTreeControls {
        height: auto;
        padding: 1;
        background: $panel;
        layout: horizontal;
    }
    
    #control-label {
        width: 1fr;
        content-align: center middle;
    }
    
    #root-selector {
        width: 40%;
    }
    
    #depth-input {
        width: 10;
        margin-right: 1;
    }
    
    #depth-label {
        width: auto;
        margin-right: 1;
        content-align: center middle;
    }
    
    #refresh-button {
        margin-left: 1;
    }
    """
    
    class DepthChanged(Message):
        """Message sent when the depth input is changed."""
        def __init__(self, depth: int) -> None:
            self.depth = depth
            super().__init__()
    
    class RootChanged(Message):
        """Message sent when the root item is changed."""
        def __init__(self, root_id: Optional[str]) -> None:
            self.root_id = root_id
            super().__init__()
    
    class RefreshRequested(Message):
        """Message sent when a refresh is requested."""
        def __init__(self) -> None:
            super().__init__()
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._items = []
    
    def compose(self) -> ComposeResult:
        """Compose the control panel."""
        yield Static("Tree Controls", id="control-label")
        
        # Root selector
        yield Select(
            [(None, "All Items")], 
            id="root-selector", 
            prompt="Root Item"
        )
        
        # Depth input with label
        yield Static("Depth:", id="depth-label")
        yield Input(value="3", id="depth-input", type="number")
        
        # Refresh button
        yield Button("Refresh", id="refresh-button")
    
    def update_items(self, items: List[Dict[str, Any]]) -> None:
        """Update the list of items for the root selector.
        
        Args:
            items: List of item dictionaries
        """
        self._items = items
        
        # Create options for the select
        options = [(None, "All Items")]
        for item in items:
            options.append((item["id"], f"{item['id']} - {item['title']}"))
        
        # Update the select
        root_selector = self.query_one("#root-selector", Select)
        root_selector.set_options(options)
    
    @on(Select.Changed, "#root-selector")
    def handle_root_changed(self, event: Select.Changed) -> None:
        """Handle the root selector change."""
        root_id = event.value
        self.post_message(self.RootChanged(root_id))
    
    @on(Input.Changed, "#depth-input")
    def handle_depth_changed(self, event: Input.Changed) -> None:
        """Handle the depth input change."""
        try:
            # Get depth value and ensure it's within range
            depth = int(event.value)
            if depth < 1:
                depth = 1
                event.input.value = "1"
            elif depth > 10:
                depth = 10
                event.input.value = "10"
            
            self.post_message(self.DepthChanged(depth))
        except ValueError:
            # Handle invalid input by resetting to default
            event.input.value = "3"
            self.post_message(self.DepthChanged(3))
    
    @on(Button.Pressed, "#refresh-button")
    def handle_refresh(self, event: Button.Pressed) -> None:
        """Handle the refresh button press."""
        self.post_message(self.RefreshRequested())
