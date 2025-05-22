"""
Base worker thread class for handling background operations.

This module provides a thread-safe way to execute operations off the main thread,
which is especially important for database operations in Textual applications.
"""

import threading
import time
import traceback
from functools import partial
from typing import Any, Callable, Dict, Optional


class BaseWorker:
    """Base class for worker threads that execute operations asynchronously.

    This class handles thread lifecycle management, result callbacks, and error handling.
    Subclasses should implement the _run method to define the actual work to be done.
    """

    def __init__(
        self,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        timeout: float = 30.0,
    ):
        """Initialize a worker thread.

        Args:
            callback: Function to call with the results when the operation completes
            error_callback: Function to call with error info if the operation fails
            timeout: Maximum time (seconds) to wait for the thread to complete
        """
        self.callback = callback
        self.error_callback = error_callback
        self.timeout = timeout
        self.thread: Optional[threading.Thread] = None
        self.is_running = False
        self.result: Any = None
        self.error: Optional[Exception] = None
        self.traceback: Optional[str] = None

    def start(self, **kwargs) -> None:
        """Start the worker thread with the given parameters.

        Args:
            **kwargs: Parameters to pass to the _run method
        """
        if self.is_running:
            raise RuntimeError("Worker is already running")

        self.is_running = True
        self.thread = threading.Thread(
            target=self._thread_wrapper,
            args=(kwargs,),
            daemon=True,
        )
        self.thread.start()

    def _thread_wrapper(self, kwargs: Dict[str, Any]) -> None:
        """Wrapper method that captures results and errors from the _run method.

        Args:
            kwargs: Parameters to pass to the _run method
        """
        try:
            self.result = self._run(**kwargs)
            if self.callback:
                self.callback(self.result)
        except Exception as e:
            self.error = e
            self.traceback = traceback.format_exc()
            if self.error_callback:
                self.error_callback(self.error, self.traceback)
        finally:
            self.is_running = False

    def _run(self, **kwargs) -> Any:
        """Execute the worker's main functionality.

        This method should be overridden by subclasses to implement the actual work.

        Args:
            **kwargs: Parameters for the operation

        Returns:
            The result of the operation
        """
        raise NotImplementedError("Subclasses must implement _run")

    def wait(self, timeout: Optional[float] = None) -> bool:
        """Wait for the worker thread to complete.

        Args:
            timeout: Maximum time (seconds) to wait; defaults to self.timeout

        Returns:
            True if the thread completed, False if it timed out
        """
        if not self.thread:
            return True

        if timeout is None:
            timeout = self.timeout

        start_time = time.time()
        while self.is_running and (time.time() - start_time) < timeout:
            time.sleep(0.05)

        return not self.is_running

    def cancel(self) -> None:
        """Mark the worker as canceled.

        Note: This does not actually stop the thread execution since Python threads
        cannot be forcibly terminated. It only sets a flag that can be checked by
        long-running operations.
        """
        self.is_running = False 