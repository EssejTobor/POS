"""
Simple script to test the CLI interactively.
"""
from src.cli import WorkSystemCLI
from src.models import ItemType

def main():
    # Create a CLI instance
    cli = WorkSystemCLI()
    
    # Add a thought
    print("\n=== Adding initial thought ===")
    cli.onecmd('add_thought TestProject-Initial Idea-This is my first thought')
    
    # Get the thought ID
    thought_id = [item.id for item in cli.work_system.get_items_by_type(ItemType.THOUGHT)][0]
    print(f"\nThought ID: {thought_id}")
    
    # List all items
    print("\n=== Listing all items ===")
    cli.onecmd('list')
    
    # Add a followup thought with a link to the first thought
    print("\n=== Adding a followup thought with link ===")
    cli.onecmd(f'add_thought TestProject-Followup Idea-This builds on my first thought --parent {thought_id}')
    
    # List all items again
    print("\n=== Listing all items again ===")
    cli.onecmd('list')
    
    # Get all thoughts
    thoughts = cli.work_system.get_items_by_type(ItemType.THOUGHT)
    
    # Display links between thoughts
    print("\n=== Links between thoughts ===")
    for thought in thoughts:
        links = cli.work_system.get_links(thought.id)
        print(f"\nThought: {thought.id} - {thought.title}")
        
        if links['outgoing']:
            print("  Outgoing links:")
            for link in links['outgoing']:
                print(f"    -> {link['target_id']} - {link['title']} (Type: {link['link_type']})")
                
        if links['incoming']:
            print("  Incoming links:")
            for link in links['incoming']:
                print(f"    <- {link['source_id']} - {link['title']} (Type: {link['link_type']})")

if __name__ == "__main__":
    main() 