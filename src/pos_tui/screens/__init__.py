"""
Screens for the POS Textual UI.

This module contains the main screens used in the POS application.
"""

# Import screens as they are implemented
from .dashboard import DashboardScreen
from .link_tree import LinkTreeScreen
from .new_item import NewItemScreen
from .detail import ItemDetailScreen

__all__: list[str] = [
    "DashboardScreen",
    "NewItemScreen",
    "LinkTreeScreen",
    "ItemDetailScreen",
]
