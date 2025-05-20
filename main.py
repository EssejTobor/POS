"""Convenience entry point for the POS application."""

try:
    from src.textual_ui import TextualApp
except Exception as exc:  # pragma: no cover - fallback when Textual missing
    print("Textual UI unavailable, falling back to CLI:", exc)
    from src.cli import main

    if __name__ == "__main__":
        main()
else:
    if __name__ == "__main__":
        TextualApp().run()
