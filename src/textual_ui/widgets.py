from typing import Callable

try:
    from textual.containers import Container, Horizontal
    from textual.message import Message
    from textual.reactive import reactive
    from textual.widgets import Button, Input, ProgressBar, Static

    TEXTUAL_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - fallback stubs
    TEXTUAL_AVAILABLE = False

    class Container:  # type: ignore
        def __init__(self, *_, **__):
            pass

        def mount(self, *_, **__):
            pass

    class Horizontal(Container):  # type: ignore[misc]
        pass

    class Button:  # type: ignore
        def __init__(self, *_, **__):
            pass

    class Input:  # type: ignore
        placeholder: str
        value: str = ""

        def __init__(self, *_, **__):
            pass

    class Static:  # type: ignore
        def __init__(self, *_, **__):
            pass

    class ProgressBar:  # type: ignore
        def __init__(self, *_, **__):
            pass

    class Message:  # type: ignore
        pass

    def reactive(*_, **__):  # type: ignore
        return None


class CommandPalette(Container):
    """Simple command palette widget."""

    DEFAULT_CSS = """
    CommandPalette {
        layer: overlay;
        width: 60%;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 1;
        align: center middle;
    }
    """

    def __init__(self, commands: dict[str, Callable[[], None]]):
        super().__init__()
        self.commands = commands

    def compose(self):  # pragma: no cover - UI only
        if not TEXTUAL_AVAILABLE:
            return None
        yield Input(placeholder="Enter command", id="cmd-input")

    def on_mount(self) -> None:  # pragma: no cover - UI only
        if TEXTUAL_AVAILABLE:
            self.query_one(Input).focus()

    def on_input_submitted(
        self, event: Input.Submitted
    ) -> None:  # pragma: no cover - UI only
        if not TEXTUAL_AVAILABLE:
            return
        cmd = event.value.strip()
        action = self.commands.get(cmd)
        if action:
            action()
        self.remove()

    def key_escape(self) -> None:  # pragma: no cover - UI only
        if TEXTUAL_AVAILABLE:
            self.remove()


class ModalDialog(Container):
    """Generic modal dialog with OK/Cancel."""

    DEFAULT_CSS = """
    ModalDialog {
        layer: overlay;
        width: 50%;
        height: auto;
        border: heavy $primary;
        background: $background;
        padding: 2;
        align: center middle;
    }
    ModalDialog Button {
        margin: 1 2;
    }
    """

    def __init__(self, message: str, callback):
        super().__init__()
        self.message = message
        self.callback = callback

    def compose(self):  # pragma: no cover - UI only
        if not TEXTUAL_AVAILABLE:
            return None
        yield Static(self.message)
        with Horizontal():
            yield Button("OK", id="ok")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(
        self, event: Button.Pressed
    ) -> None:  # pragma: no cover - UI only
        if not TEXTUAL_AVAILABLE:
            return
        self.callback(event.button.id == "ok")
        self.remove()


class ProgressIndicator(Container):
    """Display simple progress information."""

    progress = reactive(0)

    DEFAULT_CSS = """
    ProgressIndicator {
        layer: overlay;
        width: 60%;
        height: auto;
        border: heavy $primary;
        background: $background;
        padding: 1;
        align: center middle;
    }
    """

    def __init__(self, message: str = "Working..."):
        super().__init__()
        self.message = message

    def compose(self):  # pragma: no cover - UI only
        if not TEXTUAL_AVAILABLE:
            return None
        yield Static(self.message, id="progress-msg")
        yield ProgressBar(total=100, id="progress-bar")

    def watch_progress(self, value: int) -> None:  # pragma: no cover - UI only
        if not TEXTUAL_AVAILABLE:
            return
        bar = self.query_one("#progress-bar", ProgressBar)
        bar.update(value)
        if value >= 100:
            self.remove()


class StatusBar(Static):
    """Simple status bar showing system info."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: auto;
        background: $secondary-darken-1;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(self, get_info):
        super().__init__("")
        self.get_info = get_info

    def on_mount(self) -> None:  # pragma: no cover - UI only
        if TEXTUAL_AVAILABLE:
            self.set_interval(5, self.refresh_info)
            self.refresh_info()

    def refresh_info(self) -> None:  # pragma: no cover - UI only
        if TEXTUAL_AVAILABLE:
            self.update(self.get_info())
