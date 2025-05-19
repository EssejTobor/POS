"""
Custom widgets and components for the Textual UI for Personal Operating System (POS).

This module contains specialized widgets that enhance the user experience in the TUI.
"""

from importlib import import_module

# Re-export the ``TEXTUAL_AVAILABLE`` flag and ``TextualApp`` class from the
# sibling module ``textual_ui.py``.  Having a package and a module with the same
# name can lead to confusion when importing; explicitly re-exporting here
# ensures ``from src.textual_ui import TEXTUAL_AVAILABLE`` works as intended.
from .widgets import (
    CommandPalette,
    ConfirmationDialog,
    ExpandableThoughtTree,
    ProgressIndicator,
    SearchInput,
    Sidebar,
    StatusBar,
)

_mod = import_module("src.textual_ui")
TEXTUAL_AVAILABLE = _mod.TEXTUAL_AVAILABLE
TextualApp = _mod.TextualApp

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
