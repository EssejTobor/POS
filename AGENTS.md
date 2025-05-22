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

## 2. "First-Principles" Validation Workflow
*No external test frameworks required.*

### Core Validation Principles

1. **Self-Validating Scripts**:
   - Use the built-in validation framework in `src/pos_tui/validation/`
   - Each feature should have validation protocols in the appropriate module

2. **Runtime Introspection**:
   - Use `src/pos_tui/validation/introspect.py` for database inspection
   - Compare system state before and after operations

3. **UI Component Simulation**:
   - Use `UIComponentSimulator` to validate UI components without rendering
   - Verify properties, methods, and event handling

### Running Validations

The validation framework provides a command-line interface:
```bash
# Run all validation protocols
python -m src.pos_tui.validation.run

# List available protocols
python -m src.pos_tui.validation.run --list

# Run specific protocols
python -m src.pos_tui.validation.run item_editing edit_modal
```

### Creating New Validation Protocols

To create a new validation protocol:

1. Create a new subclass of `ValidationProtocol`
2. Implement the `_run_validation()` method
3. Register the protocol in `src/pos_tui/validation/run.py`

Example:
```python
from src.pos_tui.validation import ValidationProtocol

class MyFeatureValidation(ValidationProtocol):
    def __init__(self):
        super().__init__("my_feature")
    
    def _run_validation(self) -> None:
        # Implement validation logic
        # Use self.result.add_pass(), self.result.add_fail(), etc.
```

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

# 2. Run validation protocols
python -m src.pos_tui.validation.run

# 3. Re-run the application
python -m pos_tui.app
# -> no crash? commit
git commit -am "fix: remove stray debug print"

# 4. Repeat
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
  * Create validation protocols that detail expected behavior
  * Implement corresponding validation scripts in `src/pos_tui/validation/`
  * Document validation results in `docs/validation_protocols.md`

**Remember**: Validation is as important as implementation. Every feature should have a corresponding validation protocol that can verify its functionality without relying on external frameworks.


