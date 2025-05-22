#!/usr/bin/env python3
"""Entry point for the POS application."""

import sys
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> None:
    """Launch the Textual UI."""
    try:
        from src.pos_tui.app import main as tui_main

        tui_main()
    except KeyboardInterrupt:
        print("\nExiting POS application. Goodbye!")
    except Exception as e:  # pragma: no cover - top-level error
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main(sys.argv[1:])
