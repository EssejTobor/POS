from __future__ import annotations
"""Simple error logging utilities."""

import traceback
from pathlib import Path
from typing import Any
from textual.app import App
from .widgets import ToastNotification

ERROR_LOG = Path(__file__).resolve().parents[2] / "data" / "error.log"


def log_error(err: Exception | str) -> None:
    """Append the traceback for ``err`` to ``error.log``."""
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERROR_LOG.open("a") as fh:
        if isinstance(err, Exception):
            fh.write(traceback.format_exc())
        else:
            fh.write(str(err))
        fh.write("\n")


def log_and_notify(app: App, err: Exception | str, message: str = "Error") -> None:
    """Log an error and display a toast notification."""
    log_error(err)
    toast = ToastNotification(f"{message}: {err}")
    app.push_screen(toast)
