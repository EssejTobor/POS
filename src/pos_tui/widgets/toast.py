from __future__ import annotations

from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Static
from textual.screen import ModalScreen


class ToastNotification(ModalScreen[bool]):
    """Simple toast-style notification with optional undo action."""

    CSS_PATH = Path(__file__).parent.parent / "styles" / "app.css"

    BINDINGS = [
        ("u", "undo", "Undo"),
        ("escape", "dismiss", "Close"),
    ]

    def __init__(self, message: str, *, show_undo: bool = False) -> None:
        super().__init__()
        self.message = message
        self.show_undo = show_undo

    def compose(self) -> ComposeResult:
        with Container(id="toast_container"):
            yield Static(self.message, id="toast_message")
            if self.show_undo:
                yield Button("Undo", id="undo_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI
        if event.button.id == "undo_button":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_undo(self) -> None:  # pragma: no cover - key binding
        if self.show_undo:
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_dismiss(self) -> None:  # pragma: no cover - key binding
        self.dismiss(False)
