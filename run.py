#!/usr/bin/env python3
"""Entry point for the POS application."""

try:
    from src.textual_ui import TextualApp
except ImportError as exc:  # pragma: no cover - fallback when Textual missing
    print("??  Textual missing, dropping to CLI:", exc)
    from src.cli import main

    main()
else:
    TextualApp().run()
