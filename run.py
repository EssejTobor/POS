#!/usr/bin/env python3
"""Entry point for the POS application."""

# Due to import issues with Textual UI, use CLI for now
from src.cli import main
main()

# Commented out until Textual UI issues are resolved
# try:
#     from src.textual_ui import TextualApp
# except ImportError as exc:  # pragma: no cover - fallback when Textual missing
#     print("??  Textual missing, dropping to CLI:", exc)
#     from src.cli import main
#
#     main()
# else:
#     TextualApp().run()
