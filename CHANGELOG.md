# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-05-20
### Added
- Textual screens for **Dashboard**, **New Item**, and **Link Tree** under `src/pos_tui/screens`.
- Widgets `ItemEntryForm`, `ItemTable`, and `LinkTree` under `src/pos_tui/widgets`.
- Keyboard shortcuts (`1`, `2`, `3`) in `POSTUI` to switch tabs.
- Basic headless test to launch `POSTUI`.

### Changed
- `POSTUI.compose()` now wires the new screens and widgets into a tabbed layout.

