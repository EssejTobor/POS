"""
Theme management for the POS Textual UI.

Provides functions and classes for handling theme switching and customization.
"""

from enum import Enum, auto
from pathlib import Path
from typing import Dict, Optional

from textual.app import App


class ThemeType(Enum):
    """Types of themes available in the application."""
    DARK = auto()
    LIGHT = auto()


class ThemeManager:
    """Manager for handling theme switching and customization."""
    
    # Define theme colors
    THEMES = {
        ThemeType.DARK: {
            "primary": "#1976D2",
            "primary-darken-1": "#1565C0",
            "primary-darken-2": "#0D47A1",
            "primary-lighten-1": "#42A5F5",
            "accent": "#FF4081",
            "accent-darken-1": "#F50057",
            "accent-lighten-1": "#FF80AB",
            "background": "#121212",
            "surface": "#1E1E1E",
            "error": "#CF6679",
            "on-primary": "#FFFFFF",
            "on-secondary": "#000000",
            "on-background": "#FFFFFF",
            "on-surface": "#FFFFFF",
            "on-error": "#000000",
            "panel": "#252525",
            "panel-darken-1": "#1C1C1C",
            "text": "#FFFFFF",
            "text-muted": "#AAAAAA",
            "boost": "#2C2C2C",
            "warning": "#FFC107",
            "success": "#4CAF50",
        },
        ThemeType.LIGHT: {
            "primary": "#2196F3",
            "primary-darken-1": "#1976D2",
            "primary-darken-2": "#0D47A1",
            "primary-lighten-1": "#64B5F6",
            "accent": "#FF4081",
            "accent-darken-1": "#F50057",
            "accent-lighten-1": "#FF80AB",
            "background": "#FAFAFA",
            "surface": "#FFFFFF",
            "error": "#B00020",
            "on-primary": "#FFFFFF",
            "on-secondary": "#000000",
            "on-background": "#000000",
            "on-surface": "#000000",
            "on-error": "#FFFFFF",
            "panel": "#F5F5F5",
            "panel-darken-1": "#EEEEEE",
            "text": "#000000",
            "text-muted": "#666666",
            "boost": "#E0E0E0",
            "warning": "#FF9800",
            "success": "#4CAF50",
        }
    }
    
    def __init__(self, app: App) -> None:
        """Initialize the theme manager.
        
        Args:
            app: The Textual application instance
        """
        self.app = app
        self.current_theme = ThemeType.DARK  # Default to dark theme
        self._theme_css_path = Path(__file__).parent / "theme_custom.css"
        
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self.current_theme == ThemeType.DARK:
            self.set_theme(ThemeType.LIGHT)
        else:
            self.set_theme(ThemeType.DARK)
    
    def set_theme(self, theme_type: ThemeType) -> None:
        """Set the application theme.
        
        Args:
            theme_type: The theme type to set
        """
        if theme_type == self.current_theme:
            return
            
        self.current_theme = theme_type
        
        # Generate CSS variables for the theme
        self._generate_theme_css()
        
        # Reload the application styling
        self.app.refresh_css()
        
    def _generate_theme_css(self) -> None:
        """Generate a CSS file with theme variables."""
        theme_colors = self.THEMES[self.current_theme]
        
        css_content = ":root {\n"
        
        # Add each color as a CSS variable
        for name, color in theme_colors.items():
            css_content += f"    --{name}: {color};\n"
            
        css_content += "}\n"
        
        # Write the CSS file
        self._theme_css_path.write_text(css_content)
        
    def get_current_theme(self) -> ThemeType:
        """Get the current theme.
        
        Returns:
            The current theme type
        """
        return self.current_theme 