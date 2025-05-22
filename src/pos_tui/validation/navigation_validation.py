"""
Validation for navigation and usability features.

This module provides validation protocols for testing command palette,
keyboard shortcuts, theme switching, and notifications.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple

from textual.app import App

from ...models import ItemStatus, ItemType, Priority
from ..app import POSTUI
from ..widgets import CommandPalette, NotificationCenter
from ..styles.theme import ThemeType


class NavigationValidator:
    """Validator for navigation and usability features."""
    
    def __init__(self, app: POSTUI) -> None:
        """Initialize the validator.
        
        Args:
            app: The POSTUI application instance
        """
        self.app = app
        self.results: Dict[str, Tuple[bool, str]] = {}
        
    async def validate_command_palette(self) -> bool:
        """Validate command palette functionality.
        
        Returns:
            True if validation passes, False otherwise
        """
        try:
            command_palette = self.app.query_one("#command_palette", CommandPalette)
            
            # Check command registration
            if not command_palette.commands:
                self.results["command_palette_registration"] = (False, "No commands registered")
                return False
                
            # Test command palette visibility
            if command_palette._visible:
                self.results["command_palette_initial_state"] = (False, "Command palette should be hidden initially")
                return False
                
            # Show command palette
            self.app.action_toggle_command_palette()
            await asyncio.sleep(0.1)
            
            if not command_palette._visible:
                self.results["command_palette_toggle_show"] = (False, "Command palette did not show")
                return False
                
            # Hide command palette
            self.app.action_toggle_command_palette()
            await asyncio.sleep(0.1)
            
            if command_palette._visible:
                self.results["command_palette_toggle_hide"] = (False, "Command palette did not hide")
                return False
                
            # Test search functionality
            self.app.action_toggle_command_palette()
            await asyncio.sleep(0.1)
            
            # Simulate search input
            search_input = command_palette.query_one("#search_input")
            search_input.value = "theme"
            await asyncio.sleep(0.1)
            
            # Check filtered commands
            if not command_palette._filtered_commands:
                self.results["command_palette_search"] = (False, "Search did not return any results")
                return False
                
            # Hide command palette
            self.app.action_toggle_command_palette()
            
            self.results["command_palette"] = (True, "Command palette validation passed")
            return True
            
        except Exception as e:
            self.results["command_palette"] = (False, f"Command palette validation failed: {str(e)}")
            return False
            
    async def validate_theme_switching(self) -> bool:
        """Validate theme switching functionality.
        
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Get initial theme
            initial_theme = self.app.theme_manager.current_theme
            
            # Toggle theme
            self.app.action_toggle_theme()
            await asyncio.sleep(0.1)
            
            # Check if theme changed
            if self.app.theme_manager.current_theme == initial_theme:
                self.results["theme_toggle"] = (False, "Theme did not change after toggle")
                return False
                
            # Toggle back
            self.app.action_toggle_theme()
            await asyncio.sleep(0.1)
            
            # Check if theme reverted
            if self.app.theme_manager.current_theme != initial_theme:
                self.results["theme_revert"] = (False, "Theme did not revert after second toggle")
                return False
                
            # Test explicit theme setting
            self.app.theme_manager.set_theme(ThemeType.LIGHT)
            await asyncio.sleep(0.1)
            
            if self.app.theme_manager.current_theme != ThemeType.LIGHT:
                self.results["theme_explicit_set"] = (False, "Failed to explicitly set light theme")
                return False
                
            # Reset to initial theme
            self.app.theme_manager.set_theme(initial_theme)
            
            self.results["theme_switching"] = (True, "Theme switching validation passed")
            return True
            
        except Exception as e:
            self.results["theme_switching"] = (False, f"Theme switching validation failed: {str(e)}")
            return False
            
    async def validate_notifications(self) -> bool:
        """Validate notification system functionality.
        
        Returns:
            True if validation passes, False otherwise
        """
        try:
            notification_center = self.app.query_one("#notification_center", NotificationCenter)
            
            # Test info notification
            self.app.notify_info("Test info notification", auto_dismiss=0.5)
            await asyncio.sleep(0.1)
            
            notifications = notification_center.query("Notification")
            if not notifications:
                self.results["notification_creation"] = (False, "Info notification was not created")
                return False
                
            # Wait for auto-dismiss
            await asyncio.sleep(0.6)
            
            notifications = notification_center.query("Notification")
            if notifications:
                self.results["notification_auto_dismiss"] = (False, "Notification did not auto-dismiss")
                return False
                
            # Test all notification types
            self.app.notify_error("Test error notification", auto_dismiss=None)
            self.app.notify_warning("Test warning notification", auto_dismiss=None)
            self.app.notify_success("Test success notification", auto_dismiss=None)
            await asyncio.sleep(0.1)
            
            notifications = notification_center.query("Notification")
            if len(notifications) != 3:
                self.results["notification_types"] = (False, f"Expected 3 notifications, got {len(notifications)}")
                return False
                
            # Manually dismiss notifications
            for notification in list(notifications):
                notification.dismiss()
            
            await asyncio.sleep(0.1)
            
            notifications = notification_center.query("Notification")
            if notifications:
                self.results["notification_manual_dismiss"] = (False, "Notifications did not dismiss manually")
                return False
                
            self.results["notifications"] = (True, "Notifications validation passed")
            return True
            
        except Exception as e:
            self.results["notifications"] = (False, f"Notifications validation failed: {str(e)}")
            return False
            
    async def validate_keyboard_shortcuts(self) -> bool:
        """Validate keyboard shortcut functionality.
        
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Test tab switching
            tabs = self.app.query_one("#tabs")
            
            # Initial tab should be dashboard
            if tabs.active != "dashboard":
                self.results["keyboard_initial_tab"] = (False, f"Initial tab is {tabs.active}, expected dashboard")
                return False
                
            # Press 2 to switch to new-item
            self.app.action_switch_tab("new-item")
            await asyncio.sleep(0.1)
            
            if tabs.active != "new-item":
                self.results["keyboard_tab_switch"] = (False, f"Tab did not switch to new-item, still at {tabs.active}")
                return False
                
            # Press 1 to switch back to dashboard
            self.app.action_switch_tab("dashboard")
            await asyncio.sleep(0.1)
            
            if tabs.active != "dashboard":
                self.results["keyboard_tab_switch_back"] = (False, f"Tab did not switch back to dashboard, at {tabs.active}")
                return False
                
            # Test shortcuts screen
            self.app.action_show_shortcuts()
            await asyncio.sleep(0.1)
            
            # Check if shortcuts screen is shown
            shortcuts_screen = self.app.screen
            if "ShortcutsScreen" not in str(type(shortcuts_screen)):
                self.results["keyboard_shortcuts_screen"] = (False, "Shortcuts screen was not shown")
                return False
                
            # Pop screen to return to main app
            self.app.pop_screen()
            await asyncio.sleep(0.1)
            
            self.results["keyboard_shortcuts"] = (True, "Keyboard shortcuts validation passed")
            return True
            
        except Exception as e:
            self.results["keyboard_shortcuts"] = (False, f"Keyboard shortcuts validation failed: {str(e)}")
            return False
    
    async def run_all_validations(self) -> Dict[str, Tuple[bool, str]]:
        """Run all validation tests.
        
        Returns:
            Dictionary of test results with test names as keys and (success, message) tuples as values
        """
        # Reset results
        self.results = {}
        
        # Run validations
        await self.validate_command_palette()
        await self.validate_theme_switching()
        await self.validate_notifications()
        await self.validate_keyboard_shortcuts()
        
        return self.results
        
    def print_results(self) -> None:
        """Print validation results to console."""
        print("\n=== Navigation and Usability Validation Results ===\n")
        
        passed = 0
        failed = 0
        
        for test_name, (success, message) in self.results.items():
            status = "PASS" if success else "FAIL"
            print(f"{status}: {test_name} - {message}")
            
            if success:
                passed += 1
            else:
                failed += 1
                
        print(f"\nSummary: {passed} passed, {failed} failed\n")


async def run_validation(app: POSTUI) -> Dict[str, Tuple[bool, str]]:
    """Run navigation validation on the provided app.
    
    Args:
        app: The POSTUI application instance
        
    Returns:
        Dictionary of test results
    """
    validator = NavigationValidator(app)
    results = await validator.run_all_validations()
    validator.print_results()
    return results


if __name__ == "__main__":
    """Run standalone validation."""
    app = POSTUI()
    
    async def run_tests():
        await run_validation(app)
        app.exit()
        
    app.run(run_tests()) 