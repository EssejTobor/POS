"""
Validation runner for the POS application.

This script runs all validation protocols and reports the results.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import ValidationResult, enable_validation_mode
from src.pos_tui.validation.item_management import ItemEditingValidation
from src.pos_tui.validation.ui_components import (
    EditItemModalValidation,
    ItemTableValidation,
    ConfirmModalValidation,
    DetailScreenValidation,
)
from src.pos_tui.validation.link_widget import LinkedItemsWidgetValidation
from src.pos_tui.validation.links import LinkValidation
from src.pos_tui.validation.link_tree import LinkTreeValidation


def run_selected_validations(validation_names: List[str] = None) -> Dict[str, ValidationResult]:
    """
    Run selected validation protocols.
    
    Args:
        validation_names: List of validation protocol names to run. If None, run all.
        
    Returns:
        Dictionary of validation results keyed by validation name
    """
    # Available validation protocols
    validation_protocols = {
        "item_editing": ItemEditingValidation,
        "edit_modal": EditItemModalValidation,
        "item_table": ItemTableValidation,
        "confirm_modal": ConfirmModalValidation,
        "detail_screen": DetailScreenValidation,
        "linked_items_widget": LinkedItemsWidgetValidation,
        "link_validation": LinkValidation,
        "link_tree": LinkTreeValidation,
        # Add more validation protocols here as they are implemented
    }
    
    # Filter protocols by name if specified
    if validation_names:
        protocols_to_run = {name: protocol for name, protocol in validation_protocols.items() 
                            if name in validation_names}
    else:
        protocols_to_run = validation_protocols
    
    if not protocols_to_run:
        print(f"Error: No matching validation protocols found. Available: {', '.join(validation_protocols.keys())}")
        return {}
    
    # Enable validation mode
    enable_validation_mode()
    
    # Run each protocol and collect results
    results = {}
    for name, protocol_class in protocols_to_run.items():
        print(f"\n{'='*20} Running {name} validation {'='*20}\n")
        
        # Instantiate and run the protocol
        protocol = protocol_class()
        result = protocol.validate()
        
        results[name] = result
    
    return results


def summarize_results(results: Dict[str, ValidationResult]) -> None:
    """
    Print a summary of all validation results.
    
    Args:
        results: Dictionary of validation results
    """
    if not results:
        print("\nNo validation results to summarize.")
        return
    
    print("\n" + "="*80)
    print(f"VALIDATION SUMMARY ({len(results)} protocols)")
    print("="*80)
    
    # Count overall statistics
    total_pass = 0
    total_fail = 0
    total_warn = 0
    
    for name, result in results.items():
        total_pass += len(result.passed)
        total_fail += len(result.failed)
        total_warn += len(result.warnings)
    
    # Print summary table
    print(f"\nTotal checks: {total_pass + total_fail}")
    print(f"Passed: {total_pass}")
    print(f"Failed: {total_fail}")
    print(f"Warnings: {total_warn}")
    
    # Print status of each validation
    print("\nProtocol Status:")
    print("-"*80)
    print(f"{'Protocol':<30} {'Status':<10} {'Pass':<8} {'Fail':<8} {'Warn':<8}")
    print("-"*80)
    
    for name, result in results.items():
        status = "SUCCESS" if result.success else "FAILURE"
        print(f"{name:<30} {status:<10} {len(result.passed):<8} {len(result.failed):<8} {len(result.warnings):<8}")
    
    # Print failure details if any
    failures = [(name, fail) for name, result in results.items() 
                for fail in result.failed]
    
    if failures:
        print("\nFailure Details:")
        print("-"*80)
        for name, failure in failures:
            print(f"[{name}] {failure}")
    
    print("\n" + "="*80)
    print(f"OVERALL STATUS: {'SUCCESS' if total_fail == 0 else 'FAILURE'}")
    print("="*80)


def main() -> int:
    """
    Run the validation protocols specified by command line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failures)
    """
    parser = argparse.ArgumentParser(description="Run validation protocols for the POS application")
    parser.add_argument("protocols", nargs="*", help="Specific protocols to run (default: all)")
    parser.add_argument("--list", action="store_true", help="List available validation protocols")
    args = parser.parse_args()
    
    # List available protocols if requested
    if args.list:
        # This matches the protocols defined in run_selected_validations
        available_protocols = [
            "item_editing",
            "edit_modal",
            "item_table",
            "confirm_modal",
            "detail_screen",
            "linked_items_widget",
            "link_validation",
            "link_tree",
            # Add more as implemented
        ]
        
        print("Available validation protocols:")
        for protocol in available_protocols:
            print(f"  - {protocol}")
        return 0
    
    # Run validations
    results = run_selected_validations(args.protocols if args.protocols else None)
    
    # Summarize results
    summarize_results(results)
    
    # Return success if all validations passed
    return 0 if all(result.success for result in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main()) 