#!/usr/bin/env python3
"""Entry point for the POS application."""


def _main() -> None:
 
    try:
        from src.cli import main as cli_main

        cli_main()
        
main()
