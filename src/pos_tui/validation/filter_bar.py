from __future__ import annotations

"""Validation protocol for the FilterBar widget."""

from . import ValidationProtocol


class FilterBarValidation(ValidationProtocol):
    """Validate the FilterBar advanced filtering behaviour."""

    def __init__(self) -> None:
        super().__init__("filter_bar")

    def _run_validation(self) -> None:
        try:
            from src.pos_tui.widgets.filter_bar import FilterBar
            from src.models import ItemType, ItemStatus
            from src.pos_tui.preferences import load_preferences

            bar = FilterBar()
            bar.item_types = {ItemType.TASK}
            bar.statuses = {ItemStatus.NOT_STARTED}
            bar.search_text = "example"
            bar.start_date = "2025-05-20"
            bar.end_date = "2025-05-22"
            bar.presets = {}
            bar.current_preset = "test"
            bar._save_preferences()

            prefs = load_preferences()
            preset = prefs.get("filters", {})
            if preset.get("preset") == "test":
                self.result.add_pass("Filters saved")
            else:
                self.result.add_fail("Filters not saved")
        except Exception as e:
            self.result.add_fail(f"Exception during validation: {e}")
