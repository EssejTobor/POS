"""
A simple script to verify Python environment
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir())

try:
    from src.models import ItemType

    logger.info("Successfully imported %s from src.models", ItemType.__name__)
except ImportError as e:
    print("Error importing from src.models:", str(e))
