"""
Debug test for thought listing functionality.
"""
import sys
import tempfile
from src.models import ItemType
from src.storage import WorkSystem

def main():
    # Create a temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    work_system = WorkSystem(temp_db.name)
    
    # Add some test items
    thought1 = work_system.add_item(
        goal="TestGoal1",
        title="Test Thought 1",
        item_type=ItemType.THOUGHT,
        description="This is a test thought"
    )
    
    thought2 = work_system.add_item(
        goal="TestGoal2",
        title="Test Thought 2",
        item_type=ItemType.THOUGHT,
        description="This is another test thought"
    )
    
    task = work_system.add_item(
        goal="TestGoal1",
        title="Test Task",
        item_type=ItemType.TASK,
        description="This is a test task"
    )
    
    # Test get_items_by_type
    print("\n=== Testing get_items_by_type ===")
    thoughts = work_system.get_items_by_type(ItemType.THOUGHT)
    print(f"Found {len(thoughts)} thoughts: {[t.title for t in thoughts]}")
    
    tasks = work_system.get_items_by_type(ItemType.TASK)
    print(f"Found {len(tasks)} tasks: {[t.title for t in tasks]}")
    
    # Test filtering thoughts by goal
    print("\n=== Testing filtering thoughts by goal ===")
    all_thoughts = work_system.get_items_by_type(ItemType.THOUGHT)
    goal1_thoughts = [t for t in all_thoughts if t.goal.lower() == "testgoal1"]
    print(f"Found {len(goal1_thoughts)} thoughts for TestGoal1: {[t.title for t in goal1_thoughts]}")
    
    # Clean up
    temp_db.close()

if __name__ == "__main__":
    main() 