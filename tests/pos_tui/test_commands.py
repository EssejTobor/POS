import pytest
from textual.testing import AppTest
from textual.widgets import ListItem

from src.pos_tui.app import POSTUI
from src.pos_tui.commands import Command, CommandRegistry


class TestCommandRegistry:
    def test_command_registration(self):
        registry = CommandRegistry()
        cmd = Command("test", "Test Command", lambda: None)
        registry.register(cmd)
        assert "test" in registry.commands

    def test_command_categorization(self):
        registry = CommandRegistry()
        cmd1 = Command("new_item", "Create New Item", lambda: None, category="items")
        cmd2 = Command("filter", "Filter View", lambda: None, category="view")
        registry.register(cmd1)
        registry.register(cmd2)

        item_commands = registry.get_commands_by_category("items")
        assert len(item_commands) == 1
        assert item_commands[0].name == "new_item"


class TestCommandPalette:
    @pytest.mark.asyncio
    async def test_palette_display(self):
        app = POSTUI()
        async with AppTest(app) as pilot:
            await pilot.press("ctrl+p")
            palette = pilot.app.query_one("#command_palette")
            assert palette.display

    @pytest.mark.asyncio
    async def test_palette_filtering(self):
        app = POSTUI()
        async with AppTest(app) as pilot:
            await pilot.press("ctrl+p")
            palette = pilot.app.query_one("#command_palette")
            await pilot.write("new")
            results = palette.query(ListItem)
            assert len(results) > 0
            assert all("new" in r.renderable.plain.lower() for r in results)
