import pytest
from textual.testing import AppTest
from textual.worker import WorkerState

from src.pos_tui.app import POSTUI
from src.pos_tui.workers import DatabaseWorker


class TestDatabaseWorker:
    @pytest.mark.asyncio
    async def test_worker_lifecycle(self):
        app = POSTUI()
        async with AppTest(app) as pilot:
            worker = DatabaseWorker(
                "test_worker",
                lambda: pilot.app.work_system.get_incomplete_items(),
                pilot.app,
            )
            worker_id = await pilot.app.run_worker(worker, "test_worker")
            await pilot.wait_for_worker(worker_id)
            assert worker.state == WorkerState.SUCCESS
            assert isinstance(worker.result, list)

    @pytest.mark.asyncio
    async def test_worker_error_handling(self):
        app = POSTUI()
        async with AppTest(app) as pilot:

            def fail():
                raise ValueError("boom")

            worker = DatabaseWorker("failing", fail, pilot.app)
            worker_id = await pilot.app.run_worker(worker, "failing")
            await pilot.wait_for_worker(worker_id)
            assert worker.state == WorkerState.ERROR
            assert isinstance(worker.error, ValueError)
