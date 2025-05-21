from src.models import ItemStatus, ItemType, Priority, WorkItem
from src.pos_tui.widgets.item_table import ItemTable


def _make_item(
    idx: int,
    priority: Priority = Priority.MED,
    status: ItemStatus = ItemStatus.NOT_STARTED,
) -> WorkItem:
    return WorkItem(
        id=f"item{idx}",
        title=f"Item {idx}",
        goal="test",
        item_type=ItemType.TASK,
        description="desc",
        priority=priority,
        status=status,
    )


def test_columns_defined():
    table = ItemTable()
    table.on_mount()
    headers = [col.label for col in table.columns]
    assert headers == [
        "ID",
        "Title",
        "Type",
        "Status",
        "Priority",
        "Due Date",
        "Actions",
    ]


def test_pagination():
    items = [_make_item(i) for i in range(3)]
    table = ItemTable(page_size=2)
    table.on_mount()
    table.load_items(items)

    assert table.row_count == 2
    table.next_page()
    assert table.row_count == 1


def test_row_style():
    item = _make_item(1, priority=Priority.HI, status=ItemStatus.IN_PROGRESS)
    table = ItemTable()
    table.on_mount()
    table.load_items([item])
    row_style = table.rows[0].style
    assert "bold red" in str(row_style)
    assert "yellow" in str(row_style)


def test_keyboard_bindings_defined():
    table = ItemTable()
    keys = {b.key for b in table.BINDINGS}
    assert {"v", "e", "d"} <= keys


def test_context_menu_state():
    table = ItemTable()
    table.on_mount()
    table.open_context_menu(1)
    assert table.context_menu_open is True
    assert table.context_menu_row == 1
