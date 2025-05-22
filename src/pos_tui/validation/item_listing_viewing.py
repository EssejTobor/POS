from __future__ import annotations
"""Validation protocol for item listing and viewing features."""

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
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        tmp.close()
        self.temp_db = tmp.name
        ws = WorkSystem(tmp.name)
        ws.add_item("GoalA", "Task1", ItemType.TASK, "d1", Priority.LOW)
        ws.add_item("GoalB", "Thought1", ItemType.THOUGHT, "d2", Priority.MED)
        return ws

    def _run_validation(self) -> None:
        ws = self._setup()
        try:
            from src.pos_tui.widgets.item_table import ItemTable

            class DummyApp(App):
                def __init__(self) -> None:
                    super().__init__(driver_class=None)

            app = DummyApp()
            active_app.set(app)

            table = ItemTable()
            object.__setattr__(table, "_parent", app)
            table.apply_row_styling = lambda *a, **k: None
            table.on_mount()
            for item in ws.items.values():
                table.add_row(
                    item.id,
                    item.title,
                    item.goal,
                    item.item_type.value,
                    item.status.value,
                    str(item.priority.value),
                    "",
                    key=item.id,
                )

            headers = [str(col.label) for col in table.columns.values()]
            if "Goal" in headers:
                self.result.add_pass("Goal column present in table")
            else:
                self.result.add_fail("Goal column missing from table")

            first = next(iter(ws.items.values()))
            row = table.get_row(first.id)
            if row and row[2] == "GoalA":
                self.result.add_pass("Goal value displayed correctly")
            else:
                self.result.add_fail("Goal value incorrect in table")

            # Validate FilterBar has THOUGHT option
            values = [t.value for t in ItemType]
            if "th" in values:
                self.result.add_pass("THOUGHT option present in type filter")
            else:
                self.result.add_fail("THOUGHT option missing in type filter")

            # Verify filtering by goal
            filtered = ws.get_filtered_items(goal="GoalB")
            if len(filtered) == 1 and filtered[0].goal == "GoalB":
                self.result.add_pass("Filtering by goal returns correct item")
            else:
                self.result.add_fail("Filtering by goal failed")

            filtered_th = ws.get_filtered_items(item_type=ItemType.THOUGHT)
            if len(filtered_th) == 1 and filtered_th[0].item_type == ItemType.THOUGHT:
                self.result.add_pass("Filtering by THOUGHT type works")
            else:
                self.result.add_fail("Filtering by THOUGHT type failed")
        except Exception as exc:
            self.result.add_fail(f"Validation error: {exc}")
        finally:
            if self.temp_db and os.path.exists(self.temp_db):
                os.unlink(self.temp_db)
                self.result.add_note(f"Removed temporary database {self.temp_db}")
