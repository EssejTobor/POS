from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Static
from textual.screen import ModalScreen


class ConfirmModal(ModalScreen[bool]):
    """Simple yes/no confirmation modal."""

    BINDINGS = [
        ("y", "confirm", "Yes"),
        ("n", "cancel", "No"),
    ]

    def __init__(self, message: str, *, variant: str = "warning") -> None:
        super().__init__()
        self.message = message
        self.variant = variant

    def compose(self) -> ComposeResult:
        with Container(id="confirm_container", classes=self.variant):
            yield Static(self.message, id="confirm_message")
            with Container(id="confirm_buttons"):
                yield Button("Yes", id="yes_button")
                yield Button("No", id="no_button")

    def on_mount(self) -> None:
        try:
            container = self.query_one("#confirm_container", Container)
        except Exception:
            # In headless validation there may be no DOM
            return
        container.styles.opacity = 0
        container.styles.animate("opacity", 1.0, duration=0.4)

    def on_button_pressed(self, event: Button.Pressed) -> None:  # pragma: no cover - UI action
        self.dismiss(event.button.id == "yes_button")

    def action_confirm(self) -> None:  # pragma: no cover - key binding
        self.dismiss(True)

    def action_cancel(self) -> None:  # pragma: no cover - key binding
        self.dismiss(False)
