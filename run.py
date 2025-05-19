#!/usr/bin/env python3
"""
Entry point for POS – launches the Textual UI.
Falls back to CLI if Textual import ever fails.
"""
try:
    from src.textual_ui import TextualApp
    TextualApp().run()
except ImportError as exc:
    print("??  Textual missing, dropping to CLI:", exc)
    from src.cli import main
    main() 