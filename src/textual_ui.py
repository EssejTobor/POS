from __future__ import annotations

try:  # pragma: no cover - Textual is optional
    from textual.app import App  # type: ignore
    from textual.widgets import Static  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback stub

    class App:  # type: ignore
        def __init__(self, *_, **__):
            pass

        def run(self, *_, **__):
            print("Textual not available")

    class Static:  # type: ignore
        def __init__(self, *_, **__):
            pass


class TextualApp(App):
    """Minimal Textual application stub."""

    def compose(self):  # type: ignore[override]
        yield Static("POS Textual UI")
