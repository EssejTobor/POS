from __future__ import annotations
"""User preference persistence helpers."""

import json
from pathlib import Path
from typing import Any, Dict

# Path to the preferences file within the repository
PREF_FILE = Path(__file__).resolve().parents[2] / "data" / "preferences.json"


def load_preferences(path: Path | None = None) -> Dict[str, Any]:
    """Load preferences from ``path`` or the default location."""
    pref_path = path or PREF_FILE
    if pref_path.is_file():
        try:
            return json.loads(pref_path.read_text())
        except Exception:
            return {}
    return {}


def save_preferences(prefs: Dict[str, Any], path: Path | None = None) -> None:
    """Save ``prefs`` to ``path`` or the default location."""
    pref_path = path or PREF_FILE
    pref_path.parent.mkdir(parents=True, exist_ok=True)
    pref_path.write_text(json.dumps(prefs, indent=2))
