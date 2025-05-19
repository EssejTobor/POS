"""
Personal Organization System (POS) - A command-line task management system
"""

from .models import ItemType, ItemStatus, Priority, WorkItem
from .storage import WorkSystem
from .cli import WorkSystemCLI

__version__ = "0.1.0"
