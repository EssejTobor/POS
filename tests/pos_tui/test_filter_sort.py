from src.models import ItemStatus, ItemType, Priority, WorkItem
from src.pos_tui.widgets.item_table import ItemTable


def _make_item(
    idx: int,
    *,
    item_type: ItemType = ItemType.TASK,
    status: ItemStatus = ItemStatus.NOT_STARTED,
    title: str | None = None,
) -> WorkItem:
    return WorkItem(
        id=f"i{idx}",
        title=title or f"Item {idx}",
        goal="g",
        item_type=item_type,
        description="desc",
        priority=Priority.MED,
        status=status,
    )


def test_type_filter():
    items = [
        _make_item(1, item_type=ItemType.TASK),
        _make_item(2, item_type=ItemType.RESEARCH),
    ]
    table = ItemTable()
    table.on_mount()
    table.load_items(items)
    table.set_filters(item_type=ItemType.RESEARCH)
    assert table.row_count == 1


def test_search_filter():
    items = [_make_item(1, title="foo"), _make_item(2, title="bar baz")]
    table = ItemTable()
    table.on_mount()
    table.load_items(items)
    table.set_filters(search_text="bar")
    assert table.row_count == 1


def test_sorting_title():
    items = [_make_item(1, title="b"), _make_item(2, title="a")]
    table = ItemTable()
    table.on_mount()
    table.load_items(items)
    table.sort_by(lambda i: i.title.lower())
    first = table.rows[0].get_cell(1)
    assert first == "a"
