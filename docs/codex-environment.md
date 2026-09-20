# Codex Cloud environment

## Settings

After these repository changes are committed and pushed to the branch used by
the cloud environment, configure:

| Setting | Value |
| --- | --- |
| Container | Universal |
| Python runtime | 3.13 |
| Setup script | `uv sync --locked --all-groups --all-extras` |
| Maintenance script | `uv sync --locked --all-groups --all-extras` |
| Environment variables / secrets | None required |
| Additional system packages | None required |

Run the scripts from the repository root. The same command also works locally on
Windows. `uv` creates `.venv` and installs the project with its CLI entry point.
Use `uv run --locked ...` during tasks; virtual environment activation is not needed.
Python's patch version may differ across machines; `.python-version` selects 3.13.

The setup phase has internet access for installation. Agent internet access is
optional for running installed tools and tests. If enabled for documentation
research, use trusted domains and GET/HEAD/OPTIONS as appropriate.

Codex caches setup from the repository's default branch, then runs maintenance
after checking out the task branch. Put these files on the default branch before
using the locked setup command. A default branch with the old dependency files
will not work with this setup. See the
[official environment documentation](https://learn.chatgpt.com/docs/environments/cloud-environment).

## Branch naming

The local `origin/HEAD` recorded during preparation points to `legacy-public`.
This is an ordinary branch name, not a Codex mode. Its recorded difference from
`main` consists of LICENSE and README additions. Confirm the current GitHub state
before making `main` the default, and preserve the license/public documentation
changes when reconciling branches. No branch was deleted, merged, or changed on
GitHub as part of this environment preparation.

## Verification

Check dependency consistency and imports without launching the application:

```bash
uv lock --check
uv run --locked python -c "import src.cli, src.models, src.schemas"
uv build
```

The tests instantiate the CLI, which can open a database relative to the working
directory. Run them in a temporary directory to isolate that default database.
`test_phase45.py` additionally creates `data/db/test_work_items.db` inside the
checkout using an absolute path; use a disposable checkout if that file contains
anything you want to preserve.
In the Linux cloud container, after syncing:

```bash
repo="$PWD"
test_dir="$(mktemp -d)"
(cd "$test_dir" && "$repo/.venv/bin/python" -m pytest "$repo/tests" -q -p no:cacheprovider)
```

Keep tests out of setup/maintenance scripts: application failures should not
prevent the development environment from starting.

The preparation run on native Windows / Python 3.13.2 passed locked sync,
application imports, console entry-point loading, and source/wheel builds.
The existing suite produced **23 passed, 7 failed**: the `add_thought` command,
link-tree option/depth behavior, and duplicate generated item IDs caused failures.
Application and test code were left unchanged. A Linux container run remains to
be verified; Docker was not running locally.

## Dependency maintenance

Runtime dependencies are Pydantic and Rich. Textual is retained as an optional
`tui` extra. Pytest, mypy, and Ruff are in the `dev` dependency group.
The stale `setup.py` and hand-maintained `requirements.txt` were removed.
If a downstream tool needs requirements format, generate it with `uv export`.
See [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/).
