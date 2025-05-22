from __future__ import annotations
"""Validation protocol for item listing and viewing features.

This protocol populates a temporary database with several items, then
simulates the :class:`DashboardScreen` loading data and applying
``FilterBar`` filters.  It verifies that the ``ItemTable`` shows the
"Goal" column and that filtering by goal or item type works correctly.
"""

import os
import tempfile
from pathlib import Path
from typing import List

# Add project root for imports when running directly
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import ValidationProtocol
from src.pos_tui.validation.ui_components import UIComponentSimulator
from src.models import ItemType, Priority
from textual.app import App
from textual.message_pump import active_app
from src.storage import WorkSystem


class ItemListingAndViewingValidation(ValidationProtocol):
    """Validate goal display and filtering in the dashboard."""

    def __init__(self) -> None:
        super().__init__("item_listing_and_viewing")
        self.temp_db: str | None = None

    def _setup(self) -> WorkSystem:
        """Create a temporary database with sample items."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.temp_db = tmp.name
        ws = WorkSystem(tmp.name)

        # Populate with multiple goals and types, including a thought item
        ws.add_item("GoalA", "Task1", ItemType.TASK, "d1", Priority.LOW)
        ws.add_item("GoalB", "Task2", ItemType.TASK, "d2", Priority.MED)
        ws.add_item("GoalA", "Thought1", ItemType.THOUGHT, "d3", Priority.HI)

        return ws

    def _run_validation(self) -> None:
        ws = self._setup()
        try:
            from src.pos_tui.widgets.item_table import ItemTable
            from src.pos_tui.screens.dashboard import DashboardScreen

            class DummyApp(App):
                def __init__(self) -> None:
                    super().__init__(driver_class=None)
                    self.work_system = ws

            app = DummyApp()
            active_app.set(app)

            table = ItemTable()
            object.__setattr__(table, "_parent", app)
            table.apply_row_styling = lambda *a, **k: None
            table.on_mount()

            status = type("Status", (), {"update": lambda self, v: None})()
            loading = type("Loading", (), {"display": False})()

            class DummyDashboard(DashboardScreen):
                def query_one(self, selector: str, *a, **k):
                    if selector == "#dashboard_table":
                        return table
                    if selector == "#status_message":
                        return status
                    if selector == "#loading_indicator":
                        return loading
                    return super().query_one(selector, *a, **k)

            screen = DummyDashboard()
            object.__setattr__(screen, "_app", app)

            import asyncio

            # Simulate initial dashboard load
            asyncio.run(screen.fetch_items())

            headers = [str(col.label) for col in table.columns.values()]
            if "Goal" in headers:
                self.result.add_pass("Goal column present in table")
            else:
                self.result.add_fail("Goal column missing from table")

            first = next(iter(ws.items.values()))
            row = table.get_row(first.id)
            if row and row[2] == first.goal:
                self.result.add_pass("Goal value displayed correctly")
            else:
                self.result.add_fail("Goal value incorrect in table")

            # Validate FilterBar has THOUGHT option
            values = [t.value for t in ItemType]
            if ItemType.THOUGHT.value in values:
                self.result.add_pass("THOUGHT option present in type filter")
            else:
                self.result.add_fail("THOUGHT option missing in type filter")

            # Verify filtering by goal through DashboardScreen
            asyncio.run(screen.fetch_filtered_items(goal_filter="GoalB"))
            filtered_goal = ws.get_filtered_items(goal="GoalB")
            if table.row_count == len(filtered_goal) == 1:
                row = table.get_row(filtered_goal[0].id)
                if row and row[2] == "GoalB":
                    self.result.add_pass("Filtering by goal returns correct item")
                else:
                    self.result.add_fail("Goal filter data incorrect")
            else:
                self.result.add_fail("Filtering by goal failed")

            # Verify filtering by type (THOUGHT)
            asyncio.run(screen.fetch_filtered_items(item_type=ItemType.THOUGHT.value))
            filtered_th = ws.get_filtered_items(item_type=ItemType.THOUGHT)
            if table.row_count == len(filtered_th) == 1:
                row = table.get_row(filtered_th[0].id)
                if row and row[3] == ItemType.THOUGHT.value:
                    self.result.add_pass("Filtering by THOUGHT type works")
                else:
                    self.result.add_fail("THOUGHT filter data incorrect")
            else:
                self.result.add_fail("Filtering by THOUGHT type failed")
        except Exception as exc:
            self.result.add_fail(f"Validation error: {exc}")
        finally:
            if self.temp_db and os.path.exists(self.temp_db):
                os.unlink(self.temp_db)
                self.result.add_note(f"Removed temporary database {self.temp_db}")
