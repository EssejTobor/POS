"""Worker helper classes for database operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List

from textual.app import App
from textual.worker import Worker

from ..models import ItemStatus, ItemType, WorkItem
from ..storage import WorkSystem


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


class ItemFetchWorker(DatabaseWorker):
    """Worker that fetches items with filtering and sorting."""

    def __init__(
        self,
        app: App,
        work_system: WorkSystem,
        *,
        item_type: ItemType | list[ItemType] | None = None,
        status: ItemStatus | list[ItemStatus] | None = None,
        search_text: str = "",
        start_date: str | None = None,
        end_date: str | None = None,
        sort_key: Callable[[WorkItem], object] | None = None,
        sort_reverse: bool = False,
        page: int = 0,
        page_size: int = 20,
        name: str = "item_fetch",
        callback: Callable[[Iterable[WorkItem]], None] | None = None,
    ) -> None:
        self.work_system = work_system
        self.item_type = item_type
        self.status = status
        self.search_text = search_text
        self.start_date = start_date
        self.end_date = end_date
        self.sort_key = sort_key
        self.sort_reverse = sort_reverse
        self.page = page
        self.page_size = page_size
        self.callback = callback
        super().__init__(name, self._run, app)

    def _run(self) -> List[WorkItem]:
        items = self.work_system.get_filtered_items(
            item_type=self.item_type,
            status=self.status,
            search_text=self.search_text or None,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        if self.sort_key:
            items = sorted(
                items,
                key=self.sort_key,  # type: ignore[arg-type]
                reverse=self.sort_reverse,
            )
        start = self.page * self.page_size
        end = start + self.page_size
        results = items[start:end]
        if self.callback is not None:
            self.app.call_from_thread(self.callback, results)
        return results


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
