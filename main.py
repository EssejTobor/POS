#!/usr/bin/env python3
"""Entry point for the POS application."""

import argparse
import sys
from typing import List, Optional


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Personal Operating System (POS)")
    parser.add_argument(
        "--cli", action="store_true", help="Run in legacy CLI mode (deprecated)"
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for the application."""
    args = parse_args(argv)

    try:
        if args.cli:
            # Legacy CLI mode (deprecated)
            print(
                "Warning: CLI mode is deprecated and will be removed in future versions."
            )
            from src.cli import main as cli_main

            cli_main()
        else:
            # Preferred Textual UI mode
            try:
                from src.pos_tui.app import main as tui_main

                tui_main()
            except ImportError as e:
                print(f"Error loading Textual UI: {e}")
                print("Falling back to CLI mode (deprecated)...")
                from src.cli import main as cli_main

                cli_main()
    except KeyboardInterrupt:
        print("\nExiting POS application. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main(sys.argv[1:])
