from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import ValidationProtocol
from src.pos_tui.app import POSTUI
from src.storage import WorkSystem
from src.models import ItemType, Priority


class NavigationValidation(ValidationProtocol):
    """Validate breadcrumb history navigation."""

    def __init__(self) -> None:
        super().__init__("navigation_validation")

    def _run_validation(self) -> None:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        ws = WorkSystem(tmp.name)
        a = ws.add_item("g", "A1", ItemType.TASK, "a", Priority.MED)
        b = ws.add_item("g", "B1", ItemType.TASK, "b", Priority.MED)
        c = ws.add_item("g", "C1", ItemType.TASK, "c", Priority.MED)
        ws.add_link(a.id, b.id, "parent-child")
        ws.add_link(b.id, c.id, "parent-child")

        app = POSTUI()
        app.work_system = ws

        app.register_detail(a)
        if app.breadcrumb_history and app.breadcrumb_history[-1].id == a.id:
            self.result.add_pass("A registered in history")
        else:
            self.result.add_fail("A not registered")

        app.register_detail(b)
        if app.breadcrumb_history[-1].id == b.id and len(app.breadcrumb_history) == 2:
            self.result.add_pass("History updated with B")
        else:
            self.result.add_fail("History did not update for B")

        app.unregister_detail(b)
        if app.breadcrumb_history[-1].id == a.id:
            self.result.add_pass("History popped on unmount")
        else:
            self.result.add_fail("History not popped")

        import os
        os.unlink(tmp.name)

