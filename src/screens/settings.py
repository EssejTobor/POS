from textual.widgets import Static, Button, Switch, Label, Input
from textual.containers import Container, VerticalScroll
from textual import events
from textual.app import ComposeResult
import logging
import os
from pathlib import Path
from datetime import datetime

from .base_screen import BaseScreen
from ..database import Database
from ..migrations import SchemaMigrator
from ..backup import BackupManager
from ..config import Config

logger = logging.getLogger(__name__)

class SettingsScreen(BaseScreen):
    """Settings and configuration screen"""
    
    def __init__(self):
        super().__init__()
        self.db = Database(Config.DB_PATH)
        self.backup_manager = BackupManager(os.path.basename(Config.DB_PATH))
        logger.info("Settings screen initialized")
    
    def compose(self) -> ComposeResult:
        """Compose the settings screen layout"""
        yield Container(
            Static("Settings", classes="title"),
            
            # Appearance settings
            Container(
                Static("Appearance", classes="section-title"),
                Container(
                    Static("Dark Mode:", classes="setting-label"),
                    Switch(value=Config.DARK_MODE_DEFAULT, id="dark-mode-switch"),
                    id="dark-mode-setting"
                ),
                id="appearance-settings"
            ),
            
            # Database settings
            Container(
                Static("Database", classes="section-title"),
                Static(f"Database Path: {Config.DB_PATH}", id="db-path"),
                Container(
                    Button("Run Migrations", id="run-migrations"),
                    Button("Vacuum Database", id="vacuum-db"),
                    Button("Backup Database", id="backup-db"),
                    classes="button-row"
                ),
                id="database-settings"
            ),
            
            # Data Export/Import
            Container(
                Static("Data Export/Import", classes="section-title"),
                Container(
                    Button("Export to JSON", id="export-json"),
                    Button("Import from JSON", id="import-json"),
                    classes="button-row"
                ),
                Static("No current operation", id="export-import-status"),
                id="export-import-settings"
            ),
            
            # About section
            Container(
                Static("About", classes="section-title"),
                Static(f"Personal Operating System v{Config.APP_VERSION}", id="app-version"),
                Static("A personal knowledge and task management system", id="app-description"),
                id="about-section"
            ),
            id="settings"
        )
    
    def on_mount(self):
        """Initialize settings when screen is mounted"""
        # Set dark mode switch to match app's current dark mode setting
        self.query_one("#dark-mode-switch").value = self.app.dark
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes"""
        if event.switch.id == "dark-mode-switch":
            self.app.dark = event.value
            logger.info(f"Dark mode set to {event.value}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        try:
            if button_id == "run-migrations":
                self.run_migrations()
            elif button_id == "vacuum-db":
                self.vacuum_database()
            elif button_id == "backup-db":
                self.backup_database()
            elif button_id == "export-json":
                self.export_to_json()
            elif button_id == "import-json":
                self.show_import_dialog()
        except Exception as e:
            logger.error(f"Error handling button press: {e}", exc_info=True)
            self.show_error(f"Error: {str(e)}")
    
    def run_migrations(self):
        """Run database migrations"""
        try:
            migrator = SchemaMigrator(Config.DB_PATH)
            migrations_applied = migrator.run_migrations()
            
            if migrations_applied > 0:
                logger.info(f"Applied {migrations_applied} migrations")
                self.show_message(f"Successfully applied {migrations_applied} migrations")
            else:
                logger.info("No migrations needed")
                self.show_message("Database schema is up to date")
        except Exception as e:
            logger.error(f"Error running migrations: {e}", exc_info=True)
            self.show_error(f"Migration failed: {str(e)}")
    
    def vacuum_database(self):
        """Vacuum the database to optimize storage"""
        try:
            self.db.execute_vacuum()
            logger.info("Database vacuum completed")
            self.show_message("Database optimized successfully")
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}", exc_info=True)
            self.show_error(f"Database optimization failed: {str(e)}")
    
    def backup_database(self):
        """Create a backup of the database"""
        try:
            backup_path = self.backup_manager.create_backup()
            
            logger.info(f"Database backed up to {backup_path}")
            self.show_message(f"Backup created: {os.path.basename(backup_path)}")
        except Exception as e:
            logger.error(f"Error backing up database: {e}", exc_info=True)
            self.show_error(f"Backup failed: {str(e)}")
    
    def export_to_json(self):
        """Export database to JSON"""
        try:
            # Update status
            status = self.query_one("#export-import-status")
            status.update("Exporting database to JSON...")
            
            # Perform export
            output_path = self.backup_manager.export_to_json()
            
            # Update status
            status.update(f"Export completed: {os.path.basename(output_path)}")
            logger.info(f"Database exported to JSON: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}", exc_info=True)
            self.show_error(f"Export failed: {str(e)}")
    
    def show_import_dialog(self):
        """Show dialog to import from JSON
        
        This is a placeholder - in a real implementation, this would show a file picker.
        For now, we'll just use a default backup file if it exists.
        """
        # Update status
        status = self.query_one("#export-import-status")
        status.update("Checking for JSON backups...")
        
        # Check for JSON backups
        json_backups = sorted(
            list(Config.BACKUP_DIR.glob("*.json")),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not json_backups:
            status.update("No JSON backups found")
            return
        
        # Use most recent backup
        latest_backup = json_backups[0]
        
        # Confirm with user
        status.update(f"Found backup: {os.path.basename(latest_backup)}. Importing...")
        
        # Import from JSON
        try:
            self.backup_manager.import_from_json(latest_backup, overwrite=False)
            status.update(f"Import completed from {os.path.basename(latest_backup)}")
        except Exception as e:
            logger.error(f"Error importing from JSON: {e}", exc_info=True)
            self.show_error(f"Import failed: {str(e)}")
    
    def show_message(self, message: str):
        """Show a success message (placeholder for a proper notification system)"""
        # In a full implementation, this would show a notification or toast
        # For now, we'll update the export-import-status label
        status = self.query_one("#export-import-status")
        status.update(message) 