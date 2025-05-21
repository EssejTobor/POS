import os
from pathlib import Path

from src.models import ItemType, Priority
from src.storage import WorkSystem


def test_get_all_tags(tmp_path):
    db_file = tmp_path / "test_tags.db"
    ws = WorkSystem(storage_path=str(db_file))

    item = ws.add_item(
        goal="TagGoal",
        title="Item1",
        item_type=ItemType.TASK,
        description="desc",
        priority=Priority.MED,
    )
    ws.add_tag_to_item(item.id, "urgent")
    ws.add_tag_to_item(item.id, "important")

    item2 = ws.add_item(
        goal="TagGoal",
        title="Item2",
        item_type=ItemType.LEARNING,
        description="desc",
        priority=Priority.LOW,
    )
    ws.add_tag_to_item(item2.id, "urgent")

    tags = ws.get_all_tags()
    assert tags == ["important", "urgent"]
