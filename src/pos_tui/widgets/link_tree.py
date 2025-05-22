"""Widget for visualising item links in a tree."""

from __future__ import annotations

from typing import Dict, Set

from textual.reactive import reactive
from textual.widgets import Tree

from ...models import ItemStatus, ItemType, WorkItem
from ...storage import WorkSystem
from .link_utils import link_type_color


class LinkTree(Tree[str]):
    """Tree visualization of linked work items."""

    DEFAULT_MAX_DEPTH = 3
    zoom_level: int = reactive(0)

    def __init__(self, *args, work_system: WorkSystem | None = None, **kwargs) -> None:
        super().__init__("Root", *args, **kwargs)
        self.work_system = work_system
        self._link_cache: Dict[str, Dict] = {}
        self.max_depth = self.DEFAULT_MAX_DEPTH
        self.context_menu_node: str | None = None

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
        self.root.clear()
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
        self.root.clear()
        if data:
            self._add_nodes(self.root, data)
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

    def close_context_menu(self) -> None:
        self.context_menu_node = None

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

    # ------------------------------------------------------------------
    # Node helpers
    # ------------------------------------------------------------------
    def _add_nodes(self, parent, data: dict) -> None:
        item: WorkItem = data["item"]
        node = parent.add(self._format_item(item))
        node.allow_expand = True
        for link_type, child in data["children"]:
            if child is None:
                continue
            child_item: WorkItem = child["item"]
            label = (
                f"[{self._link_color(link_type)}]{link_type}[/{self._link_color(link_type)}]"
                f" → {self._format_item_plain(child_item)}"
            )
            child_node = node.add(label)
            child_node.allow_expand = True
            self._add_nodes(child_node, child)

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
