from __future__ import annotations

from pathlib import Path
import tempfile

from src.pos_tui.preferences import load_preferences, save_preferences
from src.pos_tui.validation import ValidationProtocol


class UsabilityValidation(ValidationProtocol):
    """Validate preference persistence utilities."""

    def __init__(self) -> None:
        super().__init__("usability")

    def _run_validation(self) -> None:
        tmp = Path(tempfile.NamedTemporaryFile(delete=False).name)
        prefs = {"filters": {"item_type": "TASK", "status": "IN_PROGRESS", "search_text": "foo"}, "theme": "light"}
        save_preferences(prefs, path=tmp)
        loaded = load_preferences(path=tmp)
        if loaded == prefs:
            self.result.add_pass("Preferences round trip works")
        else:
            self.result.add_fail("Preferences not persisted correctly")
        tmp.unlink(missing_ok=True)
