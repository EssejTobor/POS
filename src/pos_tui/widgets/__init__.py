"""
Widgets for the POS Textual UI application.

This package contains all the custom widgets used in the TUI.
"""

# Import widgets as they are implemented
from .item_table import ItemTable
from .item_form import ItemEntryForm
from .item_details import LinkedItemsWidget, ItemDetailsModal
from .modals import EditItemModal
from .filter_bar import FilterBar
from .link_tree import LinkTree, LinkTreeControls
from .command_palette import CommandPalette, CommandItem
from .notifications import Notification, NotificationCenter, NotificationType

# from .message import Message

__all__: list[str] = [
    "ItemTable",
    "ItemEntryForm",
    "LinkedItemsWidget",
    "ItemDetailsModal",
    "EditItemModal",
    "FilterBar",
    "LinkTree",
    "LinkTreeControls",
    "CommandPalette",
    "CommandItem",
    "Notification",
    "NotificationCenter",
    "NotificationType"
    # "Message",
]
