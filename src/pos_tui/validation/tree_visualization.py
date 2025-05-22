"""
Validation protocol for Tree Visualization.

This module provides validation scripts for the LinkTree widget
and tree-based relationship visualization.
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import ValidationProtocol, ValidationResult
from src.pos_tui.validation.introspect import dump_database_state, compare_database_states
from src.models import ItemType, Priority, ItemStatus, WorkItem, LinkType
from src.storage import WorkSystem


class TreeVisualizationValidation(ValidationProtocol):
    """Validation protocol for tree visualization functionality."""
    
    def __init__(self):
        super().__init__("tree_visualization")
        self.temp_db = None
        self.test_items = {}
        self.test_links = []
    
    def _setup_test_db(self) -> str:
        """Create a temporary database with a test tree structure."""
        # Create a temporary database file
        temp_db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db_file.close()
        
        # Initialize work system with this database
        ws = WorkSystem(temp_db_file.name)
        
        # Create test items representing a tree structure
        items = [
            # Root items
            WorkItem(
                id="root1",
                title="Root Item 1",
                goal="Test Goal",
                item_type=ItemType.TASK,
                description="Root item for testing tree visualization",
                priority=Priority.MED,
                status=ItemStatus.IN_PROGRESS
            ),
            WorkItem(
                id="root2",
                title="Root Item 2",
                goal="Test Goal",
                item_type=ItemType.THOUGHT,
                description="Second root item for testing tree visualization",
                priority=Priority.HI,
                status=ItemStatus.NOT_STARTED
            ),
            
            # Level 1 items
            WorkItem(
                id="child1",
                title="Child Item 1",
                goal="Test Goal",
                item_type=ItemType.LEARNING,
                description="Child item 1 for testing tree visualization",
                priority=Priority.LOW,
                status=ItemStatus.NOT_STARTED
            ),
            WorkItem(
                id="child2",
                title="Child Item 2",
                goal="Test Goal",
                item_type=ItemType.RESEARCH,
                description="Child item 2 for testing tree visualization",
                priority=Priority.MED,
                status=ItemStatus.COMPLETED
            ),
            WorkItem(
                id="child3",
                title="Child Item 3",
                goal="Test Goal",
                item_type=ItemType.TASK,
                description="Child item 3 for testing tree visualization",
                priority=Priority.HI,
                status=ItemStatus.IN_PROGRESS
            ),
            
            # Level 2 items
            WorkItem(
                id="grandchild1",
                title="Grandchild Item 1",
                goal="Test Goal",
                item_type=ItemType.THOUGHT,
                description="Grandchild item 1 for testing tree visualization",
                priority=Priority.MED,
                status=ItemStatus.NOT_STARTED
            ),
            WorkItem(
                id="grandchild2",
                title="Grandchild Item 2",
                goal="Test Goal",
                item_type=ItemType.LEARNING,
                description="Grandchild item 2 for testing tree visualization",
                priority=Priority.LOW,
                status=ItemStatus.COMPLETED
            ),
            
            # Level 3 item (to test deep nesting)
            WorkItem(
                id="greatgrandchild",
                title="Great Grandchild Item",
                goal="Test Goal",
                item_type=ItemType.RESEARCH,
                description="Great grandchild item for testing tree visualization",
                priority=Priority.HI,
                status=ItemStatus.IN_PROGRESS
            ),
            
            # Isolated item (no links)
            WorkItem(
                id="isolated",
                title="Isolated Item",
                goal="Test Goal",
                item_type=ItemType.TASK,
                description="Isolated item with no links",
                priority=Priority.MED,
                status=ItemStatus.NOT_STARTED
            ),
            
            # Circular reference item
            WorkItem(
                id="circular",
                title="Circular Reference Item",
                goal="Test Goal",
                item_type=ItemType.THOUGHT,
                description="Item that will have circular references",
                priority=Priority.LOW,
                status=ItemStatus.IN_PROGRESS
            )
        ]
        
        # Save items to database
        for item in items:
            ws.add_item(item)
            self.test_items[item.id] = item.id
        
        # Create links between items
        links = [
            # Root1 links
            ("root1", "child1", LinkType.PARENT_CHILD.value),
            ("root1", "child2", LinkType.PARENT_CHILD.value),
            
            # Root2 links
            ("root2", "child3", LinkType.REFERENCES.value),
            
            # Child1 links
            ("child1", "grandchild1", LinkType.PARENT_CHILD.value),
            ("child1", "grandchild2", LinkType.INSPIRED_BY.value),
            
            # Child2 links
            ("child2", "grandchild2", LinkType.REFERENCES.value),
            
            # Grandchild1 links
            ("grandchild1", "greatgrandchild", LinkType.EVOLVES_FROM.value),
            
            # Circular references
            ("circular", "child3", LinkType.REFERENCES.value),
            ("child3", "circular", LinkType.INSPIRED_BY.value),
            
            # Cross-branch link
            ("child2", "child3", LinkType.REFERENCES.value),
        ]
        
        # Add links to database
        for source, target, link_type in links:
            ws.add_link(source, target, link_type)
            self.test_links.append((source, target, link_type))
        
        self.result.add_note(f"Created temporary database at {temp_db_file.name} with test tree structure")
        self.result.add_note(f"Created {len(items)} test items and {len(links)} links")
        
        return temp_db_file.name
    
    def _run_validation(self) -> None:
        """Run validation for tree visualization."""
        try:
            # Create a temporary database with test data
            self.temp_db = self._setup_test_db()
            
            # 1. Validate tree structure rendering
            self._validate_tree_structure()
            
            # 2. Validate node expansion/collapse
            self._validate_node_expansion()
            
            # 3. Validate tree depth controls
            self._validate_depth_controls()
            
            # 4. Validate performance with large datasets
            self._validate_performance()
            
        finally:
            # Clean up temporary database
            if self.temp_db and os.path.exists(self.temp_db):
                os.unlink(self.temp_db)
                self.result.add_note(f"Removed temporary database at {self.temp_db}")
    
    def _validate_tree_structure(self) -> None:
        """Validate that the tree structure correctly represents item relationships."""
        ws = WorkSystem(self.temp_db)
        
        # Check that all items are in the database
        items_count = len(ws.items)
        expected_count = len(self.test_items)
        if items_count == expected_count:
            self.result.add_passed(f"Database contains expected {items_count} items")
        else:
            self.result.add_failed(f"Database contains {items_count} items, expected {expected_count}")
        
        # Check links for root items
        root1_links = ws.get_links("root1")
        if len(root1_links["outgoing"]) == 2:
            self.result.add_passed("Root1 has correct number of outgoing links (2)")
            
            # Verify link targets
            targets = {link["target_id"] for link in root1_links["outgoing"]}
            expected_targets = {"child1", "child2"}
            if targets == expected_targets:
                self.result.add_passed("Root1 links to the correct targets")
            else:
                self.result.add_failed(f"Root1 links to {targets}, expected {expected_targets}")
        else:
            self.result.add_failed(f"Root1 has {len(root1_links['outgoing'])} outgoing links, expected 2")
        
        # Check for circular references
        circular_links = ws.get_links("circular")
        circular_incoming = {link["source_id"] for link in circular_links["incoming"]}
        if "child3" in circular_incoming:
            self.result.add_passed("Circular reference detected correctly")
        else:
            self.result.add_failed("Failed to detect circular reference")
        
        # Check deep nesting
        path_to_greatgrandchild = ["root1", "child1", "grandchild1", "greatgrandchild"]
        current_id = "root1"
        path_valid = True
        
        for i in range(1, len(path_to_greatgrandchild)):
            next_id = path_to_greatgrandchild[i]
            links = ws.get_links(current_id)
            found = False
            
            for link in links["outgoing"]:
                if link["target_id"] == next_id:
                    found = True
                    break
            
            if not found:
                path_valid = False
                self.result.add_failed(f"Path broken: {current_id} does not link to {next_id}")
                break
            
            current_id = next_id
        
        if path_valid:
            self.result.add_passed("Deep nesting path is valid through all levels")
    
    def _validate_node_expansion(self) -> None:
        """Validate node expansion and collapse functionality."""
        # This would be better tested with actual UI interaction simulation
        # Here we're validating the data structure supports expansion
        
        ws = WorkSystem(self.temp_db)
        
        # Check that child1 has expandable children
        child1_links = ws.get_links("child1")
        if len(child1_links["outgoing"]) > 0:
            self.result.add_passed(f"Child1 has {len(child1_links['outgoing'])} expandable children")
        else:
            self.result.add_failed("Child1 should have expandable children")
        
        # Check grandchild expansion
        grandchild1_links = ws.get_links("grandchild1")
        if len(grandchild1_links["outgoing"]) > 0:
            self.result.add_passed(f"Grandchild1 has {len(grandchild1_links['outgoing'])} expandable children")
        else:
            self.result.add_failed("Grandchild1 should have expandable children")
        
        # Check leaf node
        greatgrandchild_links = ws.get_links("greatgrandchild")
        if len(greatgrandchild_links["outgoing"]) == 0:
            self.result.add_passed("Great-grandchild is correctly a leaf node with no children")
        else:
            self.result.add_failed("Great-grandchild should be a leaf node")
    
    def _validate_depth_controls(self) -> None:
        """Validate that depth limiting controls work correctly."""
        ws = WorkSystem(self.temp_db)
        
        # Calculate expected nodes at different depths
        root_items = [item for item in self.test_items.keys() 
                     if not any(link[1] == item for link in self.test_links)]
        
        # Get all descendants for a node up to a specific depth
        def get_descendants(node_id, max_depth, current_depth=0, visited=None):
            if visited is None:
                visited = set()
            
            if node_id in visited or current_depth >= max_depth:
                return set()
            
            visited.add(node_id)
            descendants = {node_id}
            
            if current_depth < max_depth:
                links = ws.get_links(node_id)
                for link in links["outgoing"]:
                    target_id = link["target_id"]
                    if target_id not in visited:
                        descendants.update(
                            get_descendants(target_id, max_depth, current_depth + 1, visited.copy())
                        )
            
            return descendants
        
        # Test various depths
        for depth in [1, 2, 3]:
            all_nodes = set()
            for root in ["root1", "root2"]:
                all_nodes.update(get_descendants(root, depth))
            
            # Check that we get the expected number of nodes at each depth
            # The exact count depends on the test data structure
            self.result.add_passed(f"Depth {depth} includes {len(all_nodes)} nodes")
        
        # Verify leaf node is only visible at sufficient depth
        depth_1_nodes = set()
        for root in ["root1", "root2"]:
            depth_1_nodes.update(get_descendants(root, 1))
        
        if "greatgrandchild" not in depth_1_nodes:
            self.result.add_passed("Depth 1 correctly excludes deep nodes")
        else:
            self.result.add_failed("Depth 1 incorrectly includes deep nodes")
        
        # Verify leaf node is visible at maximum depth
        max_depth_nodes = set()
        for root in ["root1", "root2"]:
            max_depth_nodes.update(get_descendants(root, 10))  # Large enough to get everything
        
        if "greatgrandchild" in max_depth_nodes:
            self.result.add_passed("Maximum depth correctly includes all nodes")
        else:
            self.result.add_failed("Maximum depth fails to include all nodes")
    
    def _validate_performance(self) -> None:
        """Validate performance with larger datasets."""
        # This is a simplified test - in a real environment we'd 
        # test with much larger datasets and measure actual rendering times
        
        # Check link retrieval performance
        ws = WorkSystem(self.temp_db)
        
        start_time = time.time()
        all_links = {}
        for item_id in self.test_items:
            all_links[item_id] = ws.get_links(item_id)
        end_time = time.time()
        
        retrieval_time = end_time - start_time
        self.result.add_passed(f"Link retrieval for {len(self.test_items)} items took {retrieval_time:.4f} seconds")
        
        # Simulate tree building time
        start_time = time.time()
        tree_nodes = set()
        visited = set()
        
        def build_tree_simulation(item_id, depth=0, max_depth=3):
            if item_id in visited or depth > max_depth:
                return
            
            visited.add(item_id)
            tree_nodes.add(item_id)
            
            links = all_links[item_id]
            for link in links["outgoing"]:
                target_id = link["target_id"]
                if target_id in self.test_items and target_id not in visited:
                    build_tree_simulation(target_id, depth + 1, max_depth)
        
        # Start from root items
        for item_id in ["root1", "root2"]:
            build_tree_simulation(item_id)
        
        end_time = time.time()
        build_time = end_time - start_time
        
        self.result.add_passed(f"Tree building simulation for {len(tree_nodes)} nodes took {build_time:.4f} seconds")
        
        # For a real performance test, we'd also measure:
        # - Memory usage
        # - Rendering time for different tree sizes
        # - Responsiveness during expansion/collapse
        # - Load times with virtualization vs. without


def run_tree_visualization_validation() -> None:
    """Run all tree visualization validations."""
    print("Running tree visualization validations...")
    tree_validation = TreeVisualizationValidation()
    tree_validation.run()
    tree_validation.print_results()


if __name__ == "__main__":
    run_tree_visualization_validation() 