"""Worker helper classes for database operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict

from textual.app import App
from textual.worker import Worker


@dataclass
class Progress:
    """Represents progress information for a worker."""

    current: int
    total: int
    message: str | None = None

    @property
    def percent(self) -> float:
        return (self.current / self.total) * 100 if self.total else 0.0


class DatabaseWorker(Worker):
    """Worker specialized for database operations."""

    def __init__(self, name: str, func: Callable[[], Any], app: App) -> None:
        super().__init__(func, name=name)
        self.app = app
        self.progress: Progress | None = None

    def set_progress(
        self, current: int, total: int, message: str | None = None
    ) -> None:
        self.progress = Progress(current, total, message)
        self.app.call_from_thread(self.app.refresh)

    def handle_error(self, error: Exception) -> None:
        self.app.log(f"Worker {self.name} failed: {error}")


class WorkerPool:
    """Simple container for active workers."""

    def __init__(self) -> None:
        self.workers: Dict[str, DatabaseWorker] = {}

    def add(self, worker: DatabaseWorker) -> None:
        self.workers[worker.name] = worker

    def get(self, name: str) -> DatabaseWorker | None:
        return self.workers.get(name)

    def remove(self, name: str) -> None:
        self.workers.pop(name, None)
