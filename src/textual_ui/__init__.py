"""
Custom widgets and components for the Textual UI for Personal Operating System (POS).

This module contains specialized widgets that enhance the user experience in the TUI.
"""

# Import the widgets from the local package
from .widgets import (
    CommandPalette,
    ConfirmationDialog,
    ExpandableThoughtTree,
    ProgressIndicator,
    SearchInput,
    Sidebar,
    StatusBar,
    TEXTUAL_AVAILABLE,
)

# Import TextualApp directly from the parent module to avoid circular imports
import sys
import importlib.util

if importlib.util.find_spec("textual") is not None:
    # If textual is installed, import the app from the parent module
    from .. import textual_ui
    TextualApp = textual_ui.TextualApp
else:
    # Define a stub if textual is not available
    class TextualApp:
        def __init__(self, *args, **kwargs):
            pass
        
        def run(self):
            print("Textual UI is not available. Please install textual: pip install textual")

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
