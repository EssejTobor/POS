#!/usr/bin/env python3
"""
Entry point for the Personal Operating System (POS) application.
"""
from src.app import POSApp
from src.config import Config
from src.migrations import SchemaMigrator
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    try:
        # Ensure directories exist
        Config.ensure_dirs()
        
        # Run migrations
        logger.info("Running database migrations...")
        migrator = SchemaMigrator(Config.DB_PATH)
        migrations_applied = migrator.run_migrations()
        logger.info(f"Applied {migrations_applied} migrations")
        
        # Start the application
        logger.info("Starting POS application...")
        app = POSApp()
        app.run()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        print(f"ERROR: Application failed to start: {e}")
        raise

if __name__ == '__main__':
    main() 