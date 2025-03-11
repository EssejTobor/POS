from textual.widgets import Static, Button, Label
from textual.containers import Container, VerticalScroll
from textual import events
import logging

from .base_screen import BaseScreen
from ..database import Database
from ..config import Config

logger = logging.getLogger(__name__)

class DashboardScreen(BaseScreen):
    """Main dashboard screen showing overview of work items and thoughts"""
    
    def __init__(self):
        super().__init__()
        self.db = Database(Config.DB_PATH)
        logger.info("Dashboard screen initialized")
    
    def compose(self):
        """Compose the dashboard layout"""
        yield Container(
            Static("Dashboard", classes="title"),
            VerticalScroll(
                Container(
                    Static("Recent Activity", classes="section-title"),
                    Static("No recent activity to display", id="activity-list"),
                    id="activity-section"
                ),
                Container(
                    Static("Goals Overview", classes="section-title"),
                    Static("No goals to display", id="goals-list"),
                    id="goals-section"
                ),
                Container(
                    Static("Thought Branches", classes="section-title"),
                    Static("No thought branches to display", id="branches-list"),
                    id="branches-section"
                ),
                id="dashboard-content"
            ),
            id="dashboard"
        )
    
    def on_mount(self):
        """Load data when screen is mounted"""
        self.load_data()
    
    def load_data(self):
        """Load dashboard data from database"""
        try:
            # Load goals
            goals = self.db.get_all_goals()
            if goals:
                goals_content = "\n".join([f"• {goal}" for goal in goals])
                self.query_one("#goals-list").update(goals_content)
            
            # Load recent work items
            recent_items = self.db.get_items_by_filters(limit=5)
            if recent_items:
                items_content = "\n".join([f"• {item.title} ({item.status.value})" for item in recent_items])
                self.query_one("#activity-list").update(items_content)
            
            # Try to load thought branches if the table exists
            try:
                branches = self.db.get_all_thought_branches()
                if branches:
                    branches_content = "\n".join([f"• {branch}" for branch in branches])
                    self.query_one("#branches-list").update(branches_content)
            except Exception as e:
                logger.debug(f"Could not load thought branches (may not exist yet): {e}")
        
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}", exc_info=True)
            self.show_error(f"Failed to load dashboard data: {str(e)}") 