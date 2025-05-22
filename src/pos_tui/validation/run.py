"""
Runner for validation protocols.

Provides CLI utilities for running validation protocols.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pos_tui.validation import (
    ValidationProtocol,
    ItemCreationValidation,
    ItemCreationViaFormValidation,
    ItemEditingValidation,
    OptimisticUIValidation,
    UIComponentsValidation,
    ItemListingAndViewingValidation,
    LinkManagementValidation,
    LinkNavigationValidation
)


def get_available_protocols() -> Dict[str, ValidationProtocol]:
    """Get all available validation protocols.
    
    Returns:
        Dictionary mapping protocol names to protocol instances
    """
    return {
        "item_creation": ItemCreationValidation(),
        "item_creation_via_form": ItemCreationViaFormValidation(),
        "item_editing": ItemEditingValidation(),
        "optimistic_ui": OptimisticUIValidation(),
        "ui_components": UIComponentsValidation(),
        "item_listing_and_viewing": ItemListingAndViewingValidation(),
        "link_management": LinkManagementValidation(),
        "link_navigation": LinkNavigationValidation(),
    }


def run_protocol(protocol_name: str) -> bool:
    """Run a specific validation protocol.
    
    Args:
        protocol_name: Name of the protocol to run
        
    Returns:
        True if the protocol passed, False otherwise
    """
    protocols = get_available_protocols()
    
    if protocol_name not in protocols:
        print(f"Error: Protocol '{protocol_name}' not found")
        print(f"Available protocols: {', '.join(protocols.keys())}")
        return False
    
    protocol = protocols[protocol_name]
    print(f"Running validation protocol: {protocol_name}")
    
    # Run the protocol
    result = protocol.run()
    protocol.print_results()
    
    # Save results
    result_path = protocol.save_results()
    print(f"Results saved to: {result_path}")
    
    return result.passed


def run_all_protocols() -> bool:
    """Run all validation protocols.
    
    Returns:
        True if all protocols passed, False otherwise
    """
    protocols = get_available_protocols()
    all_passed = True
    
    for name, protocol in protocols.items():
        print(f"\n\nRunning validation protocol: {name}")
        print("=" * 60)
        
        # Run the protocol
        result = protocol.run()
        protocol.print_results()
        
        # Save results
        result_path = protocol.save_results()
        print(f"Results saved to: {result_path}")
        
        # Update overall pass/fail status
        if not result.passed:
            all_passed = False
    
    return all_passed


def run_protocol_group(group_name: str) -> bool:
    """Run a group of related validation protocols.
    
    Args:
        group_name: Name of the protocol group to run
        
    Returns:
        True if all protocols in the group passed, False otherwise
    """
    # Define protocol groups
    groups = {
        "item": ["item_creation", "item_creation_via_form", "item_editing", "optimistic_ui"],
        "ui": ["ui_components", "item_listing_and_viewing"],
        "links": ["link_management", "link_navigation"],
    }
    
    if group_name not in groups:
        print(f"Error: Group '{group_name}' not found")
        print(f"Available groups: {', '.join(groups.keys())}")
        return False
    
    protocols = get_available_protocols()
    all_passed = True
    
    for protocol_name in groups[group_name]:
        if protocol_name not in protocols:
            print(f"Warning: Protocol '{protocol_name}' not found in available protocols")
            continue
        
        print(f"\n\nRunning validation protocol: {protocol_name}")
        print("=" * 60)
        
        # Run the protocol
        protocol = protocols[protocol_name]
        result = protocol.run()
        protocol.print_results()
        
        # Save results
        result_path = protocol.save_results()
        print(f"Results saved to: {result_path}")
        
        # Update overall pass/fail status
        if not result.passed:
            all_passed = False
    
    return all_passed


def main() -> int:
    """Run validation protocols based on command line arguments.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="Run validation protocols for POS TUI")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Run all validation protocols")
    group.add_argument("--protocol", type=str, help="Run a specific validation protocol")
    group.add_argument("--group", type=str, help="Run a group of related validation protocols")
    group.add_argument("--list", action="store_true", help="List available protocols and groups")
    
    args = parser.parse_args()
    
    if args.list:
        protocols = get_available_protocols()
        groups = {
            "item": ["item_creation", "item_editing", "optimistic_ui"],
            "ui": ["ui_components"],
            "links": ["link_management", "link_navigation"],
        }
        
        print("Available Validation Protocols:")
        for name in protocols.keys():
            print(f"  - {name}")
        
        print("\nAvailable Protocol Groups:")
        for name, protocols in groups.items():
            print(f"  - {name}: {', '.join(protocols)}")
        
        return 0
    
    if args.all:
        success = run_all_protocols()
    elif args.protocol:
        success = run_protocol(args.protocol)
    elif args.group:
        success = run_protocol_group(args.group)
    else:
        # This should not happen due to required=True
        print("Error: No action specified")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 