# Contributor Guide – *Crash-First Edition*

These rules apply to the entire repository unless a deeper `AGENTS.md` overrides them.

---

## 0. Environment

* The Codex task runner always performs **one** `pip install -e .` while the
  network is still on; whatever lives in **`[project].dependencies`** therefore
  gets installed automatically.
* **Do not rely on extras or dev tools** (`pytest`, `ruff`, `black`, `mypy`, …)
  unless you add a line for them in `setup.sh`.  
  By default we run with **runtime libs only** (e.g. `textual==2.1.2`, `rich`,
  `sqlalchemy`, …).

---

## 1. Coding Style

* Keep the code readable; follow PEP-8 where practical.
* When in doubt: **clarity over cleverness**.  
  Simple functions and explicit names beat meta-magic.

---

## 2. "Crash-First" Testing Workflow  
*No external test frameworks required.*

1. **Launch the program** in a separate process:
```bash
   python -m pos_tui.app              # Textual UI
   python -m src.cli add "demo" ...   # CLI examples
```

2. If it crashes, read the traceback **once**, patch the code, and rerun.
   Repeat until the command exits with `0`.
3. **Inline sanity checks** are encouraged:

   ```python
   # src/something.py
   def _quick_check() -> None:
       item = WorkSystem().add("title", "desc")
       assert item.id.startswith("wk")
   if __name__ == "__main__":
       _quick_check()
   ```

   Running `python src/something.py` must finish silently.

> Goal: leave the repo in a state where *real users* can run the main entry
> points without exploding, even if no formal test suite exists.

---

## 3. Commit Etiquette

```
[Fix] cli: handle empty title
[Feat] tui: command palette fuzzy search
```

* One logical change per commit.
* Describe **what** changed and, if non-obvious, **why**.

---

## 4. Approved Shell Commands (inside Codex sandbox)

| Allowed                       | Purpose                                                    |
| ----------------------------- | ---------------------------------------------------------- |
| `python`                      | run modules / ad-hoc scripts                               |
| `bash`                        | simple file operations (`cp`, `sed`, `grep`, …)            |
| `sqlite3`                     | inspect local DB files                                     |
| `pip install …` in `setup.sh` | **only** if the wheel is available on PyPI at install time |

Anything else (Docker, system package managers, network calls) is blocked.

---

## 5. Quick Reference – Typical Dev Loop

```bash
# 0. (Codex already ran setup.sh)

# 1. Make a small change
apply_patch <<'PATCH'
*** Begin Patch
*** Update File: src/display.py
@@
- print("DEBUG", data)
+ # Removed noisy debug print
*** End Patch
PATCH

# 2. Re-run the failing command
python -m pos_tui.app          # or any CLI example
# -> no crash? commit
git commit -am "fix: remove stray debug print"

# 3. Repeat

```
---

## 6. Documentation

* Update `CHANGELOG.md` *only* when you introduce a user-visible behaviour
  change (new command, new CLI flag, schema migration, …).
* Keep comments and docstrings concise but accurate.
* When implementing a feature or fixing a bug:
  * Check off the corresponding item in `docs/checklist.md`
  * Create or update validation protocols in the appropriate markdown file
* **Always update documentation as you implement** - this ensures our progress tracking stays accurate.

## 7. Checklist and Validation Protocols

* After implementing a feature in the checklist:
  * Mark the item as complete with `[x]` in `docs/checklist.md`
  * Update the "Phase X Status" and percentage in the summary table
  * Update the "Current Implementation Stage" and "Next Steps Priority" 
* For each feature implementation:
  * Create validation protocols that detail how to test the feature
  * Document edge cases and expected behavior
  * These protocols help ensure quality and make testing easier

**Remember**: Documentation is as important as code. Keeping the checklist and validation protocols updated ensures everyone knows the project's status.


