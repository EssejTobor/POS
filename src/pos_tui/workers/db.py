from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from queue import Empty, Queue
from typing import Any, Callable, Iterable

from textual.app import App

from .base import BaseWorker


class DBConnectionManager:
    """Simple SQLite connection pool with retry logic."""

    def __init__(self, db_path: str, pool_size: int = 4) -> None:
        self.db_path = db_path
        self.pool: Queue[sqlite3.Connection] = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.put(conn)

    @contextmanager
    def connection(self, retries: int = 3, delay: float = 0.05):
        """Acquire a connection with simple retry logic."""
        attempt = 0
        while True:
            try:
                conn = self.pool.get_nowait()
                break
            except Empty:
                if attempt >= retries:
                    raise RuntimeError("No database connections available")
                attempt += 1
                time.sleep(delay)
        try:
            yield conn
            conn.commit()
        finally:
            self.pool.put(conn)


class ItemFetchWorker(BaseWorker):
    """Worker to fetch items using the connection manager."""

    def __init__(
        self,
        name: str,
        app: App,
        manager: DBConnectionManager,
        query: str,
        params: Iterable[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        params = params or []

        def task() -> list[dict[str, Any]]:
            with manager.connection() as conn:
                cursor = conn.execute(query, tuple(params))
                return [dict(row) for row in cursor.fetchall()]

        super().__init__(name, task, app, **kwargs)


class ItemSaveWorker(BaseWorker):
    """Worker to execute write operations using a connection."""

    def __init__(
        self,
        name: str,
        app: App,
        manager: DBConnectionManager,
        operation: Callable[[sqlite3.Connection], int],
        **kwargs: Any,
    ) -> None:

        def task() -> int:
            with manager.connection() as conn:
                return operation(conn)

        super().__init__(name, task, app, **kwargs)


class LinkWorker(ItemSaveWorker):
    """Alias for ItemSaveWorker used for link operations."""

    pass
