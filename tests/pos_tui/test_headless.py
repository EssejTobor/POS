import pytest
from textual.testing import AppTest

from src.pos_tui.app import POSTUI


@pytest.mark.asyncio
async def test_app_launches_headless():
    app = POSTUI()
    async with AppTest(app) as pilot:
        assert pilot.app.query_one("#tabs")
        dashboard = pilot.app.query_one("#dashboard")
        assert dashboard.query_one("#filter_bar")
