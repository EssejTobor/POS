"""
Worker classes for handling item-related database operations.

This module provides specialized worker threads for fetching, saving,
and managing links between work items.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import traceback

from ...storage import WorkSystem
from ... import schemas
from ...models import ItemType, Priority, ItemStatus
from .base import BaseWorker


class ItemSearchWorker(BaseWorker):
    """Worker for searching items to use in linking operations."""
    
    def _run(
        self,
        search_term: str,
        exclude_ids: Optional[List[str]] = None,
        limit: int = 10,
        **_kwargs,
    ) -> Dict[str, Any]:
        """Search for items by title or ID.
        
        Args:
            search_term: Text to search for in item titles or IDs
            exclude_ids: Item IDs to exclude from results
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        work_system = WorkSystem()
        
        try:
            # First check if the search term is an exact ID match
            if work_system.item_exists(search_term):
                item = work_system.get_work_item(search_term)
                
                # Skip if in exclude list
                if exclude_ids and search_term in exclude_ids:
                    items = []
                else:
                    # Convert to dict format
                    items = [item]
            else:
                # Search by title (case insensitive)
                items = work_system.get_work_items(
                    search=search_term,
                    limit=limit
                )
                
                # Filter out excluded IDs
                if exclude_ids:
                    items = [item for item in items if item["id"] not in exclude_ids]
            
            return {
                "success": True,
                "items": items[:limit],
                "total_count": len(items),
                "search_term": search_term,
            }
        except Exception as e:
            error_traceback = traceback.format_exc()
            return {
                "success": False,
                "message": f"Error searching items: {str(e)}",
                "traceback": error_traceback,
                "search_term": search_term,
            }


class ItemFetchWorker(BaseWorker):
    """Worker for retrieving work items from the database.

    Supports filtering, sorting, and pagination for efficient data loading.
    """

    def _run(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 50,
        search_term: Optional[str] = None,
        include_links: bool = False,
        **_kwargs,
    ) -> Dict[str, Any]:
        """Fetch work items based on filters, sorting, and pagination.

        Args:
            filters: Dictionary of field-value pairs to filter items
            sort_by: Field to sort by (e.g., 'priority', 'created_at')
            sort_order: Sort direction ('asc' or 'desc')
            page: Page number to retrieve (1-indexed)
            page_size: Number of items per page
            search_term: Text to search for in item titles and descriptions
            include_links: Whether to include linked items in the results

        Returns:
            Dictionary containing items, total count, and pagination info
        """
        work_system = WorkSystem()
        
        # Calculate offset for pagination
        offset = (page - 1) * page_size
        
        # Build query parameters
        query_params = {}
        
        # Add filters if provided
        if filters:
            query_params.update(filters)
        
        # Add search term if provided
        if search_term:
            query_params["search"] = search_term
        
        # Execute query with pagination
        items = work_system.get_work_items(
            limit=page_size,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            **query_params
        )
        
        # Get total count for pagination
        total_count = work_system.count_work_items(**query_params)
        
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
        
        # Include link data if requested
        if include_links and items:
            for item in items:
                item_id = item["id"]
                links = work_system.get_links(item_id)
                item["links"] = links
        
        return {
            "items": items,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }


class ItemSaveWorker(BaseWorker):
    """Worker for creating or updating work items in the database.

    Handles both creating new items and updating existing ones,
    as well as managing relationships between items.
    """

    def _run(
        self,
        item_data: Dict[str, Any],
        links: Optional[List[Dict[str, str]]] = None,
        item_id: Optional[str] = None,
        **_kwargs,
    ) -> Dict[str, Any]:
        """Create or update a work item and its links.

        Args:
            item_data: Dictionary of item field values
            links: List of link data dictionaries with target_id and link_type
            item_id: ID of the item to update (None for new items)

        Returns:
            Dictionary with the created/updated item data and success status
        """
        work_system = WorkSystem()
        
        try:
            # Start a transaction for atomic operations
            with work_system._atomic_operation():
                if item_id:
                    # Update existing item
                    success = work_system.update_item(item_id, **item_data)
                    if success:
                        # Get the updated item
                        item = work_system.get_work_item(item_id)
                        
                        # Handle links if provided
                        if links is not None:
                            self._process_links(work_system, item_id, links)
                        
                        return {
                            "success": True,
                            "item": item,
                            "message": "Item updated successfully",
                            "is_new": False,
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Failed to update item {item_id}",
                            "is_new": False,
                        }
                else:
                    # Create new item
                    goal = item_data.get("goal", "")
                    item_type_val = item_data.get("item_type", ItemType.TASK.value)
                    item_type = ItemType(item_type_val)
                    title = item_data.get("title", "")
                    description = item_data.get("description", "")
                    priority_val = item_data.get("priority", Priority.MED.value)
                    priority = Priority(int(priority_val)) if not isinstance(priority_val, Priority) else priority_val
                    status_val = item_data.get("status", ItemStatus.NOT_STARTED.value)
                    status = ItemStatus(status_val)
                    tags = item_data.get("tags", [])

                    # Create new item
                    new_item = work_system.add_work_item(
                        goal=goal,
                        item_type=item_type,
                        title=title,
                        description=description,
                        priority=priority,
                    )
                    new_id = new_item.id

                    # Apply additional fields
                    work_system.update_item(new_id, status=status)
                    for tag in tags:
                        work_system.add_tag_to_item(new_id, tag)
                    
                    if new_id:
                        # Get the created item
                        item = work_system.items[new_id].to_dict()
                        
                        # Handle links if provided
                        if links is not None:
                            self._process_links(work_system, new_id, links)
                        
                        return {
                            "success": True,
                            "item": item,
                            "message": "Item created successfully",
                            "is_new": True,
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Failed to create item",
                            "is_new": True,
                        }
        except Exception as e:
            error_traceback = traceback.format_exc()
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "traceback": error_traceback,
                "is_new": item_id is None,
            }

    def _process_links(
        self, work_system: WorkSystem, item_id: str, new_links: List[Dict[str, str]]
    ) -> None:
        """Process link changes for an item.
        
        Args:
            work_system: The WorkSystem instance
            item_id: The ID of the source item
            new_links: List of new links to establish
        """
        # Get existing links
        existing_links = work_system.get_links(item_id).get("outgoing", [])
        
        # Convert existing links to set of target IDs for easier comparison
        existing_target_ids = {link["target_id"] for link in existing_links}
        
        # Convert new links to dictionary for easier lookup
        new_links_dict = {link["id"]: link["link_type"] for link in new_links}
        new_target_ids = set(new_links_dict.keys())
        
        # Links to remove (in existing but not in new)
        to_remove = existing_target_ids - new_target_ids
        
        # Links to add (in new but not in existing)
        to_add = new_target_ids - existing_target_ids
        
        # Links to update (in both but possibly with different link types)
        to_update = new_target_ids.intersection(existing_target_ids)
        
        # Process removals
        for target_id in to_remove:
            work_system.remove_link(item_id, target_id)
        
        # Process additions
        for target_id in to_add:
            link_type = new_links_dict[target_id]
            work_system.add_link(item_id, target_id, link_type)
        
        # Process updates (remove and re-add with new link type)
        for target_id in to_update:
            # Find existing link type
            existing_link_type = next(
                (link["link_type"] for link in existing_links if link["target_id"] == target_id),
                None
            )
            
            # If link type changed, update it
            if existing_link_type != new_links_dict[target_id]:
                work_system.remove_link(item_id, target_id)
                work_system.add_link(item_id, target_id, new_links_dict[target_id])


class LinkWorker(BaseWorker):
    """Worker for managing relationships between work items.

    Handles creating, retrieving, and deleting links between items.
    """

    def _run(
        self,
        operation: str,
        source_id: str,
        target_id: Optional[str] = None,
        link_type: Optional[str] = None,
        batch_links: Optional[List[Dict[str, Any]]] = None,
        **_kwargs,
    ) -> Dict[str, Any]:
        """Perform operations on item links.

        Args:
            operation: The operation to perform ('add', 'remove', 'get', 'batch')
            source_id: The ID of the source item
            target_id: The ID of the target item (for 'add' and 'remove')
            link_type: The type of link to create (for 'add')
            batch_links: List of link operations for batch processing

        Returns:
            Dictionary with operation results and success status
        """
        work_system = WorkSystem()
        
        try:
            if operation == "add" and target_id and link_type:
                # Add link between items
                success = work_system.add_link(source_id, target_id, link_type)
                return {
                    "success": success,
                    "message": "Link created successfully" if success else "Failed to create link",
                    "operation": "add",
                    "source_id": source_id,
                    "target_id": target_id,
                    "link_type": link_type,
                }
            
            elif operation == "remove" and target_id:
                # Remove link between items
                success = work_system.remove_link(source_id, target_id)
                return {
                    "success": success,
                    "message": "Link removed successfully" if success else "Failed to remove link",
                    "operation": "remove",
                    "source_id": source_id,
                    "target_id": target_id,
                }
            
            elif operation == "get":
                # Get links for the item
                links = work_system.get_links(source_id)
                return {
                    "success": True,
                    "operation": "get",
                    "source_id": source_id,
                    "links": links,
                }
                
            elif operation == "batch" and batch_links:
                # Process multiple link operations in a single transaction
                results = []
                
                with work_system._atomic_operation():
                    for link_op in batch_links:
                        op_type = link_op.get("operation")
                        src_id = link_op.get("source_id", source_id)
                        tgt_id = link_op.get("target_id")
                        lnk_type = link_op.get("link_type")
                        
                        if op_type == "add" and tgt_id and lnk_type:
                            success = work_system.add_link(src_id, tgt_id, lnk_type)
                            results.append({
                                "operation": "add",
                                "source_id": src_id,
                                "target_id": tgt_id,
                                "link_type": lnk_type,
                                "success": success
                            })
                        elif op_type == "remove" and tgt_id:
                            success = work_system.remove_link(src_id, tgt_id)
                            results.append({
                                "operation": "remove",
                                "source_id": src_id,
                                "target_id": tgt_id,
                                "success": success
                            })
                
                return {
                    "success": True,
                    "operation": "batch",
                    "results": results,
                    "source_id": source_id,
                }
            
            else:
                return {
                    "success": False,
                    "message": f"Invalid operation: {operation}",
                    "operation": operation,
                }
                
        except Exception as e:
            error_traceback = traceback.format_exc()
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "traceback": error_traceback,
                "operation": operation,
            } 