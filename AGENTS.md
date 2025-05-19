# AGENTS.md – Guidance for OpenAI Codex on the POS repository

## Scope
These rules apply to the entire repository unless a deeper `AGENTS.md` overrides them.

---


## 1. Code Style
- Format code using `black .` and `isort .`.
- Lint with `ruff .` and ensure no warnings remain.
- Type-check using `mypy src/`.

---

## 2. Testing
- Always pass `python -m pytest -q tests/` before committing.
- If changes affect `src/database.py` or `src/storage.py`, also run targeted DB tests.
- Never disable or skip tests in CI.

---

## 3. Documentation & Changelog
- **MANDATORY**: Append a bullet to `[Unreleased]` in `CHANGELOG.md` before any commit.
- If architecture or behavior changes, update `PROJECT_SCOPE.md`.
- Use this log format:


Updated CHANGELOG.md: <one-line summary>
Updated PROJECT\_SCOPE.md: <one-line summary> (if applicable)



---

## 4. Database Safety
- Before modifying schemas or migrations, run:


python -m src.backup create\_backup "pre\_schema\_change"

- Validate migrations with:


python src/migrate.py --dry-run



---

## 5. CLI Conventions
- New commands must include Rich help text.
- Always include a fallback stub when `rich` is not installed.
- ID generation in `WorkSystem.generate_id()` must preserve:
- Microsecond timestamp-based uniqueness.
- Two-letter goal prefixes (e.g. `th` for “thought” items).
- Existing “collision-prevention” behavior.

---

## 6. Pull-Request Checklist
- Title format: `[Feat]`, `[Fix]`, `[Refactor]`, or `[Docs]` + short description.
- Commit message format: `cli: <verb-phrase>` or `db: <verb-phrase>` etc.
- PR body must include a “Testing Done” section and link to a passing CI log.
- All changes should be pushed via a feature branch and reviewed in PRs—**never commit directly to `main`**.


