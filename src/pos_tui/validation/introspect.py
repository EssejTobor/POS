"""
Utilities for introspecting application state.

This module provides tools to examine the database state and other
aspects of the application for validation purposes.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.models import ItemType, Priority, ItemStatus
from src.work_system import WorkSystem

def dump_database_state(db_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Dump the current database state to a file or return as a dictionary.
    
    Args:
        db_path: Path to the SQLite database file
        output_path: Optional path to save the output JSON
        
    Returns:
        Dictionary containing the database state
    """
    # Initialize work system with the specified database
    ws = WorkSystem(db_path)
    
    # Extract item and link data
    state = {
        "items": {},
        "links": [],
        "stats": {
            "item_count": len(ws.items),
            "link_count": 0,
            "types": {t.name: 0 for t in ItemType},
            "priorities": {p.name: 0 for p in Priority},
            "statuses": {s.name: 0 for s in ItemStatus}
        }
    }
    
    # Process items
    for item_id, item in ws.items.items():
        # Convert item to dictionary representation
        item_dict = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "item_type": item.item_type.name,
            "priority": item.priority.name,
            "status": item.status.name,
            "created_at": item.created_at.isoformat() if hasattr(item, "created_at") else None,
            "updated_at": item.updated_at.isoformat() if hasattr(item, "updated_at") else None,
            "tags": getattr(item, "tags", []),
        }
        
        state["items"][item_id] = item_dict
        
        # Update statistics
        state["stats"]["types"][item.item_type.name] += 1
        state["stats"]["priorities"][item.priority.name] += 1
        state["stats"]["statuses"][item.status.name] += 1
    
    # Get links if the method is available
    if hasattr(ws, "get_all_links"):
        links = ws.get_all_links()
        state["links"] = links
        state["stats"]["link_count"] = len(links)
    
    # Output results if requested
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"Database state saved to {output_path}")
    
    return state

def compare_database_states(state1: Dict[str, Any], state2: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Compare two database states and return differences.
    
    Args:
        state1: First database state
        state2: Second database state
        
    Returns:
        Tuple of (is_identical, list_of_differences)
    """
    differences = []
    
    # Compare item counts
    if len(state1["items"]) != len(state2["items"]):
        differences.append(f"Item count differs: {len(state1['items'])} vs {len(state2['items'])}")
    
    # Compare individual items
    for item_id, item1 in state1["items"].items():
        if item_id not in state2["items"]:
            differences.append(f"Item {item_id} exists in state1 but not in state2")
            continue
        
        item2 = state2["items"][item_id]
        for key, value1 in item1.items():
            if key not in item2:
                differences.append(f"Item {item_id}: field {key} missing in state2")
                continue
            
            value2 = item2[key]
            if value1 != value2:
                differences.append(f"Item {item_id}: field {key} differs: '{value1}' vs '{value2}'")
    
    # Check for items in state2 that aren't in state1
    for item_id in state2["items"]:
        if item_id not in state1["items"]:
            differences.append(f"Item {item_id} exists in state2 but not in state1")
    
    # Compare link counts if available
    if "links" in state1 and "links" in state2:
        if len(state1["links"]) != len(state2["links"]):
            differences.append(f"Link count differs: {len(state1['links'])} vs {len(state2['links'])}")
    
    return len(differences) == 0, differences

def print_item(item_id: str, db_path: str = None) -> None:
    """
    Print details of a specific item.
    
    Args:
        item_id: ID of the item to print
        db_path: Optional path to the database
    """
    # Use default database if not specified
    if db_path is None:
        db_path = os.path.join("data", "db", "work_items.db")
    
    # Initialize work system
    ws = WorkSystem(db_path)
    
    # Get the item
    if item_id not in ws.items:
        print(f"Item {item_id} not found in database")
        return
    
    item = ws.items[item_id]
    
    # Print item details
    print(f"\n===== Item Details: {item_id} =====")
    print(f"Title: {item.title}")
    print(f"Type: {item.item_type.name}")
    print(f"Status: {item.status.name}")
    print(f"Priority: {item.priority.name}")
    print(f"Created: {item.created_at.isoformat() if hasattr(item, 'created_at') else 'N/A'}")
    print(f"Updated: {item.updated_at.isoformat() if hasattr(item, 'updated_at') else 'N/A'}")
    print("\nDescription:")
    print(item.description or "(No description)")
    
    # Print tags if available
    if hasattr(item, "tags") and item.tags:
        print("\nTags:")
        for tag in item.tags:
            print(f"- {tag}")
    
    # Print links if available
    if hasattr(ws, "get_links"):
        links = ws.get_links(item_id)
        if links:
            print("\nLinks:")
            for link in links:
                print(f"- {link['source_id']} {link['link_type']} {link['target_id']}")
    
    print("=" * (19 + len(item_id)))

if __name__ == "__main__":
    # Default to current database if not specified
    db_path = os.path.join("data", "db", "work_items.db")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m src.pos_tui.validation.introspect dump [db_path] [output_path]")
        print("  python -m src.pos_tui.validation.introspect item <item_id> [db_path]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "dump":
        # Get database path if provided
        if len(sys.argv) >= 3:
            db_path = sys.argv[2]
        
        # Get output path if provided
        output_path = None
        if len(sys.argv) >= 4:
            output_path = sys.argv[3]
        
        # Dump database state
        state = dump_database_state(db_path, output_path)
        
        # Print summary if not saving to file
        if not output_path:
            print(json.dumps(state, indent=2))
        
        print(f"\nDatabase Statistics:")
        print(f"Items: {state['stats']['item_count']}")
        print(f"Links: {state['stats']['link_count']}")
        print("\nItem Types:")
        for type_name, count in state['stats']['types'].items():
            if count > 0:
                print(f"  {type_name}: {count}")
        
        print("\nItem Statuses:")
        for status_name, count in state['stats']['statuses'].items():
            if count > 0:
                print(f"  {status_name}: {count}")
    
    elif command == "item":
        if len(sys.argv) < 3:
            print("Error: Item ID required")
            print("Usage: python -m src.pos_tui.validation.introspect item <item_id> [db_path]")
            sys.exit(1)
        
        item_id = sys.argv[2]
        
        # Get database path if provided
        if len(sys.argv) >= 4:
            db_path = sys.argv[3]
        
        print_item(item_id, db_path) 