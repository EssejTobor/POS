from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.css.query import DOMQuery
from textual.containers import Container
from textual import events
import logging
from pathlib import Path

from .config import Config
from .thought_manager import ThoughtManager

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

class POSApp(App):
    """Personal Operating System Textual UI Application"""
    
    TITLE = "Personal Operating System"
    CSS_PATH = "assets/pos.css"
    SCREENS = {}
    
    def __init__(self):
        super().__init__()
        logger.info("Starting POS Application")
        
        # Ensure required directories exist
        Config.ensure_dirs()
        
        # Create assets directory for CSS
        assets_dir = Path(__file__).parent / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Create CSS file if it doesn't exist
        css_path = assets_dir / "pos.css"
        if not css_path.exists():
            with open(css_path, "w") as f:
                f.write("""
/* Main POS application styles */
Screen {
    background: $surface;
}

#app-grid {
    layout: grid;
    grid-size: 5 1;
    grid-columns: 1fr 4fr;
    grid-rows: 1fr;
    height: 100%;
}

#sidebar {
    background: $panel;
    border-right: solid $primary;
    padding: 1;
    height: 100%;
    width: 100%;
    grid-column: 1;
}

#content {
    padding: 1;
    height: 100%;
    width: 100%;
    grid-column-span: 4;
}

.title {
    text-style: bold;
    background: $boost;
    color: $text;
    padding: 1;
    border: tall $primary;
    text-align: center;
    margin-bottom: 1;
}

.error-title {
    background: $error;
    color: $text;
}

.error-message {
    background: $surface;
    color: $text;
    margin: 1;
    padding: 1;
    border: tall $error;
}

.nav-item {
    margin-bottom: 1;
    padding: 1;
    background: $primary-darken-1;
    color: $text;
    text-align: center;
    border: tall $primary-darken-2;
}

.nav-item:hover {
    background: $primary;
    color: $text;
}

.button-row {
    layout: horizontal;
    background: $surface;
    height: auto;
    margin-bottom: 1;
}

.section-title {
    background: $primary-darken-1;
    color: $text;
    padding: 1;
    margin-top: 1;
    margin-bottom: 1;
    text-align: center;
    text-style: bold;
}
""")
    
    def compose(self) -> ComposeResult:
        """Create app layout"""
        # Create initial UI elements
        yield Header()
        
        with Container(id="app-grid"):
            # Sidebar navigation
            with Container(id="sidebar"):
                yield Static("Dashboard", id="nav-dashboard", classes="nav-item")
                yield Static("Work Items", id="nav-work-items", classes="nav-item")
                yield Static("Thoughts", id="nav-thoughts", classes="nav-item")
                yield Static("Settings", id="nav-settings", classes="nav-item")
            
            # Main content area - screens will be pushed here
            yield Container(id="content")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize app when mounted"""
        logger.info("App mounted")
        # Import screens here to avoid circular imports
        from .screens.dashboard import DashboardScreen
        from .screens.work_items import WorkItemScreen
        from .screens.thought_screen import ThoughtScreen
        from .screens.settings import SettingsScreen
        from .screens.error_screen import ErrorScreen
        
        # Initialize ThoughtManager
        thought_manager = ThoughtManager(Config.DB_PATH)
        
        # Register screens
        self.SCREENS = {
            "dashboard": DashboardScreen(),
            "work_items": WorkItemScreen(),
            "thoughts": ThoughtScreen(thought_manager),
            "settings": SettingsScreen(),
            "error": ErrorScreen
        }
        
        # Start with dashboard screen
        self.push_screen("dashboard")
    
    def on_static_clicked(self, event: events.Static.Clicked) -> None:
        """Handle navigation clicks"""
        # Get the ID of the clicked static widget
        widget_id = event.target.id
        
        try:
            if widget_id == "nav-dashboard":
                logger.info("Navigating to dashboard")
                self.push_screen("dashboard")
            elif widget_id == "nav-work-items":
                logger.info("Navigating to work items")
                self.push_screen("work_items")
            elif widget_id == "nav-thoughts":
                logger.info("Navigating to thoughts")
                self.push_screen("thoughts")
            elif widget_id == "nav-settings":
                logger.info("Navigating to settings")
                self.push_screen("settings")
        except Exception as e:
            logger.error(f"Error navigating to screen: {e}", exc_info=True)
            self.handle_error(e, "Navigation Error")
    
    async def handle_error(self, error: Exception, error_type: str = "General Error") -> None:
        """Handle errors by showing an error screen"""
        try:
            # Log the error
            logger.error(f"{error_type}: {str(error)}", exc_info=True)
            
            # Show error screen - ErrorScreen class accepts message and type parameters
            if "error" in self.SCREENS:
                error_screen = self.SCREENS["error"](str(error), error_type)
                await self.push_screen(error_screen)
            else:
                # Fallback if error screen isn't registered
                logger.critical("Error screen not available")
                self.bell()
        except Exception as e:
            # Last resort error handling
            logger.critical(f"Error in error handler: {str(e)}", exc_info=True)
            print(f"CRITICAL ERROR: {str(e)}")
            self.bell() 