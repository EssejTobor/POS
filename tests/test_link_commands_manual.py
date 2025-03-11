"""
Manual test script for the link and unlink commands.
"""
import os
import sys
from datetime import datetime

from src.models import ItemType
from src.storage import WorkSystem
from src.cli import WorkSystemCLI

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_section(title):
    """Print a section title with formatting"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def main():
    """Main test function"""
    # Create a CLI instance
    cli = WorkSystemCLI()
    
    # Clear the screen
    clear_screen()
    print_section("LINK/UNLINK COMMANDS TEST")
    
    # First, add some test items
    print_section("Creating test items")
    
    # Add a thought item
    cli.onecmd("add TestPhase5-th-MED-Initial Thought-This is a test thought for Phase 5")
    
    # Add a task item
    cli.onecmd("add TestPhase5-t-HI-Important Task-This is a test task for Phase 5")
    
    # List all items
    print_section("Listing all items")
    cli.onecmd("list TestPhase5")
    
    # Get the IDs of the created items
    thoughts = cli.work_system.get_items_by_type(ItemType.THOUGHT)
    tasks = cli.work_system.get_items_by_type(ItemType.TASK)
    
    thought_id = thoughts[0].id if thoughts else None
    task_id = tasks[0].id if tasks else None
    
    if not thought_id or not task_id:
        print("Error: Could not find test items. Make sure they were created successfully.")
        return
        
    # Display the IDs
    print(f"\nThought ID: {thought_id}")
    print(f"Task ID: {task_id}")
    
    # Testing the link command
    print_section("Testing link command")
    
    # Create a link with default type
    print("\n1. Creating a link with default type ('references'):")
    cli.onecmd(f"link {thought_id} {task_id}")
    
    # Display the links for the thought
    print("\nLinks for the thought:")
    links = cli.work_system.get_links(thought_id)
    
    if links['outgoing']:
        print(f"  Outgoing links: {len(links['outgoing'])}")
        for link in links['outgoing']:
            print(f"  → Target: {link['title']} (ID: {link['target_id']})")
            print(f"  → Link type: {link['link_type']}")
    else:
        print("  No outgoing links found.")
    
    # Testing the unlink command
    print_section("Testing unlink command")
    
    # Remove the link
    print("\n1. Removing the link:")
    cli.onecmd(f"unlink {thought_id} {task_id}")
    
    # Display the links for the thought after unlinking
    print("\nLinks for the thought after unlinking:")
    links = cli.work_system.get_links(thought_id)
    
    if links['outgoing']:
        print(f"  Outgoing links: {len(links['outgoing'])}")
        for link in links['outgoing']:
            print(f"  → Target: {link['title']} (ID: {link['target_id']})")
            print(f"  → Link type: {link['link_type']}")
    else:
        print("  No outgoing links found.")
    
    # Create a link with custom type
    print_section("Testing link command with custom type")
    
    # Create a link with custom type
    print("\n1. Creating a link with 'evolves-from' type:")
    cli.onecmd(f"link {thought_id} {task_id} evolves-from")
    
    # Display the links for the thought
    print("\nLinks for the thought:")
    links = cli.work_system.get_links(thought_id)
    
    if links['outgoing']:
        print(f"  Outgoing links: {len(links['outgoing'])}")
        for link in links['outgoing']:
            print(f"  → Target: {link['title']} (ID: {link['target_id']})")
            print(f"  → Link type: {link['link_type']}")
    else:
        print("  No outgoing links found.")
    
    # Final unlink for cleanup
    cli.onecmd(f"unlink {thought_id} {task_id}")
    
    print_section("Test Completed")
    print("The link and unlink commands were tested successfully.")

if __name__ == "__main__":
    main() 