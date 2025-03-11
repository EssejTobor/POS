"""
Manual test script for the link_tree visualization.
Creates a sample network of thoughts and shows how to visualize their relationships.
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
    print_section("LINK TREE VISUALIZATION TEST")
    
    # Create a test network of thoughts and tasks with various relationships
    print_section("Creating test items and relationships")
    
    # Create initial thoughts
    print("Creating initial thought...")
    cli.onecmd("add ProjectX-th-HI-Initial Concept-This is the starting point for the project")
    
    print("Creating related task...")
    cli.onecmd("add ProjectX-t-MED-Research-Research related technologies")
    
    # Get the IDs of the created items
    thoughts = cli.work_system.get_items_by_type(ItemType.THOUGHT)
    tasks = cli.work_system.get_items_by_type(ItemType.TASK)
    
    initial_thought_id = thoughts[0].id if thoughts else None
    task_id = tasks[0].id if tasks else None
    
    if not initial_thought_id or not task_id:
        print("Error: Could not find test items. Make sure they were created successfully.")
        return
        
    # Create a reference link
    print(f"Creating a reference link from thought to task...")
    cli.onecmd(f"link {initial_thought_id} {task_id} references")
    
    # Create subsequent thoughts that evolve from the first
    print("Creating an evolved thought...")
    cli.onecmd(f"add ProjectX-th-MED-Refined Concept-This builds on the initial concept --link-to {initial_thought_id} --link-type evolves-from")
    
    # Get the new thought ID
    thoughts = cli.work_system.get_items_by_type(ItemType.THOUGHT)
    evolved_thought_id = thoughts[1].id if len(thoughts) > 1 else None
    
    # Create a thought inspired by the evolved thought
    print("Creating an inspired thought...")
    cli.onecmd(f"add ProjectX-th-LOW-Alternative Approach-This takes a different direction --link-to {evolved_thought_id} --link-type inspired-by")
    
    # Create a fourth thought that branches off in a new direction
    print("Creating a branching thought...")
    cli.onecmd(f"add ProjectX-th-HI-Implementation Plan-Concrete steps for implementation --link-to {evolved_thought_id} --link-type evolves-from")
    
    # Create a thought related to both the implementation and the task
    thoughts = cli.work_system.get_items_by_type(ItemType.THOUGHT)
    implementation_thought_id = thoughts[3].id if len(thoughts) > 3 else None
    
    print("Creating a bridging thought...")
    cli.onecmd(f"add ProjectX-th-MED-Technical Limitations-Constraints to consider --link-to {implementation_thought_id} --link-type references")
    
    # Get the new thought ID
    thoughts = cli.work_system.get_items_by_type(ItemType.THOUGHT)
    technical_limitations_id = thoughts[4].id if len(thoughts) > 4 else None
    
    # Add a second link to connect it to the task
    print("Adding a second link to create multiple paths...")
    cli.onecmd(f"link {technical_limitations_id} {task_id} references")
    
    # Print all thoughts to show IDs
    print_section("Created Items")
    cli.onecmd("list thoughts")
    cli.onecmd("list ProjectX")
    
    # Visualize the link tree with different options
    print_section("Basic Link Tree (All Items)")
    cli.onecmd("link_tree")
    
    print_section("Link Tree Starting from Initial Thought")
    cli.onecmd(f"link_tree {initial_thought_id}")
    
    print_section("Link Tree for Thoughts Only")
    cli.onecmd("link_tree --thoughts")
    
    print_section("Link Tree with Limited Depth (1)")
    cli.onecmd(f"link_tree {initial_thought_id} 1")
    
    print_section("Link Tree Starting from Implementation Thought")
    cli.onecmd(f"link_tree {implementation_thought_id}")
    
    print_section("Test Completed")
    print("The link tree visualization has been demonstrated with various options.")

if __name__ == "__main__":
    main() 