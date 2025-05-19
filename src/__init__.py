"""
Personal Organization System (POS) - A command-line task management system
"""

from .cli import WorkSystemCLI
from .models import ItemStatus, ItemType, Priority, WorkItem
from .storage import WorkSystem

__all__ = [
    "ItemType",
    "ItemStatus",
    "Priority",
    "WorkItem",
    "WorkSystem",
    "WorkSystemCLI",
]

__version__ = "0.1.0"
