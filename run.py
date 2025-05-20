#!/usr/bin/env python3
"""Entry point for the POS application."""

try:
    # Attempt to launch the Textual-based UI first
    from src.textual_ui import TextualApp
except Exception as exc:  # pragma: no cover - fallback when Textual missing
    print("Textual UI unavailable, falling back to CLI:", exc)
    from src.cli import main

    main()
else:
    TextualApp().run()
