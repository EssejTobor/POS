"""
Screens package for the Personal Operating System TUI.
Contains all screen classes for the application.
"""

from .base_screen import BaseScreen
from .dashboard import DashboardScreen
from .work_items import WorkItemScreen
from .thought_screen import ThoughtScreen
from .settings import SettingsScreen
from .error_screen import ErrorScreen

__all__ = [
    'BaseScreen',
    'DashboardScreen',
    'WorkItemScreen',
    'ThoughtScreen',
    'SettingsScreen',
    'ErrorScreen'
] 