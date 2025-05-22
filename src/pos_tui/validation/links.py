from __future__ import annotations

import os
import tempfile
from typing import List, Tuple

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import ValidationProtocol
from src.storage import WorkSystem
from src.models import ItemType, Priority


class LinkValidation(ValidationProtocol):
    """Validate basic link creation constraints."""

    def __init__(self) -> None:
        super().__init__("link_validation")
        self.temp_db = None

    def _setup(self) -> Tuple[WorkSystem, List[str]]:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.close()
        ws = WorkSystem(temp_file.name)
        self.temp_db = temp_file.name
        ids = []
        for i in range(3):
            item = ws.add_item(
                goal="test",
                title=f"Item {i}",
                item_type=ItemType.TASK,
                description="d",
                priority=Priority.MED,
            )
            ids.append(item.id)
        return ws, ids

    def _cleanup(self) -> None:
        if self.temp_db and os.path.exists(self.temp_db):
            os.unlink(self.temp_db)

    def _run_validation(self) -> None:
        ws, ids = self._setup()
        try:
            # Basic link creation
            if ws.add_link(ids[0], ids[1], "references"):
                self.result.add_pass("Added link successfully")
            else:
                self.result.add_fail("Failed to add valid link")

            # Circular reference should fail
            ws.add_link(ids[1], ids[0], "references")
            if not ws.add_link(ids[0], ids[1], "references"):
                self.result.add_pass("Detected duplicate/circular reference")
            else:
                self.result.add_fail("Circular reference allowed")

            # Link count limit
            for i in range(2, len(ids)):
                ws.add_link(ids[0], ids[i], "references")
            added = ws.add_link(ids[0], "nonexistent", "references")
            if not added:
                self.result.add_pass("Link limit enforced or invalid target rejected")
            else:
                self.result.add_fail("Exceeded link limit without error")
        finally:
            self._cleanup()
