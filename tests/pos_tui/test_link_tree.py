from src.models import ItemStatus, ItemType, Priority, WorkItem
from src.pos_tui.widgets.link_tree import LinkTree


class DummyWS:
    def __init__(self):
        self.items: dict[str, WorkItem] = {}
        self.links: dict[str, dict] = {}
        self.calls: int = 0

    def get_links(self, item_id: str) -> dict:
        self.calls += 1
        return self.links.get(item_id, {"outgoing": [], "incoming": []})


def _make_item(id_: str) -> WorkItem:
    return WorkItem(
        id=id_,
        title=f"Item {id_}",
        goal="g",
        item_type=ItemType.TASK,
        description="d",
        priority=Priority.MED,
        status=ItemStatus.NOT_STARTED,
    )


def test_depth_control():
    ws = DummyWS()
    ws.items["a"] = _make_item("a")
    ws.items["b"] = _make_item("b")
    ws.items["c"] = _make_item("c")
    ws.links["a"] = {
        "outgoing": [{"target_id": "b", "link_type": "references"}],
        "incoming": [],
    }
    ws.links["b"] = {
        "outgoing": [{"target_id": "c", "link_type": "references"}],
        "incoming": [],
    }

    tree = LinkTree(work_system=ws)
    data = tree._build_tree_data("a", set(), 0)
    assert len(data["children"][0][1]["children"]) == 1

    tree.max_depth = 1
    data = tree._build_tree_data("a", set(), 0)
    assert data["children"][0][1]["children"] == []


def test_link_caching():
    ws = DummyWS()
    ws.items["a"] = _make_item("a")

    tree = LinkTree(work_system=ws)
    tree._get_links("a")
    tree._get_links("a")
    assert ws.calls == 1
