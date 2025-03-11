#!/usr/bin/env python3
"""
Entry point for the POS (Personal Operating System) application.
"""
import logging
from src.config import Config
from src.app import POSApp

def main():
    """Main entry point for the application"""
    # Now initialize the application
    app = POSApp()
    app.run()

if __name__ == "__main__":
    main() 