import pytest
from textual.testing import AppTest
from textual.widgets import Button, LoadingIndicator, Static

from src.models import ItemStatus
from src.pos_tui.app import POSTUI
from src.pos_tui.widgets.dashboard_status import DashboardStatus
from src.pos_tui.widgets.filter_bar import FilterBar
from src.pos_tui.widgets.item_table import ItemTable


@pytest.mark.asyncio
async def test_dashboard_refresh_loads_items():
    app = POSTUI()
    async with AppTest(app) as pilot:
        # Wait briefly for worker to load data
        await pilot.pause(0.1)
        table = pilot.app.query_one(ItemTable)
        loading = pilot.app.query_one(LoadingIndicator)
        assert table.row_count > 0
        assert not loading.display


@pytest.mark.asyncio
async def test_filter_bar_present():
    app = POSTUI()
    async with AppTest(app) as pilot:
        assert pilot.app.query_one(FilterBar)


@pytest.mark.asyncio
async def test_dashboard_status_counts():
    app = POSTUI()
    async with AppTest(app) as pilot:
        # Wait for items to load
        await pilot.pause(0.1)
        status = pilot.app.query_one(DashboardStatus)
        ws = pilot.app.work_system
        expected_total = len(ws.items)
        expected_incomplete = len(
            [i for i in ws.items.values() if i.status != ItemStatus.COMPLETED]
        )
        assert status.total == expected_total
        assert status.incomplete == expected_incomplete
async def test_dashboard_layout_components():
    app = POSTUI()
    async with AppTest(app) as pilot:
        pilot.app.query_one("#dashboard_header")
        pilot.app.query_one("#dashboard_footer")
        pilot.app.query_one("#refresh_button", Button)
        pilot.app.query_one("#create_button", Button)
        footer = pilot.app.query_one("#status_bar", Static)
        assert footer.renderable is not None
