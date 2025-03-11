from pathlib import Path
import os

class Config:
    """Central configuration for the POS application"""
    
    # Paths
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = BASE_DIR / "data"
    DB_DIR = DATA_DIR / "db"
    DB_PATH = DB_DIR / "work_items.db"
    BACKUP_DIR = DATA_DIR / "backups"
    LOG_DIR = DATA_DIR / "logs"
    LOG_PATH = LOG_DIR / "app.log"
    
    # Application settings
    APP_NAME = "Personal Operating System"
    APP_VERSION = "0.2.0"
    DARK_MODE_DEFAULT = True
    
    @classmethod
    def ensure_dirs(cls):
        """Ensure all required directories exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.DB_DIR.mkdir(exist_ok=True, parents=True)
        cls.BACKUP_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)
        
    @classmethod
    def get_db_path(cls) -> Path:
        """Return the database path, ensuring the directory exists"""
        cls.ensure_dirs()
        return cls.DB_PATH 