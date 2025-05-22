"""Widget for visualising item links in a tree."""

from __future__ import annotations

from typing import Dict, Set

from textual.message import Message

from textual.widgets import OptionList
from textual.widgets.option_list import Option

from textual.reactive import reactive
from textual.widgets import Tree

from ...models import ItemStatus, ItemType, WorkItem
from ...storage import WorkSystem
from .link_utils import link_type_color


class LinkTree(Tree[str]):
    """Tree visualization of linked work items."""

    DEFAULT_MAX_DEPTH = 3
    zoom_level: int = reactive(0)

    BINDINGS = [
        ("v", "view_selected", "View"),
        ("e", "edit_selected", "Edit"),
        ("d", "delete_selected", "Delete"),
    ]

    class ViewRequested(Message):
        def __init__(self, sender: "LinkTree", item_id: str) -> None:
            super().__init__(sender)
            self.item_id = item_id

    class EditRequested(Message):
        def __init__(self, sender: "LinkTree", item_id: str) -> None:
            super().__init__(sender)
            self.item_id = item_id

    class DeleteRequested(Message):
        def __init__(self, sender: "LinkTree", item_id: str) -> None:
            super().__init__(sender)
            self.item_id = item_id

    def __init__(self, *args, work_system: WorkSystem | None = None, **kwargs) -> None:
        super().__init__("Root", *args, **kwargs)
        self.work_system = work_system
        self._link_cache: Dict[str, Dict] = {}
        self.max_depth = self.DEFAULT_MAX_DEPTH
        self.context_menu_node: str | None = None
        self.context_menu: OptionList | None = None
        self.context_menu_open: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load(self, item_id: str, *, depth: int | None = None) -> None:
        """Load the tree starting from ``item_id`` asynchronously."""

        self.max_depth = depth or self.DEFAULT_MAX_DEPTH
        ws = self.work_system or getattr(self.app, "work_system", None)
        if ws is None:  # pragma: no cover - app always provides work_system
            return

        self.work_system = ws
        self.root.label = item_id
        self.root.data = {"id": item_id, "depth": 0, "loaded": False}
        self.root.remove_children()
        self.run_worker(lambda: self._fetch_and_build(item_id), thread=True)

    # ------------------------------------------------------------------
    # Worker helpers
    # ------------------------------------------------------------------
    def _fetch_and_build(self, item_id: str) -> None:
        data = self._build_tree_data(item_id, set(), 0)
        self.call_from_thread(self._apply_tree, data)

    def _build_tree_data(
        self, item_id: str, visited: Set[str], depth: int
    ) -> dict | None:
        if depth > self.max_depth or item_id in visited:
            return None

        visited.add(item_id)
        item = self._get_item(item_id)
        if item is None:
            return None

        links = self._get_links(item_id)
        children: list[tuple[str, dict | None]] = []
        for link in links.get("outgoing", []):
            target_id = link["target_id"]
            link_type = link["link_type"]
            child = self._build_tree_data(target_id, visited, depth + 1)
            children.append((link_type, child))

        visited.remove(item_id)
        return {"item": item, "children": children}

    def _apply_tree(self, data: dict | None) -> None:
        self.root.remove_children()
        if data:
            self._add_nodes(self.root, data, 0)
        else:  # pragma: no cover - no data provided
            self.root.add("No data")

    # ------------------------------------------------------------------
    # Interactive helpers
    # ------------------------------------------------------------------
    def action_zoom_in(self) -> None:
        self.zoom_level += 1
        self.styles.indent = 1 + self.zoom_level

    def action_zoom_out(self) -> None:
        self.zoom_level = max(0, self.zoom_level - 1)
        self.styles.indent = 1 + self.zoom_level

    def open_context_menu(self, node_id: str) -> None:
        self.context_menu_node = node_id
        if self.context_menu_open:
            self.close_context_menu()
        menu = OptionList(
            Option("View", id="view"),
            Option("Edit", id="edit"),
            Option("Delete", id="delete"),
            id="tree_context_menu",
        )
        self.context_menu = menu
        self.mount(menu)
        self.focus()
        self.context_menu_open = True

    def close_context_menu(self) -> None:
        if self.context_menu is not None:
            self.context_menu.remove()
            self.context_menu = None
        self.context_menu_node = None
        self.context_menu_open = False

    def action_view_selected(self) -> None:  # pragma: no cover - simple action
        node = self.cursor_node
        if node is None:
            return
        self.post_message(self.ViewRequested(self, node.data["id"]))

    def action_edit_selected(self) -> None:  # pragma: no cover - simple action
        node = self.cursor_node
        if node is None:
            return
        self.post_message(self.EditRequested(self, node.data["id"]))

    def action_delete_selected(self) -> None:  # pragma: no cover - simple action
        node = self.cursor_node
        if node is None:
            return
        self.post_message(self.DeleteRequested(self, node.data["id"]))

    def export_tree(self) -> str:
        """Export the current tree as plain text."""
        return "\n".join(node.label for node in self.nodes)

    def bookmark_view(self) -> Dict:
        """Return a bookmark representing the current tree state."""
        return {"root": self.root.label, "depth": self.max_depth}

    # --------------------------------------------------------------
    # Event handlers
    # --------------------------------------------------------------
    def on_tree_node_selected(
        self, event: Tree.NodeSelected
    ) -> None:  # pragma: no cover - simple selection
        self.open_context_menu(event.node.id)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        node = event.node
        if node.data and not node.data.get("loaded"):
            self._load_children(node)

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:  # pragma: no cover - simple UI
        if not self.context_menu_open or self.context_menu is None:
            return
        action = event.option.id
        node_id = self.context_menu_node
        self.close_context_menu()
        if node_id is None:
            return
        if action == "view":
            self.action_view_selected()
        elif action == "edit":
            self.action_edit_selected()
        elif action == "delete":
            self.action_delete_selected()

    # ------------------------------------------------------------------
    # Node helpers
    # ------------------------------------------------------------------
    def _add_nodes(self, parent, data: dict, depth: int) -> None:
        item: WorkItem = data["item"]
        node = parent.add(self._format_item(item))
        node.allow_expand = True
        node.data = {"id": item.id, "depth": depth, "loaded": True}
        if depth >= self.max_depth:
            return
        for link_type, child in data["children"]:
            if child is None:
                continue
            child_item: WorkItem = child["item"]
            label = (
                f"[{self._link_color(link_type)}]{link_type}[/{self._link_color(link_type)}]"
                f" -> {self._format_item_plain(child_item)}"
            )
            child_node = node.add(label)
            child_node.allow_expand = True
            child_node.data = {"id": child_item.id, "depth": depth + 1, "loaded": False}

    def _load_children(self, node) -> None:
        depth = node.data.get("depth", 0)
        if depth >= self.max_depth:
            node.data["loaded"] = True
            return
        item_id = node.data.get("id")
        if item_id is None:
            return
        links = self._get_links(item_id)
        for link in links.get("outgoing", []):
            target_id = link["target_id"]
            child_item = self._get_item(target_id)
            if child_item is None:
                continue
            label = (
                f"[{self._link_color(link['link_type'])}]{link['link_type']}[/{self._link_color(link['link_type'])}]"
                f" -> {self._format_item_plain(child_item)}"
            )
            child = node.add(label)
            child.allow_expand = True
            child.data = {"id": child_item.id, "depth": depth + 1, "loaded": False}
        node.data["loaded"] = True

    # ------------------------------------------------------------------
    # Caching helpers
    # ------------------------------------------------------------------
    def _get_links(self, item_id: str) -> Dict:
        assert self.work_system is not None
        if item_id not in self._link_cache:
            self._link_cache[item_id] = self.work_system.get_links(item_id)
        return self._link_cache[item_id]

    def _get_item(self, item_id: str) -> WorkItem | None:
        assert self.work_system is not None
        return self.work_system.items.get(item_id)

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def _format_item(self, item: WorkItem) -> str:
        color = self._type_color(item.item_type)
        status_style = {
            ItemStatus.IN_PROGRESS: "bold",
            ItemStatus.COMPLETED: "dim",
            ItemStatus.NOT_STARTED: "",
        }.get(item.status, "")
        style = " ".join(filter(None, [color, status_style]))
        return f"[{style}]{item.id} - {item.title}[/{style}]"

    def _format_item_plain(self, item: WorkItem) -> str:
        color = self._type_color(item.item_type)
        return f"[{color}]{item.id} - {item.title}[/{color}]"

    @staticmethod
    def _type_color(item_type: ItemType) -> str:
        return {
            ItemType.TASK: "cyan",
            ItemType.LEARNING: "green",
            ItemType.RESEARCH: "yellow",
            ItemType.THOUGHT: "magenta",
        }.get(item_type, "white")

    @staticmethod
    def _link_color(link_type: str) -> str:
        """Return color for ``link_type`` using shared mapping."""
        return link_type_color(link_type)
