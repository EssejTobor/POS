# Contributor Guide

## Scope
These rules apply to the entire repository unless a deeper `AGENTS.md` overrides them.

---

## 0. Environment Setup
- Run `uv pip install -e .[dev]` to install the project and its development dependencies.
- Target Python 3.12 (`python --version` should return 3.12.*).
- Internet access is disabled once the container starts; make all dependencies local.
- See .cursor directory for more guides
---

## 1. Code Style
- Format code using `black .` and `isort .`.
- Lint with `ruff .` and ensure no warnings remain.
- Type-check using `mypy src/`.

---

## 2. Testing
- Always pass `python -m pytest -q tests/` before committing.
- If changes affect `src/database.py` or `src/storage.py`, also run targeted DB tests.
- For Textual UI changes, run `python -m pytest tests/pos_tui/` in headless mode.
- Never disable or skip tests in CI.

---

## 3. Documentation 
- N/A



---

## 4. Database Safety
- Before modifying schemas or migrations, run:


python -m src.backup create\_backup "pre\_schema\_change"


- Validate migrations with:


python src/migrate.py --dry-run



---

## 5. UI Conventions
- New Textual screens must be registered in the main app tabs.
- Widget IDs should use consistent naming: `#lowercase_with_underscores`.
- CSS should be placed in `src/pos_tui/styles/` directory.
- Worker threads must be used for database operations to maintain UI responsiveness.

For legacy CLI (deprecated):
- New commands must include Rich help text.
- ID generation in `WorkSystem.generate_id()` must preserve:
  - Microsecond timestamp-based uniqueness.
  - Two-letter goal prefixes (e.g. `th` for "thought" items).
  - Existing "collision-prevention" behavior.

---

## 6. Pull-Request Checklist
- Title format: `[Feat]`, `[Fix]`, `[Refactor]`, or `[Docs]` + short description.
- Commit message format: `cli: <verb-phrase>` or `db: <verb-phrase>` etc.
- PR body must include a "Testing Done" section and link to a passing CI log.
- All changes should be pushed via a feature branch and reviewed in PRs—**never commit directly to `main`**.

---

## 7. Approved Shell Commands
Allowed:
- `uv`
- `pytest`
- `ruff`
- `black`
- `mypy`
- `sqlite3`
- `bash` (read-only ops only)

Disallowed:
- Docker (`docker`), even though not available in sandbox
- Any command requiring outbound network access
- Package managers other than `uv`
- `git push --force`

---

## 8. Interaction Policy
- Use *ask-before-exec* mode for any command that writes outside the following folders:
- `src/`
- `tests/`
- `docs/`

---

## 9. Pre-commit Hooks
- If `.pre-commit-config.yaml` exists, run:


pre-commit run --all-files


before committing changes.

## 10. Textual Development Guidelines
- Screens should be in `src/pos_tui/screens/`.
- Widgets should be in `src/pos_tui/widgets/`.
- Use worker threads for any operation that might block the UI.
- Follow Textual's reactive programming model for state management.
- Include keyboard shortcuts for all actions with visual indicators.
- All data-related changes must continue to use the `WorkSystem` API.



