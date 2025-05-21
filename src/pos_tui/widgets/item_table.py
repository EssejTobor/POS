from __future__ import annotations

import asyncio

from textual.widgets import DataTable, LoadingIndicator


class ItemTable(DataTable):
    """Table for displaying work items."""

    def on_mount(self) -> None:
        self.add_columns("ID", "Title", "Type", "Status", "Priority")
        self.loading = LoadingIndicator()
        self.mount(self.loading)
        self.loading.display = False

    async def refresh_data(self) -> None:
        """Fetch items from the work system asynchronously."""
        self.loading.display = True
        items = await asyncio.to_thread(self.app.work_system.get_incomplete_items)
        self.loading.display = False

        self.clear(columns=False)
        for item in items:
            self.add_row(
                item.id,
                item.title,
                item.item_type.value,
                item.status.value,
                item.priority.name,
            )
