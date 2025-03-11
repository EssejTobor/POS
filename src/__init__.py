"""
Personal Operating System (POS) - A Textual-based TUI application for personal knowledge management and task tracking
"""

from .models import ItemType, ItemStatus, Priority, WorkItem, ThoughtNode, ThoughtStatus, BranchType
from .app import POSApp
from .config import Config
from .thought_manager import ThoughtManager

__version__ = "0.2.0" 