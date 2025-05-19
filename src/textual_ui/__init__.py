"""
Custom widgets and components for the Textual UI for Personal Operating System (POS).

This module contains specialized widgets that enhance the user experience in the TUI.
"""

# Import the widgets from the local package
from __future__ import annotations

from importlib import util as importlib_util
from pathlib import Path

from .widgets import (
    TEXTUAL_AVAILABLE,
    CommandPalette,
    ConfirmationDialog,
    ExpandableThoughtTree,
    ProgressIndicator,
    SearchInput,
    Sidebar,
    StatusBar,
)

# Lazily load ``TextualApp`` from the sibling module ``textual_ui.py``.  Using
# ``spec_from_file_location`` avoids importing this package again during
# initialisation, which previously triggered a circular import error.
_mod_path = Path(__file__).resolve().parents[1] / "textual_ui.py"

if _mod_path.exists():
    spec = importlib_util.spec_from_file_location("_textual_ui", _mod_path)
    assert spec and spec.loader  # for mypy
    _module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(_module)
    TextualApp = _module.TextualApp
    TEXTUAL_AVAILABLE = _module.TEXTUAL_AVAILABLE
else:  # pragma: no cover - defensive fallback

    class TextualApp:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            pass

        def run(self) -> None:
            print(
                "Textual UI is not available. Please install textual: pip install textual"
            )


__all__ = [
    "CommandPalette",
    "ConfirmationDialog",
    "ExpandableThoughtTree",
    "ProgressIndicator",
    "SearchInput",
    "Sidebar",
    "StatusBar",
    "TEXTUAL_AVAILABLE",
    "TextualApp",
]
