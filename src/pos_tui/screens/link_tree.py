from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Select, Input

from ..widgets import LinkTree


class LinkTreeScreen(Container):
    """Screen for visualizing item links."""

    def compose(self) -> ComposeResult:
        ws = getattr(self.app, "work_system", None)
        options = []
        if ws:
            options = [
                (text, text.split(" ")[0]) for text in ws.suggest_link_targets()
            ]
        yield Select(options, prompt="Root Item", id="root_select")
        yield Input(placeholder="Depth", id="depth_input")
        yield Button("Load", id="load_tree")
        yield LinkTree(id="link_tree")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_tree":
            root = self.query_one("#root_select", Select).value
            depth_field = self.query_one("#depth_input", Input).value
            depth = int(depth_field) if depth_field.isdigit() else None
            tree = self.query_one(LinkTree)
            if root:
                tree.load(root, depth=depth)
