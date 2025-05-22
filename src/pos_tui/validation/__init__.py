"""
Validation framework for the POS application.

This module provides a first-principles approach to code validation
without relying on external testing frameworks.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("validation")

# Constants
VALIDATION_MODE = os.environ.get("POS_VALIDATION_MODE", "0") == "1"
VALIDATION_RESULTS_DIR = Path("data") / "validation_results"

# Create results directory if it doesn't exist
VALIDATION_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self, name: str):
        self.name = name
        self.timestamp = datetime.now()
        self.passed: List[str] = []
        self.failed: List[str] = []
        self.warnings: List[str] = []
        self.notes: List[str] = []
    
    @property
    def success(self) -> bool:
        """Return True if validation passed without failures."""
        return len(self.failed) == 0
    
    def add_pass(self, message: str) -> None:
        """Add a passed check."""
        self.passed.append(message)
        logger.info(f"✓ PASS: {message}")
    
    def add_fail(self, message: str) -> None:
        """Add a failed check."""
        self.failed.append(message)
        logger.error(f"✗ FAIL: {message}")
    
    def add_warning(self, message: str) -> None:
        """Add a warning."""
        self.warnings.append(message)
        logger.warning(f"⚠ WARNING: {message}")
    
    def add_note(self, message: str) -> None:
        """Add a note."""
        self.notes.append(message)
        logger.info(f"ℹ NOTE: {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "notes": self.notes,
        }
    
    def save(self) -> Path:
        """Save the validation result to disk."""
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.name}_{timestamp_str}.json"
        result_path = VALIDATION_RESULTS_DIR / filename
        
        with open(result_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return result_path
    
    def print_summary(self) -> None:
        """Print a summary of the validation results."""
        print("\n" + "=" * 80)
        print(f"VALIDATION RESULTS: {self.name}")
        print(f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        print(f"\nSTATUS: {'SUCCESS' if self.success else 'FAILURE'}")
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\nFAILURES:")
            for i, failure in enumerate(self.failed, 1):
                print(f"  {i}. {failure}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if self.notes:
            print("\nNOTES:")
            for i, note in enumerate(self.notes, 1):
                print(f"  {i}. {note}")
        
        print("\n" + "=" * 80)


class ValidationProtocol:
    """Base class for validation protocols."""
    
    def __init__(self, name: str):
        self.name = name
        self.result = ValidationResult(name)
    
    def validate(self) -> ValidationResult:
        """Run validation and return results."""
        try:
            self._run_validation()
        except Exception as e:
            self.result.add_fail(f"Validation protocol threw an exception: {str(e)}")
            import traceback
            self.result.add_note(f"Exception traceback: {traceback.format_exc()}")
        
        self.result.print_summary()
        self.result.save()
        return self.result
    
    def _run_validation(self) -> None:
        """Override this method to implement specific validation logic."""
        raise NotImplementedError("Subclasses must implement _run_validation()")


def enable_validation_mode() -> None:
    """Enable validation mode globally."""
    os.environ["POS_VALIDATION_MODE"] = "1"
    global VALIDATION_MODE
    VALIDATION_MODE = True
    logger.info("Validation mode enabled")


def disable_validation_mode() -> None:
    """Disable validation mode globally."""
    os.environ["POS_VALIDATION_MODE"] = "0"
    global VALIDATION_MODE
    VALIDATION_MODE = False
    logger.info("Validation mode disabled")


def is_validation_mode() -> bool:
    """Check if validation mode is enabled."""
    return VALIDATION_MODE 