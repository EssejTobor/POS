import pytest

from src.models import ItemStatus, ItemType, Priority, WorkItem
from src.pos_tui.widgets.item_details_modal import ItemDetailsModal


class DummyWorkSystem:
    def get_links(self, item_id: str):
        return {"outgoing": [], "incoming": []}


@pytest.mark.asyncio
async def test_modal_builds_details_text():
    item = WorkItem(
        id="1",
        title="Test",
        goal="g",
        item_type=ItemType.TASK,
        description="d",
        priority=Priority.MED,
        status=ItemStatus.NOT_STARTED,
    )
    modal = ItemDetailsModal(item, DummyWorkSystem())
    text = modal._build_details_text()
    assert "ID: 1" in text
    assert "Title: Test" in text
    assert "Related Items" in text
