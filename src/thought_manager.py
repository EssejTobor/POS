from datetime import datetime
import logging
import threading
from typing import List, Optional, Dict, Any, Set, Tuple
import uuid
from collections import defaultdict

from .models import ThoughtNode, BranchType, ThoughtStatus
from .database import Database 
from .config import Config

logger = logging.getLogger(__name__)

class ThoughtManager:
    """Manages thought operations with thread safety"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with optional custom db path"""
        self.db = Database(db_path or Config.DB_PATH)
        self.thought_cache: Dict[str, ThoughtNode] = {}
        self.lock = threading.Lock()

    def add_thought(self, title: str, content: str, 
                   branch_name: str = "main",
                   tags: Optional[List[str]] = None,
                   status: ThoughtStatus = ThoughtStatus.DRAFT) -> ThoughtNode:
        """Create a new root thought"""
        with self.lock:
            try:
                thought = ThoughtNode(
                    title=title,
                    content=content,
                    branch_name=branch_name,
                    tags=tags or [],
                    status=status
                )
                thought.id = self._generate_id(branch_name)
                
                # Add to database
                self.db.add_thought(thought)
                
                # Update cache
                self.thought_cache[thought.id] = thought
                logger.info(f"Created new thought: {thought.id} - {thought.title}")
                return thought
            except Exception as e:
                logger.error(f"Error creating thought: {e}", exc_info=True)
                raise
    
    def branch_thought(self, parent_id: str, title: str, content: str,
                       branch_name: str, branch_type: BranchType,
                       tags: Optional[List[str]] = None,
                       status: ThoughtStatus = ThoughtStatus.DRAFT) -> ThoughtNode:
        """Create a new branch from existing thought"""
        with self.lock:
            try:
                parent = self.get_thought_by_id(parent_id)
                if not parent:
                    error_msg = f"Parent thought {parent_id} not found"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                thought = ThoughtNode(
                    title=title,
                    content=content,
                    branch_name=branch_name,
                    parent_id=parent_id,
                    branch_type=branch_type,
                    tags=tags or [],
                    status=status
                )
                thought.id = self._generate_id(branch_name)
                
                # Add thought and relationship
                self.db.add_thought(thought)
                self.db.add_thought_relationship(
                    parent_id=parent_id,
                    child_id=thought.id,
                    relationship_type=branch_type.value
                )
                
                # Update cache
                self.thought_cache[thought.id] = thought
                logger.info(f"Created branch thought: {thought.id} from parent {parent_id}")
                return thought
            except Exception as e:
                logger.error(f"Error branching thought: {e}", exc_info=True)
                raise
    
    def merge_thoughts(self, thought_ids: List[str], title: str, 
                       content: str, branch_name: str) -> ThoughtNode:
        """Merge multiple thoughts into a new synthesis"""
        with self.lock:
            try:
                # Validate all thoughts exist
                thoughts = []
                missing_ids = []
                for tid in thought_ids:
                    thought = self.get_thought_by_id(tid)
                    if thought:
                        thoughts.append(thought)
                    else:
                        missing_ids.append(tid)
                
                if missing_ids:
                    error_msg = f"Thoughts not found: {missing_ids}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Create merged thought
                merged = ThoughtNode(
                    title=title,
                    content=content,
                    branch_name=branch_name,
                    branch_type=BranchType.REFINEMENT,
                    # Combine tags from all thoughts
                    tags=list(set(tag for t in thoughts for tag in t.tags))
                )
                merged.id = self._generate_id(branch_name)
                
                # Add to database
                self.db.add_thought(merged)
                
                # Add relationships to all parents
                for parent_id in thought_ids:
                    self.db.add_thought_relationship(
                        parent_id=parent_id,
                        child_id=merged.id,
                        relationship_type="merge"
                    )
                
                # Update cache
                self.thought_cache[merged.id] = merged
                logger.info(f"Merged thoughts {thought_ids} into new thought {merged.id}")
                return merged
            except Exception as e:
                logger.error(f"Error merging thoughts: {e}", exc_info=True)
                raise
    
    def get_thought_by_id(self, thought_id: str) -> Optional[ThoughtNode]:
        """Get a thought by ID"""
        # Check cache first
        if thought_id in self.thought_cache:
            return self.thought_cache[thought_id]
        
        try:
            # Fetch from database
            thought = self.db.get_thought(thought_id)
            if thought:
                self.thought_cache[thought_id] = thought
            return thought
        except Exception as e:
            logger.error(f"Error getting thought {thought_id}: {e}")
            return None
    
    def update_thought(self, thought_id: str, title: str, content: str,
                      branch_name: str, tags: List[str], 
                      status: ThoughtStatus) -> bool:
        """Update an existing thought"""
        with self.lock:
            try:
                # Ensure thought exists
                existing = self.get_thought_by_id(thought_id)
                if not existing:
                    logger.error(f"Cannot update: Thought {thought_id} not found")
                    return False
                
                # Update thought properties
                existing.title = title
                existing.content = content
                existing.branch_name = branch_name
                existing.tags = tags
                existing.status = status
                existing.updated_at = datetime.now()
                
                # Update in database
                result = self.db.update_thought(existing)
                
                # Update cache
                if result:
                    self.thought_cache[thought_id] = existing
                    logger.info(f"Updated thought: {thought_id}")
                
                return result
            except Exception as e:
                logger.error(f"Error updating thought: {e}", exc_info=True)
                return False
    
    def delete_thought(self, thought_id: str) -> bool:
        """Delete a thought and its relationships"""
        with self.lock:
            try:
                # Ensure thought exists
                existing = self.get_thought_by_id(thought_id)
                if not existing:
                    logger.error(f"Cannot delete: Thought {thought_id} not found")
                    return False
                
                # Delete from database
                result = self.db.delete_thought(thought_id)
                
                # Remove from cache
                if result and thought_id in self.thought_cache:
                    del self.thought_cache[thought_id]
                    logger.info(f"Deleted thought: {thought_id}")
                
                return result
            except Exception as e:
                logger.error(f"Error deleting thought: {e}", exc_info=True)
                return False
    
    def get_thought_lineage(self, thought_id: str) -> List[ThoughtNode]:
        """Get all thoughts in lineage (parents and children)"""
        try:
            lineage = []
            visited: Set[str] = set()
            
            def traverse(node_id: str) -> None:
                if node_id in visited:
                    return
                visited.add(node_id)
                
                node = self.get_thought_by_id(node_id)
                if node:
                    lineage.append(node)
                    
                    # Get parents
                    parents = self.db.get_thought_parents(node_id)
                    for parent in parents:
                        traverse(parent.id)
                    
                    # Get children
                    children = self.db.get_thought_children(node_id)
                    for child in children:
                        traverse(child.id)
            
            traverse(thought_id)
            return lineage
        except Exception as e:
            logger.error(f"Error getting thought lineage for {thought_id}: {e}")
            return []
    
    def get_thought_tree(self, thought_id: str, max_depth: Optional[int] = None) -> Dict[str, Any]:
        """Get a hierarchical tree of thoughts starting from the given thought"""
        try:
            # Get the root thought
            root_thought = self.get_thought_by_id(thought_id)
            if not root_thought:
                logger.error(f"Root thought {thought_id} not found")
                return {}
            
            # Build the tree recursively
            tree = self._build_thought_tree(root_thought, max_depth)
            return tree
        except Exception as e:
            logger.error(f"Error getting thought tree for {thought_id}: {e}")
            return {}
    
    def _build_thought_tree(self, thought: ThoughtNode, max_depth: Optional[int] = None, 
                           current_depth: int = 0) -> Dict[str, Any]:
        """Recursively build a thought tree"""
        tree = {
            "id": thought.id,
            "title": thought.title,
            "content": thought.content,
            "status": thought.status.value,
            "branch_name": thought.branch_name,
            "tags": thought.tags,
            "created_at": thought.created_at.isoformat(),
            "updated_at": thought.updated_at.isoformat(),
            "children": []
        }
        
        # Stop recursion if we've reached max depth
        if max_depth is not None and current_depth >= max_depth:
            return tree
        
        # Get children and add them to the tree
        children = self.db.get_thought_children(thought.id)
        for child in children:
            child_tree = self._build_thought_tree(child, max_depth, current_depth + 1)
            tree["children"].append(child_tree)
        
        return tree
    
    def visualize_thought_tree(self, thought_id: str, max_depth: Optional[int] = None,
                              include_content: bool = False) -> str:
        """Generate an ASCII representation of the thought tree"""
        try:
            # Get the thought tree
            tree = self.get_thought_tree(thought_id, max_depth)
            if not tree:
                return "No thought tree found"
            
            # Generate ASCII representation
            lines = []
            self._generate_ascii_tree(tree, "", True, lines, include_content)
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error visualizing thought tree for {thought_id}: {e}")
            return f"Error visualizing thought tree: {str(e)}"
    
    def _generate_ascii_tree(self, node: Dict[str, Any], prefix: str, is_last: bool, 
                            lines: List[str], include_content: bool) -> None:
        """Recursively generate ASCII tree lines"""
        # Determine the branch character
        branch = "└── " if is_last else "├── "
        
        # Format status with color indicators
        status_indicators = {
            "draft": "🟡",      # Yellow for draft
            "evolving": "🔵",   # Blue for evolving
            "crystallized": "🟢" # Green for crystallized
        }
        status_indicator = status_indicators.get(node["status"], "⚪")
        
        # Format tags
        tags_str = f" [{', '.join(['#' + tag for tag in node.get('tags', [])])}]" if node.get("tags") else ""
        
        # Add the node line
        node_line = f"{prefix}{branch}{status_indicator} {node['title']}{tags_str}"
        lines.append(node_line)
        
        # Add content if requested
        if include_content and node.get("content"):
            # Truncate content if too long
            content = node["content"]
            if len(content) > 100:
                content = content[:97] + "..."
            
            # Format content as indented block
            content_prefix = prefix + ("    " if is_last else "│   ") + "    "
            for line in content.split("\n"):
                if line.strip():  # Skip empty lines
                    lines.append(f"{content_prefix}{line}")
        
        # Process children
        children = node.get("children", [])
        for i, child in enumerate(children):
            is_last_child = i == len(children) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            self._generate_ascii_tree(child, new_prefix, is_last_child, lines, include_content)
    
    def get_all_thoughts(self) -> List[ThoughtNode]:
        """Get all thoughts"""
        try:
            thoughts = self.db.get_all_thoughts()
            # Update cache with retrieved thoughts
            for thought in thoughts:
                self.thought_cache[thought.id] = thought
            return thoughts
        except Exception as e:
            logger.error(f"Error getting all thoughts: {e}")
            return []
    
    def get_thoughts_by_branch(self, branch_name: str) -> List[ThoughtNode]:
        """Get all thoughts in a specific branch"""
        try:
            thoughts = self.db.get_thoughts_by_branch(branch_name)
            # Update cache with retrieved thoughts
            for thought in thoughts:
                self.thought_cache[thought.id] = thought
            return thoughts
        except Exception as e:
            logger.error(f"Error getting thoughts by branch {branch_name}: {e}")
            return []
    
    def get_all_branches(self) -> List[str]:
        """Get all unique branch names"""
        try:
            return self.db.get_all_thought_branches()
        except Exception as e:
            logger.error(f"Error getting all branches: {e}")
            return []
    
    def search_thoughts(self, query: str) -> List[ThoughtNode]:
        """Search thoughts using FTS"""
        try:
            results = self.db.search_thoughts(query)
            # Update cache with search results
            for thought in results:
                self.thought_cache[thought.id] = thought
            return results
        except Exception as e:
            logger.error(f"Error searching thoughts with query '{query}': {e}")
            return []
    
    def get_thoughts_by_tag(self, tag: str) -> List[ThoughtNode]:
        """Get all thoughts with a specific tag"""
        try:
            results = self.db.get_thoughts_by_tag(tag)
            # Update cache with results
            for thought in results:
                self.thought_cache[thought.id] = thought
            return results
        except Exception as e:
            logger.error(f"Error getting thoughts by tag '{tag}': {e}")
            return []
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags used in thoughts"""
        try:
            return self.db.get_all_thought_tags()
        except Exception as e:
            logger.error(f"Error getting all tags: {e}")
            return []
    
    def get_tag_cloud(self) -> Dict[str, int]:
        """Get a tag cloud with tag frequencies"""
        try:
            return self.db.get_thought_tag_frequencies()
        except Exception as e:
            logger.error(f"Error getting tag cloud: {e}")
            return {}
    
    def get_thoughts_by_status(self, status: ThoughtStatus) -> List[ThoughtNode]:
        """Get all thoughts with a specific status"""
        try:
            results = self.db.get_thoughts_by_status(status.value)
            # Update cache with results
            for thought in results:
                self.thought_cache[thought.id] = thought
            return results
        except Exception as e:
            logger.error(f"Error getting thoughts by status '{status}': {e}")
            return []
    
    def crystallize_thought(self, thought_id: str) -> bool:
        """Mark a thought as crystallized"""
        with self.lock:
            try:
                thought = self.get_thought_by_id(thought_id)
                if not thought:
                    logger.error(f"Cannot crystallize: Thought {thought_id} not found")
                    return False
                
                thought.status = ThoughtStatus.CRYSTALLIZED
                thought.updated_at = datetime.now()
                
                result = self.db.update_thought(thought)
                if result:
                    self.thought_cache[thought_id] = thought
                    logger.info(f"Crystallized thought: {thought_id}")
                
                return result
            except Exception as e:
                logger.error(f"Error crystallizing thought: {e}", exc_info=True)
                return False
    
    def _generate_id(self, branch_name: str) -> str:
        """Generate a unique ID for a thought"""
        # Create a UUID
        uid = str(uuid.uuid4())
        # Use first 8 characters for brevity
        short_id = uid[:8]
        # Add branch prefix
        branch_prefix = branch_name.lower().replace(" ", "-")[:10]
        return f"{branch_prefix}-{short_id}" 