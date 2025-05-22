"""
Runner script for all POS TUI validations.

This script runs all the validation protocols in the framework
and reports the results.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import (
    ItemCreationValidation,
    ItemCreationViaFormValidation,
    ItemEditingValidation,
    OptimisticUIValidation,
    UIComponentsValidation,
    LinkManagementValidation,
    LinkNavigationValidation,
    TreeVisualizationValidation
)


def run_all_validations():
    """Run all validation protocols."""
    print("=" * 80)
    print("RUNNING POS TUI VALIDATIONS")
    print("=" * 80)
    
    validations = [
        # Phase 1-2 validations
        UIComponentsValidation(),

        # Phase 3 validations
        ItemCreationValidation(),
        ItemCreationViaFormValidation(),
        ItemEditingValidation(),
        OptimisticUIValidation(),
        
        # Phase 4 validations
        LinkManagementValidation(),
        LinkNavigationValidation(),
        
        # Phase 5 validations
        TreeVisualizationValidation(),
    ]
    
    results = []
    
    for validation in validations:
        print(f"\nRunning validation: {validation.name}")
        result = validation.run()
        validation.print_results()
        filepath = validation.save_results()
        results.append((validation.name, result.passed, filepath))
    
    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for name, passed, filepath in results:
        status = "PASS" if passed else "FAIL"
        all_passed = all_passed and passed
        print(f"{name}: {status}")
        print(f"  Results saved to: {filepath}")
    
    print("\n" + "=" * 80)
    print(f"OVERALL RESULT: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1) 