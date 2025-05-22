from __future__ import annotations

import os
import tempfile

from . import ValidationProtocol
from ..widgets.link_tree import LinkTree
from ...storage import WorkSystem
from ...models import ItemType, Priority


class LinkTreeValidation(ValidationProtocol):
    """Validate basic LinkTree functionality."""

    def __init__(self) -> None:
        super().__init__("link_tree")

    def _run_validation(self) -> None:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        try:
            ws = WorkSystem(tmp.name)
            parent = ws.add_item(
                goal="test",
                title="Parent",
                item_type=ItemType.TASK,
                description="p",
                priority=Priority.MED,
            )
            child = ws.add_item(
                goal="test",
                title="Child",
                item_type=ItemType.TASK,
                description="c",
                priority=Priority.LOW,
            )
            ws.add_link(parent.id, child.id, "references")

            tree = LinkTree(work_system=ws)
            tree.root.label = parent.id
            tree._apply_tree(tree._build_tree_data(parent.id, set(), 0))

            if tree.root.children:
                self.result.add_pass("Root children loaded")
            else:
                self.result.add_fail("Root children missing")

            node = list(tree.root.children)[0]
            tree._load_children(node)
            if node.children:
                self.result.add_pass("Expansion loads children")
            else:
                self.result.add_fail("Expansion failed")
        except Exception as e:
            self.result.add_fail(f"LinkTree validation error: {e}")
        finally:
            os.unlink(tmp.name)
