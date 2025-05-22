"""
Standalone test script for the LinkTreeScreen.

This script runs the LinkTreeScreen component in isolation
to test the tree visualization features.
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from textual.app import App

from src.pos_tui.screens.link_tree import LinkTreeScreen


class LinkTreeTestApp(App):
    """Test application for the LinkTreeScreen."""
    
    def __init__(self):
        """Initialize the test application."""
        super().__init__()
    
    def compose(self):
        """Compose the app with the LinkTreeScreen."""
        yield LinkTreeScreen()


if __name__ == "__main__":
    app = LinkTreeTestApp()
    app.run() 