"""
Notification system for the POS Textual UI.

Provides widgets for displaying error messages, success notifications, and warnings.
"""

import asyncio
from enum import Enum, auto
from typing import Callable, Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Static


class NotificationType(Enum):
    """Types of notifications that can be displayed."""
    ERROR = auto()
    WARNING = auto()
    SUCCESS = auto()
    INFO = auto()


class Notification(Container):
    """A notification widget that can be displayed and dismissed."""
    
    DEFAULT_CSS = """
    Notification {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        padding: 1;
        border: solid $primary;
        dock: top;
    }
    
    Notification.error {
        background: $error-darken-3;
        border: solid $error;
        color: $error;
    }
    
    Notification.warning {
        background: $warning-darken-3;
        border: solid $warning;
        color: $warning;
    }
    
    Notification.success {
        background: $success-darken-3;
        border: solid $success;
        color: $success;
    }
    
    Notification.info {
        background: $primary-darken-3;
        border: solid $primary;
        color: $primary;
    }
    
    .notification-message {
        width: 1fr;
    }
    
    .notification-close {
        dock: right;
    }
    """
    
    # Notification message
    message = reactive("")
    
    # Notification type
    notification_type = reactive(NotificationType.INFO)
    
    # Auto-dismiss timer (in seconds, None for no auto-dismiss)
    auto_dismiss = reactive(5.0)
    
    class Dismissed(Message):
        """Message sent when notification is dismissed."""
        
        def __init__(self, notification: "Notification") -> None:
            self.notification = notification
            super().__init__()
    
    def __init__(
        self, 
        message: str, 
        notification_type: NotificationType = NotificationType.INFO,
        auto_dismiss: Optional[float] = 5.0,
        *args, 
        **kwargs
    ) -> None:
        """Initialize the notification.
        
        Args:
            message: The notification message
            notification_type: The type of notification
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
        """
        super().__init__(*args, **kwargs)
        self.message = message
        self.notification_type = notification_type
        self.auto_dismiss = auto_dismiss
        self._dismiss_task = None
    
    def compose(self) -> ComposeResult:
        """Compose the notification widget."""
        yield Static(self.message, classes="notification-message")
        yield Button("×", classes="notification-close")
    
    def on_mount(self) -> None:
        """Handle the widget being mounted in the DOM."""
        # Add the appropriate class based on notification type
        type_class = self.notification_type.name.lower()
        self.add_class(type_class)
        
        # Set up auto-dismiss if enabled
        if self.auto_dismiss is not None and self.auto_dismiss > 0:
            self._dismiss_task = asyncio.create_task(self._auto_dismiss())
    
    async def _auto_dismiss(self) -> None:
        """Automatically dismiss the notification after a delay."""
        await asyncio.sleep(self.auto_dismiss)
        self.dismiss()
    
    def dismiss(self) -> None:
        """Dismiss the notification."""
        # Cancel auto-dismiss task if it exists
        if self._dismiss_task is not None:
            self._dismiss_task.cancel()
            self._dismiss_task = None
            
        # Post dismissed message
        self.post_message(self.Dismissed(self))
        
        # Remove from parent
        self.remove()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if "notification-close" in event.button.classes:
            self.dismiss()
            

class NotificationCenter(Container):
    """Container for displaying notifications."""
    
    DEFAULT_CSS = """
    NotificationCenter {
        width: 60;
        margin: 1 0;
        dock: top;
        layer: notification;
        height: auto;
    }
    """
    
    def notify(
        self, 
        message: str, 
        notification_type: NotificationType = NotificationType.INFO,
        auto_dismiss: Optional[float] = 5.0,
    ) -> Notification:
        """Show a notification.
        
        Args:
            message: The notification message
            notification_type: The type of notification
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
            
        Returns:
            The created notification widget
        """
        notification = Notification(
            message, 
            notification_type=notification_type,
            auto_dismiss=auto_dismiss
        )
        self.mount(notification)
        return notification
    
    def error(self, message: str, auto_dismiss: Optional[float] = 8.0) -> Notification:
        """Show an error notification.
        
        Args:
            message: The error message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
            
        Returns:
            The created notification widget
        """
        return self.notify(message, NotificationType.ERROR, auto_dismiss)
    
    def warning(self, message: str, auto_dismiss: Optional[float] = 5.0) -> Notification:
        """Show a warning notification.
        
        Args:
            message: The warning message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
            
        Returns:
            The created notification widget
        """
        return self.notify(message, NotificationType.WARNING, auto_dismiss)
    
    def success(self, message: str, auto_dismiss: Optional[float] = 3.0) -> Notification:
        """Show a success notification.
        
        Args:
            message: The success message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
            
        Returns:
            The created notification widget
        """
        return self.notify(message, NotificationType.SUCCESS, auto_dismiss)
    
    def info(self, message: str, auto_dismiss: Optional[float] = 5.0) -> Notification:
        """Show an info notification.
        
        Args:
            message: The info message
            auto_dismiss: Time in seconds before auto-dismissing (None for no auto-dismiss)
            
        Returns:
            The created notification widget
        """
        return self.notify(message, NotificationType.INFO, auto_dismiss) 