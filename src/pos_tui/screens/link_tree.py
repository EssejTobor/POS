from textual.app import ComposeResult
from textual.containers import Container

from ..widgets import LinkTree


class LinkTreeScreen(Container):
    """Screen for visualizing item links."""

    def compose(self) -> ComposeResult:
        yield LinkTree(id="link_tree")
