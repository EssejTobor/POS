from textual.widgets import Tree


class LinkTree(Tree[str]):
    """Tree visualization of linked work items."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__("Root", *args, **kwargs)
