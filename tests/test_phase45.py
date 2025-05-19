"""
Manual test script for Phase 4.5 implementation.
Tests the unified add command with linking functionality.
"""

import os
from typing import Optional

from src.models import ItemType
from src.schemas import AddItemInput
from src.storage import WorkSystem


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def print_section(title):
    """Print a section title with formatting"""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}\n")


def test_add_item_input_parsing():
    """Test that the AddItemInput class parses different command formats correctly"""

    print_section("Testing AddItemInput Parsing")

    try:
        # Test basic command
        cmd = "TestGoal-th-MED-Test Thought-This is a test thought"
        input_data = AddItemInput.parse_input(cmd)
        print("✓ Basic command parsing:")
        print(f"  Goal: {input_data.goal}")
        print(f"  Type: {input_data.type_}")
        print(f"  Priority: {input_data.priority}")
        print(f"  Title: {input_data.title}")
        print(f"  Description: {input_data.description}")
        print(f"  Link to: {input_data.link_to}")
        print(f"  Link type: {input_data.link_type}")

        # Test command with link_to
        cmd = "TestGoal-th-MED-Test Thought-This is a test thought --link-to abc123"
        input_data = AddItemInput.parse_input(cmd)
        print("\n✓ Command with link_to parsing:")
        print(f"  Goal: {input_data.goal}")
        print(f"  Type: {input_data.type_}")
        print(f"  Title: {input_data.title}")
        print(f"  Link to: {input_data.link_to}")
        print(f"  Link type: {input_data.link_type}")

        # Test command with link_to and link_type
        cmd = "TestGoal-th-MED-Test Thought-This is a test thought --link-to abc123 --link-type evolves-from"
        input_data = AddItemInput.parse_input(cmd)
        print("\n✓ Command with link_to and link_type parsing:")
        print(f"  Goal: {input_data.goal}")
        print(f"  Type: {input_data.type_}")
        print(f"  Title: {input_data.title}")
        print(f"  Link to: {input_data.link_to}")
        print(f"  Link type: {input_data.link_type}")

        # Test invalid link type
        try:
            cmd = "TestGoal-th-MED-Test Thought-This is a test thought --link-to abc123 --link-type invalid-type"
            input_data = AddItemInput.parse_input(cmd)
            print("\n✗ Failed to catch invalid link type")
        except ValueError as e:
            print("\n✓ Correctly caught invalid link type:")
            print(f"  Error: {str(e)}")

    except Exception as e:
        print(f"\n✗ Error in parsing tests: {str(e)}")


def setup_test_database() -> Optional[WorkSystem]:
    """Set up a test database and return a WorkSystem instance"""
    try:
        # Use a test database file
        test_db_path = "test_work_items.db"

        # Remove the test database if it exists
        if os.path.exists(f"data/db/{test_db_path}"):
            os.remove(f"data/db/{test_db_path}")

        # Create a new WorkSystem with the test database
        work_system = WorkSystem(test_db_path)
        return work_system
    except Exception as e:
        print(f"Error setting up test database: {str(e)}")
        return None


def test_add_item_with_links():
    """Test adding items with links using the WorkSystem"""

    print_section("Testing Item Creation and Linking")

    work_system = setup_test_database()
    if not work_system:
        print("Failed to set up test database")
        return

    try:
        # Add a task item first to link to
        task = work_system.add_item(
            goal="TestGoal",
            title="Test Task",
            item_type=ItemType.TASK,
            description="This is a test task",
        )
        print("✓ Added task item:")
        print(f"  ID: {task.id}")
        print(f"  Title: {task.title}")
        print(f"  Type: {task.item_type}")

        # Add a thought item with a link to the task
        thought = work_system.add_item(
            goal="TestGoal",
            title="Test Thought",
            item_type=ItemType.THOUGHT,
            description="This is a test thought linked to the task",
        )
        print("\n✓ Added thought item:")
        print(f"  ID: {thought.id}")
        print(f"  Title: {thought.title}")
        print(f"  Type: {thought.item_type}")

        # Create a link between the thought and the task
        link_success = work_system.add_link(thought.id, task.id, "evolves-from")

        if link_success:
            print("\n✓ Successfully created link")

            # Get links for the thought
            links = work_system.get_links(thought.id)
            print("\n✓ Links for thought:")
            print(f"  Outgoing links: {len(links['outgoing'])}")
            for link in links["outgoing"]:
                print(f"    → Link type: {link['link_type']}")
                print(f"    → Target: {link['title']} (ID: {link['target_id']})")

            # Get links for the task
            task_links = work_system.get_links(task.id)
            print("\n✓ Links for task:")
            print(f"  Incoming links: {len(task_links['incoming'])}")
            for link in task_links["incoming"]:
                print(f"    ← Link type: {link['link_type']}")
                print(f"    ← Source: {link['title']} (ID: {link['source_id']})")

        else:
            print("\n✗ Failed to create link")

        # Test getting items by type
        thoughts = work_system.get_items_by_type(ItemType.THOUGHT)
        print(f"\n✓ Found {len(thoughts)} thoughts")
        tasks = work_system.get_items_by_type(ItemType.TASK)
        print(f"✓ Found {len(tasks)} tasks")

    except Exception as e:
        print(f"\n✗ Error in item and link tests: {str(e)}")
    finally:
        # Clean up - remove the test database
        try:
            os.remove("data/db/test_work_items.db")
            print("\n✓ Test database cleaned up")
        except Exception as e:
            print(f"\n✗ Error cleaning up test database: {str(e)}")


if __name__ == "__main__":
    clear_screen()
    print_section("PHASE 4.5 IMPLEMENTATION TEST")

    test_add_item_input_parsing()
    test_add_item_with_links()

    print("\nTests completed!")
