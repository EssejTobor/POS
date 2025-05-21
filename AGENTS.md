# Agent Guide  — POS Repository

## 0  Environment facts
- Code executes in **`/workspace/POS`** inside a disposable container built from the Codex base image.  
- **Internet is already disabled** when this file is parsed; any command that tries to reach PyPI or the web will fail. 

## Tools that are guaranteed to exist
| Tool            | Notes |
|-----------------|-------|
| `python` 3.12   | System interpreter |
| `pytest`        | Unit-test runner |
| `black`, `isort`, `ruff`, `mypy` | Formatting / lint / type-check |
| `sqlite3`       | Local DB CLI |

No external package manager (pip, uv, apt, etc.) can download packages once the sandbox is online. 


## Allowed / disallowed shell commands

* **Allowed:** `python`, `pytest`, `black`, `isort`, `ruff`, `mypy`, `sqlite3`, simple `bash` built-ins.
* **Disallowed:** networked package managers (`pip install …`), `curl`, `wget`, `docker`, or any command that contacts the outside world.

## Coding standards
| Step | Command | Rule |
|------|---------|------|
| Format | `black .` | default settings |
| Sort imports | `isort .` | profile = black, blank-line *after* third-party & project imports |
| Lint | `ruff .` | fail only on E,F,W,I,B,UP rules |
| Type-check | `mypy src/` | `--strict`, `ignore_missing_imports = true` |

Run those four before every commit.

## Test discipline
```bash
python -m pytest -q tests/ || true  # never abort the job