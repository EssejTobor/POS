import pytest
from textual.testing import AppTest
from textual.worker import WorkerState

from src.models import ItemType
from src.pos_tui.app import POSTUI
from src.pos_tui.workers import DatabaseWorker, ItemFetchWorker


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


class TestItemFetchWorker:
    @pytest.mark.asyncio
    async def test_fetch_worker_filters(self):
        app = POSTUI()
        async with AppTest(app) as pilot:
            worker = ItemFetchWorker(
                pilot.app,
                pilot.app.work_system,
                item_type=ItemType.RESEARCH,
                page_size=50,
            )
            worker_id = await pilot.app.run_worker(worker, "filter_worker")
            await pilot.wait_for_worker(worker_id)
            assert worker.state == WorkerState.SUCCESS
            assert worker.result
            assert all(i.item_type == ItemType.RESEARCH for i in worker.result)

    @pytest.mark.asyncio
    async def test_fetch_worker_sorting(self):
        app = POSTUI()
        async with AppTest(app) as pilot:
            worker = ItemFetchWorker(
                pilot.app,
                pilot.app.work_system,
                sort_key=lambda i: i.title.lower(),
                page_size=50,
            )
            worker_id = await pilot.app.run_worker(worker, "sort_worker")
            await pilot.wait_for_worker(worker_id)
            titles = [i.title for i in worker.result]
            assert titles == sorted(titles, key=str.lower)
