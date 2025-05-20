#!/usr/bin/env python3
"""Entry point for the POS application."""


def _main() -> None:
    """Launch the Textual UI or fall back to the CLI."""
    try:
        from src.textual_ui import TextualApp
    except Exception as exc:  # pragma: no cover - fallback when Textual missing
        print("Textual UI unavailable, falling back to CLI:", exc)
        from src.cli import main as cli_main

        cli_main()
    else:
        TextualApp().run()


if __name__ == "__main__":
    _main()
