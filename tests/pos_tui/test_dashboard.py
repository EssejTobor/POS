import pytest
from textual.testing import AppTest
from textual.widgets import LoadingIndicator

from src.pos_tui.app import POSTUI
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
