"""
Database connection manager for thread-safe database access.

This module provides a connection manager for SQLite that handles
connection pooling, thread safety, and timeout/retry logic.
"""

import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple, Union

# Thread-local storage for database connections
_thread_local = threading.local()


class DBConnectionManager:
    """Manages SQLite connections with thread safety and connection pooling.

    This class ensures that each thread has its own database connection and
    handles timeouts and retries for database operations.
    """

    def __init__(
        self,
        db_path: Union[str, Path],
        max_retries: int = 3,
        retry_delay: float = 0.5,
        timeout: float = 5.0,
    ):
        """Initialize the database connection manager.

        Args:
            db_path: Path to the SQLite database file
            max_retries: Maximum number of retry attempts for failed operations
            retry_delay: Delay between retry attempts in seconds
            timeout: SQLite connection timeout in seconds
        """
        self.db_path = Path(db_path)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self._conn_lock = threading.Lock()
        self._connections: Dict[int, sqlite3.Connection] = {}

    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-specific database connection.

        Returns:
            An SQLite connection object specific to the current thread
        """
        thread_id = threading.get_ident()

        # Check if this thread already has a connection
        if hasattr(_thread_local, "connection"):
            return _thread_local.connection

        with self._conn_lock:
            # Create a new connection for this thread
            conn = sqlite3.connect(
                self.db_path,
                timeout=self.timeout,
                isolation_level=None,  # Use autocommit mode by default
                check_same_thread=False,  # Allow cross-thread usage with proper locking
            )

            # Enable foreign keys support
            conn.execute("PRAGMA foreign_keys = ON")

            # Row factory returns rows as dictionaries
            conn.row_factory = sqlite3.Row

            # Store connection for this thread
            _thread_local.connection = conn
            self._connections[thread_id] = conn

            return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for handling database transactions.

        Provides a connection with transaction support and automatic rollback on error.

        Yields:
            An SQLite connection object with an active transaction
        """
        conn = self._get_connection()
        conn.execute("BEGIN TRANSACTION")
        try:
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for handling database connections.

        Provides a connection without transaction support for simple operations.

        Yields:
            An SQLite connection object
        """
        yield self._get_connection()

    def execute(
        self, query: str, params: Optional[Tuple] = None, retries: Optional[int] = None
    ) -> sqlite3.Cursor:
        """Execute an SQL query with retry logic.

        Args:
            query: SQL query to execute
            params: Parameters to bind to the query
            retries: Number of retry attempts (defaults to self.max_retries)

        Returns:
            SQLite cursor object with the query results

        Raises:
            sqlite3.Error: If the query fails after all retry attempts
        """
        if retries is None:
            retries = self.max_retries

        conn = self._get_connection()
        last_error = None

        for attempt in range(retries + 1):
            try:
                if params is None:
                    return conn.execute(query)
                else:
                    return conn.execute(query, params)
            except sqlite3.Error as e:
                last_error = e
                if attempt < retries:
                    time.sleep(self.retry_delay)
                    continue
                raise last_error

        # This should never be reached, but added for type checking completeness
        raise last_error if last_error else RuntimeError("Unknown database error")

    def execute_many(
        self, query: str, params_list: List[Tuple], retries: Optional[int] = None
    ) -> sqlite3.Cursor:
        """Execute an SQL query with multiple parameter sets.

        Args:
            query: SQL query to execute
            params_list: List of parameter tuples to bind to the query
            retries: Number of retry attempts (defaults to self.max_retries)

        Returns:
            SQLite cursor object

        Raises:
            sqlite3.Error: If the query fails after all retry attempts
        """
        if retries is None:
            retries = self.max_retries

        conn = self._get_connection()
        last_error = None

        for attempt in range(retries + 1):
            try:
                return conn.executemany(query, params_list)
            except sqlite3.Error as e:
                last_error = e
                if attempt < retries:
                    time.sleep(self.retry_delay)
                    continue
                raise last_error

        # This should never be reached, but added for type checking completeness
        raise last_error if last_error else RuntimeError("Unknown database error")

    def close_all(self) -> None:
        """Close all database connections.

        This method should be called when shutting down the application.
        """
        with self._conn_lock:
            for conn in self._connections.values():
                try:
                    conn.close()
                except Exception:
                    pass  # Ignore errors when closing connections
            self._connections.clear()

    def close_current(self) -> None:
        """Close the database connection for the current thread."""
        thread_id = threading.get_ident()
        with self._conn_lock:
            if thread_id in self._connections:
                try:
                    self._connections[thread_id].close()
                except Exception:
                    pass  # Ignore errors when closing connection
                del self._connections[thread_id]

            if hasattr(_thread_local, "connection"):
                delattr(_thread_local, "connection") 