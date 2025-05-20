"""
Personal Organization System (POS) - A terminal-based task management system
"""

from .cli import WorkSystemCLI
from .models import ItemStatus, ItemType, Priority, WorkItem
from .storage import WorkSystem
from .pos_tui import POSTUI

__all__ = [
    "ItemType",
    "ItemStatus",
    "Priority",
    "WorkItem",
    "WorkSystem",
    "WorkSystemCLI",
    "POSTUI",
]

__version__ = "0.2.0"
