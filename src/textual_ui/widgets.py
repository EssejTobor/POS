"""Simple widget stubs used by the Textual UI."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from textual.containers import Container
    from textual.widget import Widget
    from textual.widgets import Button, Input, Static, Tree

    TEXTUAL_AVAILABLE = True
else:  # pragma: no cover - runtime import with fallback
    try:
        from textual.containers import Container  # type: ignore
        from textual.widget import Widget  # type: ignore
        from textual.widgets import Button, Input, Static, Tree  # type: ignore

        TEXTUAL_AVAILABLE = True
    except Exception:
        TEXTUAL_AVAILABLE = False

        class Widget:
            def __init__(self, *args, **kwargs) -> None:
                pass

        class Input:
            def __init__(self, *args, **kwargs) -> None:
                pass

        class Button:
            def __init__(self, *args, **kwargs) -> None:
                pass

        class Tree:
            def __init__(self, *args, **kwargs) -> None:
                pass

        class Static:
            def __init__(self, *args, **kwargs) -> None:
                pass

        class Container:
            def __init__(self, *args, **kwargs) -> None:
                pass


class CommandPalette(Widget):
    """A command palette widget for quick access to functionality."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class ConfirmationDialog(Container):
    """A dialog for confirming potentially destructive actions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class ExpandableThoughtTree(Tree):
    """A tree widget for displaying thought hierarchies."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class ProgressIndicator(Static):
    """A widget for displaying progress of long-running operations."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class SearchInput(Input):
    """An enhanced input widget for search functionality."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class Sidebar(Container):
    """A sidebar widget for navigation and quick actions."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class StatusBar(Static):
    """A status bar widget for displaying system information."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
