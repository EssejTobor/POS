# POS Textual UI Test Plan

This document outlines the testing strategy for the POS Textual UI components, focusing on PyTest as the primary testing framework.

## Testing Strategy

Testing a Terminal User Interface (TUI) presents unique challenges compared to traditional GUI or web applications. Our approach will use:

1. **Unit tests** for individual components and utility functions
2. **Integration tests** for component interactions
3. **Snapshot tests** for UI appearance
4. **Headless tests** for full application flows

We'll leverage Textual's built-in testing capabilities, including `AppTest` for simulating user interactions and verifying UI state.

## Test Environment Setup

```python
# tests/conftest.py
import pytest
from textual.app import App
from textual.driver import Driver
from textual.widgets import Button

from src.pos_tui.app import POSTUI
from src.storage import WorkSystem

@pytest.fixture
def mock_work_system():
    """Create a mock WorkSystem with predefined test data."""
    system = WorkSystem(":memory:")
    # Add test items
    system.add_work_item("Test Task", "A test task", "TASK")
    system.add_work_item("Test Thought", "A test thought", "THOUGHT")
    # Add test links
    system.add_link("ta1", "th1", "references")
    return system

@pytest.fixture
def app():
    """Create a test instance of the POSTUI app."""
    app = POSTUI()
    app.work_system = mock_work_system()
    return app

@pytest.fixture
def app_test(app):
    """Create an AppTest instance for testing the app."""
    async def _app_test():
        async with AppTest(app) as pilot:
            yield pilot
    return _app_test
```

## 1. Dashboard Screen Tests

### Unit Tests

```python
# tests/pos_tui/screens/test_dashboard.py
import pytest
from textual.app import ComposeResult
from textual.pilot import Pilot

from src.pos_tui.screens.dashboard import DashboardScreen
from src.models import ItemType, ItemStatus, Priority

class TestDashboardScreen:
    async def test_dashboard_composition(self, app_test):
        """Test that the dashboard screen composes correctly."""
        async with app_test() as pilot:
            # Navigate to dashboard
            dashboard = pilot.app.query_one(DashboardScreen)
            # Check that required widgets are present
            assert dashboard.query_one("#item_table")
            assert dashboard.query_one("#filter_bar")
            
    async def test_dashboard_data_loading(self, app_test):
        """Test that the dashboard loads data from the work system."""
        async with app_test() as pilot:
            # Navigate to dashboard
            dashboard = pilot.app.query_one(DashboardScreen)
            # Trigger data loading
            await pilot.press("r")  # Refresh key
            # Wait for worker to complete
            await pilot.wait_for_animation()
            # Check that table has data
            table = dashboard.query_one("#item_table")
            assert len(table.rows) > 0
            
    async def test_dashboard_filtering(self, app_test):
        """Test that filtering works correctly."""
        async with app_test() as pilot:
            # Navigate to dashboard
            dashboard = pilot.app.query_one(DashboardScreen)
            # Find filter input
            filter_input = dashboard.query_one("#filter_input")
            # Set filter text
            await pilot.click(filter_input)
            await pilot.write("Test Task")
            # Press apply filter button
            filter_button = dashboard.query_one("#apply_filter")
            await pilot.click(filter_button)
            # Check results
            table = dashboard.query_one("#item_table")
            assert len(table.rows) == 1
            assert "Test Task" in table.rows[0][1].plain
```

### Integration Tests

```python
# tests/pos_tui/test_dashboard_integration.py
import pytest

class TestDashboardIntegration:
    async def test_item_selection_updates_details(self, app_test):
        """Test that selecting an item shows details in the details panel."""
        async with app_test() as pilot:
            # Navigate to dashboard
            dashboard = pilot.app.query_one("DashboardScreen")
            # Select first item in table
            table = dashboard.query_one("#item_table")
            await pilot.click(table.coordinate_for_cell(0, 0))
            # Check that details panel shows the selected item
            details = dashboard.query_one("#details_panel")
            assert "Test Task" in details.render()
            
    async def test_action_button_triggers_edit(self, app_test):
        """Test that clicking edit button opens edit form."""
        async with app_test() as pilot:
            # Navigate to dashboard
            dashboard = pilot.app.query_one("DashboardScreen")
            # Select first item in table
            table = dashboard.query_one("#item_table")
            await pilot.click(table.coordinate_for_cell(0, 0))
            # Click edit button
            edit_button = dashboard.query_one("#edit_button")
            await pilot.click(edit_button)
            # Check that edit form is shown
            assert pilot.app.query_one("ItemEntryForm")
```

## 2. Item Entry Form Tests

### Unit Tests

```python
# tests/pos_tui/widgets/test_item_form.py
import pytest
from textual.pilot import Pilot

from src.pos_tui.widgets.item_form import ItemEntryForm
from src.models import ItemType, Priority, ItemStatus

class TestItemEntryForm:
    async def test_form_initial_state(self, app_test):
        """Test that the form initializes with correct fields."""
        async with app_test() as pilot:
            # Create and mount form
            form = ItemEntryForm()
            await pilot.mount(form)
            # Check that all required fields exist
            assert form.query_one("#title_field")
            assert form.query_one("#description_field")
            assert form.query_one("#type_selector")
            assert form.query_one("#priority_selector")
            
    async def test_form_validation(self, app_test):
        """Test that form validation works correctly."""
        async with app_test() as pilot:
            # Create and mount form
            form = ItemEntryForm()
            await pilot.mount(form)
            # Submit without required fields
            submit_button = form.query_one("#submit_button")
            await pilot.click(submit_button)
            # Check for validation error message
            assert form.query_one("#validation_message").text == "Title is required"
            
    async def test_form_submission(self, app_test, mock_work_system):
        """Test that form submission creates a work item."""
        async with app_test() as pilot:
            # Create form with work system
            form = ItemEntryForm(work_system=mock_work_system)
            await pilot.mount(form)
            # Fill out form
            title_field = form.query_one("#title_field")
            await pilot.click(title_field)
            await pilot.write("New Test Item")
            
            description_field = form.query_one("#description_field")
            await pilot.click(description_field)
            await pilot.write("Description of test item")
            
            # Select type
            type_selector = form.query_one("#type_selector")
            await pilot.click(type_selector)
            await pilot.press("down")  # Select TASK
            await pilot.press("enter")
            
            # Submit form
            submit_button = form.query_one("#submit_button")
            await pilot.click(submit_button)
            
            # Wait for worker to complete
            await pilot.wait_for_worker()
            
            # Check that item was created
            items = mock_work_system.get_work_items()
            assert any(item.title == "New Test Item" for item in items)
```

## 3. Link Tree Tests

### Unit Tests

```python
# tests/pos_tui/widgets/test_link_tree.py
import pytest
from textual.pilot import Pilot

from src.pos_tui.widgets.link_tree import LinkTree

class TestLinkTree:
    async def test_tree_initial_state(self, app_test, mock_work_system):
        """Test that the tree initializes correctly."""
        async with app_test() as pilot:
            # Create and mount tree
            tree = LinkTree(work_system=mock_work_system)
            await pilot.mount(tree)
            # Check that tree is empty initially
            assert len(tree.nodes) == 0
            
    async def test_tree_loading(self, app_test, mock_work_system):
        """Test that the tree loads data correctly."""
        async with app_test() as pilot:
            # Create and mount tree
            tree = LinkTree(work_system=mock_work_system)
            await pilot.mount(tree)
            # Load tree with root item
            await tree.load_tree("ta1")
            # Wait for worker to complete
            await pilot.wait_for_worker()
            # Check that tree has nodes
            assert len(tree.nodes) > 0
            # Check that root node is correct
            assert tree.root.label == "Test Task"
            
    async def test_node_expansion(self, app_test, mock_work_system):
        """Test that nodes can be expanded and collapsed."""
        async with app_test() as pilot:
            # Create and mount tree
            tree = LinkTree(work_system=mock_work_system)
            await pilot.mount(tree)
            # Load tree with root item
            await tree.load_tree("ta1")
            # Wait for worker to complete
            await pilot.wait_for_worker()
            # Get first node
            node = tree.nodes[0]
            # Expand node
            await pilot.click(node)
            # Check that node is expanded
            assert node.is_expanded
            # Collapse node
            await pilot.click(node)
            # Check that node is collapsed
            assert not node.is_expanded
```

## 4. Command Palette Tests

### Unit Tests

```python
# tests/pos_tui/test_commands.py
import pytest
from textual.pilot import Pilot

from src.pos_tui.commands import CommandRegistry, Command

class TestCommandRegistry:
    def test_command_registration(self):
        """Test that commands can be registered."""
        registry = CommandRegistry()
        cmd = Command("test", "Test Command", lambda: None)
        registry.register(cmd)
        assert "test" in registry.commands
        
    def test_command_categorization(self):
        """Test that commands are properly categorized."""
        registry = CommandRegistry()
        cmd1 = Command("new_item", "Create New Item", lambda: None, category="items")
        cmd2 = Command("filter", "Filter View", lambda: None, category="view")
        registry.register(cmd1)
        registry.register(cmd2)
        
        item_commands = registry.get_commands_by_category("items")
        assert len(item_commands) == 1
        assert item_commands[0].name == "new_item"

class TestCommandPalette:
    async def test_palette_display(self, app_test):
        """Test that the command palette displays correctly."""
        async with app_test() as pilot:
            # Open command palette
            await pilot.press("ctrl+p")
            # Check that palette is visible
            palette = pilot.app.query_one("#command_palette")
            assert palette.display
            
    async def test_palette_filtering(self, app_test):
        """Test that the command palette filters commands."""
        async with app_test() as pilot:
            # Open command palette
            await pilot.press("ctrl+p")
            palette = pilot.app.query_one("#command_palette")
            # Type search term
            await pilot.write("new")
            # Check that results are filtered
            results = palette.query("CommandResult")
            assert len(results) > 0
            assert all("new" in result.command.name.lower() for result in results)
```

## 5. DB Worker Thread Tests

### Unit Tests

```python
# tests/pos_tui/test_workers.py
import pytest
from textual.worker import Worker, WorkerState

from src.pos_tui.workers import DatabaseWorker, WorkerPool

class TestDatabaseWorker:
    async def test_worker_lifecycle(self, app_test):
        """Test the lifecycle of a database worker."""
        async with app_test() as pilot:
            # Create a worker
            worker = DatabaseWorker(
                "test_worker",
                lambda: pilot.app.work_system.get_work_items(),
                pilot.app
            )
            # Start worker
            worker_id = await pilot.app.run_worker(worker, "test_worker")
            # Wait for worker to complete
            await pilot.wait_for_worker(worker_id)
            # Check worker state
            assert worker.state == WorkerState.SUCCESS
            # Check worker result
            result = worker.result
            assert len(result) > 0
            
    async def test_worker_error_handling(self, app_test):
        """Test that worker errors are handled correctly."""
        async with app_test() as pilot:
            # Create a worker that will fail
            def failing_func():
                raise ValueError("Test error")
                
            worker = DatabaseWorker(
                "failing_worker",
                failing_func,
                pilot.app
            )
            # Start worker
            worker_id = await pilot.app.run_worker(worker, "failing_worker")
            # Wait for worker to complete
            await pilot.wait_for_worker(worker_id)
            # Check worker state
            assert worker.state == WorkerState.ERROR
            # Check that error was logged
            assert isinstance(worker.error, ValueError)
```

## Snapshot Tests

```python
# tests/pos_tui/test_snapshots.py
import pytest
from textual.app import App
from textual.snapshot import snapshot_tree

from src.pos_tui.app import POSTUI

class TestSnapshots:
    async def test_dashboard_snapshot(self, app_test):
        """Test that the dashboard appearance matches the snapshot."""
        async with app_test() as pilot:
            # Navigate to dashboard
            dashboard = pilot.app.query_one("DashboardScreen")
            # Take snapshot
            snapshot = await snapshot_tree(dashboard)
            # Compare with saved snapshot
            snapshot.compare("dashboard")
            
    async def test_item_form_snapshot(self, app_test):
        """Test that the item form appearance matches the snapshot."""
        async with app_test() as pilot:
            # Create and mount form
            from src.pos_tui.widgets.item_form import ItemEntryForm
            form = ItemEntryForm()
            await pilot.mount(form)
            # Take snapshot
            snapshot = await snapshot_tree(form)
            # Compare with saved snapshot
            snapshot.compare("item_form")
```

## Headless Integration Tests

```python
# tests/pos_tui/test_headless.py
import pytest
from textual.app import App
from textual.driver import Driver
from textual.events import Key

from src.pos_tui.app import POSTUI

class TestHeadlessIntegration:
    async def test_full_item_creation_flow(self, app_test, mock_work_system):
        """Test the full flow of creating a work item."""
        async with app_test() as pilot:
            # Navigate to New Item tab
            await pilot.press("2")  # Second tab
            
            # Fill out form
            await pilot.press("tab")  # Focus title field
            await pilot.write("Integration Test Item")
            
            await pilot.press("tab")  # Focus description
            await pilot.write("This is a test of the full item creation flow")
            
            await pilot.press("tab")  # Focus type selector
            await pilot.press("down")  # THOUGHT
            await pilot.press("enter")
            
            await pilot.press("tab")  # Focus priority
            await pilot.press("down")  # Medium
            await pilot.press("enter")
            
            # Submit form
            await pilot.press("ctrl+s")  # Save shortcut
            
            # Wait for operation to complete
            await pilot.wait_for_worker()
            
            # Verify item was created
            items = mock_work_system.get_work_items(type="THOUGHT")
            assert any(item.title == "Integration Test Item" for item in items)
            
            # Verify we're redirected to dashboard
            assert pilot.app.query_one("DashboardScreen")
            
    async def test_link_visualization_flow(self, app_test, mock_work_system):
        """Test the flow of visualizing linked items."""
        async with app_test() as pilot:
            # Navigate to Link Tree tab
            await pilot.press("3")  # Third tab
            
            # Enter item ID to visualize
            id_input = pilot.app.query_one("#item_id_input")
            await pilot.click(id_input)
            await pilot.write("ta1")
            
            # Press visualize button
            visualize_button = pilot.app.query_one("#visualize_button")
            await pilot.click(visualize_button)
            
            # Wait for tree to load
            await pilot.wait_for_worker()
            
            # Verify tree is displayed with correct root
            tree = pilot.app.query_one("LinkTree")
            assert tree.root.label == "Test Task"
            
            # Verify linked items are displayed
            assert any("Test Thought" in node.label for node in tree.nodes)
```

## Why These Tests Are Important

1. **Unit Tests** verify that individual components work correctly in isolation, enabling isolated debugging and incremental development.

2. **Integration Tests** ensure that components work correctly together, catching issues that might not appear in isolation.

3. **Snapshot Tests** help maintain visual consistency across changes, preventing unintended UI regressions.

4. **Headless Tests** validate complete user flows, ensuring the application works as a cohesive whole.

5. **Worker Thread Tests** specifically validate the asynchronous operations that are critical for a responsive TUI.

These tests will be particularly important as we transition from CLI to TUI, ensuring that all functionality is preserved while taking advantage of Textual's interactive capabilities. 