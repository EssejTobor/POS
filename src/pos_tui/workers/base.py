from __future__ import annotations

import traceback
from typing import Any, Callable, Optional

from textual.app import App
from textual.worker import Worker


class BaseWorker(Worker):
    """Worker with lifecycle callbacks and result/error handling."""

    def __init__(
        self,
        name: str,
        func: Callable[[], Any],
        app: App,
        on_start: Callable[[], None] | None = None,
        on_success: Callable[[Any], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(func, name=name)
        self.app = app
        self.on_start_cb = on_start
        self.on_success_cb = on_success
        self.on_error_cb = on_error
        self.on_complete_cb = on_complete
        self.result: Any = None
        self.error: Exception | None = None

    # Textual calls these methods at various stages of execution
    def on_start(self) -> None:  # pragma: no cover - simple delegation
        if self.on_start_cb:
            self.app.call_from_thread(self.on_start_cb)

    def on_success(self, result: Any) -> None:
        self.result = result
        if self.on_success_cb:
            self.app.call_from_thread(self.on_success_cb, result)

    def on_error(self, error: Exception) -> None:
        self.error = error
        if self.on_error_cb:
            self.app.call_from_thread(self.on_error_cb, error)
        else:
            self.app.log(
                f"Worker {self.name} failed: {error}\n{traceback.format_exc()}"
            )

    def on_complete(self) -> None:  # pragma: no cover - simple delegation
        if self.on_complete_cb:
            self.app.call_from_thread(self.on_complete_cb)
