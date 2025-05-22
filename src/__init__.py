"""
Personal Organization System (POS) - A terminal-based task management system
"""

from .cli import WorkSystemCLI
from .models import ItemStatus, ItemType, LinkType, Priority, WorkItem
from .pos_tui import POSTUI
from .storage import WorkSystem

__all__ = [
    "ItemType",
    "ItemStatus",
    "LinkType",
    "Priority",
    "WorkItem",
    "WorkSystem",
    "WorkSystemCLI",
    "POSTUI",
]

__version__ = "0.4.0"
