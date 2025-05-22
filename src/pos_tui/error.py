from __future__ import annotations
"""Simple error logging utilities."""

import traceback
from pathlib import Path
from typing import Any

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
