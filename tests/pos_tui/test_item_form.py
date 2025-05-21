import pytest
from textual.app import App, ComposeResult
from textual.testing import AppTest

from src.pos_tui.widgets.item_form import ItemEntryForm


class FormApp(App):
    def compose(self) -> ComposeResult:
        yield ItemEntryForm()


@pytest.mark.asyncio
async def test_item_form_fields_exist():
    app = FormApp()
    async with AppTest(app) as pilot:
        form = pilot.app.query_one(ItemEntryForm)
        assert form.query_one("#title_field")
        assert form.query_one("#description_field")
        assert form.query_one("#type_selector")
        assert form.query_one("#priority_selector")
        assert form.query_one("#due_date_field")
        assert form.query_one("#tags_field")


@pytest.mark.asyncio
async def test_item_form_validation_error():
    app = FormApp()
    async with AppTest(app) as pilot:
        form = pilot.app.query_one(ItemEntryForm)
        submit = form.query_one("#submit_button")
        await pilot.click(submit)
        msg = form.query_one("#validation_message").renderable.plain
        assert "Title is required" in msg
