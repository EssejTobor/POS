"""
A simple script to verify Python environment
"""

import os
import sys

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir())

try:
    from src.models import ItemType

    print(f"Successfully imported {ItemType.__name__} from src.models")
except ImportError as e:
    print("Error importing from src.models:", str(e))
