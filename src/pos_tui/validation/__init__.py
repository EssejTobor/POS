"""
First-principles validation framework for POS TUI.

This module provides a validation framework for TUI components that
verifies functionality through first-principles testing rather than
using external testing frameworks.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
import time

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
    
    def __init__(self):
        """Initialize the validation result container."""
        self.passes: List[str] = []
        self.failures: List[str] = []
        self.notes: List[str] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def add_pass(self, message: str) -> None:
        """Add a passing test result."""
        self.passes.append(message)
    
    def add_fail(self, message: str) -> None:
        """Add a failing test result."""
        self.failures.append(message)
    
    def add_note(self, message: str) -> None:
        """Add a note about the test execution."""
        self.notes.append(message)
    
    def start_timer(self) -> None:
        """Start timing the validation."""
        self.start_time = time.time()
    
    def stop_timer(self) -> None:
        """Stop timing the validation."""
        self.end_time = time.time()
    
    @property
    def duration(self) -> float:
        """Get the duration of the validation in seconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time
    
    @property
    def passed(self) -> bool:
        """Check if the validation passed (no failures)."""
        return len(self.failures) == 0
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Get a summary of the validation results."""
        return {
            "passed": self.passed,
            "pass_count": len(self.passes),
            "fail_count": len(self.failures),
            "duration": self.duration,
            "timestamp": datetime.now().isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation results to a dictionary."""
        return {
            "passed": self.passed,
            "passes": self.passes,
            "failures": self.failures,
            "notes": self.notes,
            "duration": self.duration,
            "timestamp": datetime.now().isoformat()
        }
    
    def to_json(self) -> str:
        """Convert the validation results to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, filepath: str) -> None:
        """Save the validation results to a JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json())


class ValidationProtocol:
    """Base class for validation protocols."""
    
    def __init__(self, name: str):
        """Initialize the validation protocol.
        
        Args:
            name: Name of the validation protocol
        """
        self.name = name
        self.result = ValidationResult()
    
    def run(self) -> ValidationResult:
        """Run the validation protocol.
        
        Returns:
            ValidationResult object containing the validation results
        """
        self.result.start_timer()
        try:
            self._run_validation()
        except Exception as e:
            self.result.add_fail(f"Validation failed with error: {str(e)}")
            import traceback
            self.result.add_note(traceback.format_exc())
        finally:
            self.result.stop_timer()
        
        return self.result
    
    def _run_validation(self) -> None:
        """Implement the validation logic in subclasses."""
        raise NotImplementedError("Subclasses must implement _run_validation")
    
    def print_results(self) -> None:
        """Print the validation results to the console."""
        print(f"\n=== Validation Results for {self.name} ===")
        
        print(f"\nDuration: {self.result.duration:.2f} seconds")
        
        if self.result.notes:
            print("\nNotes:")
            for note in self.result.notes:
                print(f"  - {note}")
        
        print(f"\nPassing Tests ({len(self.result.passes)}):")
        for i, msg in enumerate(self.result.passes, 1):
            print(f"  ✓ {i}. {msg}")
        
        if self.result.failures:
            print(f"\nFailing Tests ({len(self.result.failures)}):")
            for i, msg in enumerate(self.result.failures, 1):
                print(f"  ✗ {i}. {msg}")
        
        print(f"\nOverall Result: {'PASS' if self.result.passed else 'FAIL'}")
    
    def save_results(self, directory: str = None) -> str:
        """Save the validation results to a file.
        
        Args:
            directory: Directory to save the results in (default: data/validation_results)
            
        Returns:
            Path to the saved file
        """
        # Determine directory
        if directory is None:
            # Default to data/validation_results in the project root
            project_root = Path(__file__).parent.parent.parent.parent
            directory = project_root / "data" / "validation_results"
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.name}_{timestamp}.json"
        filepath = os.path.join(directory, filename)
        
        # Save results
        self.result.save_to_file(filepath)
        
        return filepath


# Import validation protocols
from .item_management import (
    ItemCreationValidation,
    ItemEditingValidation,
    OptimisticUIValidation,
    ItemCreationViaFormValidation,
)
from .ui_components import ItemFormValidation, UIComponentsValidation
from .item_links import LinkManagementValidation, LinkNavigationValidation
from .tree_visualization import TreeVisualizationValidation
from .navigation_validation import NavigationValidator, run_validation

__all__ = [
    "ValidationResult",
    "ValidationProtocol",
    "ItemCreationValidation",
    "ItemEditingValidation",
    "OptimisticUIValidation",
    "ItemCreationViaFormValidation",
    "ItemFormValidation",
    "UIComponentsValidation",
    "LinkManagementValidation",
    "LinkNavigationValidation",
    "TreeVisualizationValidation",
    "NavigationValidator",
    "run_validation"
]


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