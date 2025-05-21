import pytest
from textual.testing import AppTest
from textual.worker import WorkerState

from src.models import ItemType
from src.pos_tui.app import POSTUI
from src.pos_tui.workers import DatabaseWorker, ItemFetchWorker
from src.pos_tui.workers.db import DBConnectionManager, ItemFetchWorker

@pytest.mark.asyncio
async def test_worker_lifecycle():
    app = POSTUI()
    async with AppTest(app) as pilot:
        manager = DBConnectionManager(app.work_system.db.db_path)
        worker = ItemFetchWorker(
            "count_items",
            pilot.app,
            manager,
            "SELECT COUNT(*) as c FROM work_items",
        )
        worker_id = pilot.app.schedule_worker(worker)
        await pilot.wait_for_worker(worker_id)
        assert worker.state == WorkerState.SUCCESS
        assert worker.result[0]["c"] >= 0


def test_connection_pool_reuse():
    app = POSTUI()
    manager = DBConnectionManager(app.work_system.db.db_path, pool_size=2)
    with manager.connection() as c1, manager.connection() as c2:
        assert c1 is not c2
    with manager.connection() as c3:
        assert c3 in (c1, c2)

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

@pytest.mark.asyncio
async def test_worker_error_handling():
    app = POSTUI()
    async with AppTest(app) as pilot:
        manager = DBConnectionManager(app.work_system.db.db_path)
        worker = ItemFetchWorker(
            "bad_sql",
            pilot.app,
            manager,
            "SELECT * FROM missing_table",
        )
        worker_id = pilot.app.schedule_worker(worker)
        await pilot.wait_for_worker(worker_id)
        assert worker.state == WorkerState.ERROR
        assert worker.error is not None
