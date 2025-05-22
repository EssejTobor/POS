from __future__ import annotations

from pathlib import Path
from typing import Type

from . import ValidationProtocol
from .ui_components import UIComponentSimulator
from ..widgets.linked_items import LinkedItemsWidget
from ...storage import WorkSystem
from ...models import ItemType, Priority
import tempfile


class LinkedItemsWidgetValidation(ValidationProtocol):
    """Validation protocol for the LinkedItemsWidget."""

    def __init__(self) -> None:
        super().__init__("linked_items_widget")

    def _run_validation(self) -> None:
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.close()
            ws = WorkSystem(tmp.name)
            item_a = ws.add_item(
                goal="test",
                title="A1",
                item_type=ItemType.TASK,
                description="a",
                priority=Priority.MED,
            )
            item_b = ws.add_item(
                goal="test",
                title="B1",
                item_type=ItemType.TASK,
                description="b",
                priority=Priority.LOW,
            )
            ws.add_link(item_a.id, item_b.id, "references")

            simulator = UIComponentSimulator(
                LinkedItemsWidget,
                item_id=item_a.id,
                work_system=ws,
            )
            widget = simulator.instantiate()
            simulator.simulate_mount()
            if hasattr(widget, "refresh_links"):
                self.result.add_pass("Widget exposes refresh_links method")
            else:
                self.result.add_fail("refresh_links method missing")
        except Exception as e:
            self.result.add_fail(f"Widget validation failed: {e}")
        finally:
            try:
                import os
                os.unlink(tmp.name)
            except Exception:
                pass
