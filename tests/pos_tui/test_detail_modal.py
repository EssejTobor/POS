import pytest
from textual.testing import AppTest

from src.models import ItemType, Priority
from src.pos_tui.app import POSTUI
from src.pos_tui.widgets import ItemDetailModal
from src.storage import WorkSystem


@pytest.mark.asyncio
async def test_item_detail_modal_renders(tmp_path):
    db_file = tmp_path / "test.db"
    ws = WorkSystem(storage_path=str(db_file))
    item = ws.add_item(
        goal="TestGoal",
        title="Test Item",
        item_type=ItemType.TASK,
        description="desc",
        priority=Priority.LOW,
    )
    # Ensure the item exists in WorkSystem
    app = POSTUI()
    async with AppTest(app) as pilot:
        modal = ItemDetailModal(item, ws)
        await pilot.app.push_screen(modal)
        assert modal.query_one("#item_detail_container")
