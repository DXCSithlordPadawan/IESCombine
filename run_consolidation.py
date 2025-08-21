#!/usr/bin/env python3
"""
Simple runner script for IES4 JSON consolidation.

This script provides an easy way to run the consolidation process
with different options and configurations.
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ies4_consolidator import IES4Consolidator
except ImportError as e:
    print(f"Error importing consolidator: {e}")
    print("Make sure ies4_consolidator.py is in the same directory.")
    sys.exit(1)


def main():
    """
    Main execution with command line argument parsing.
    """
    parser = argparse.ArgumentParser(
        description="Consolidate IES4 JSON files by country/region"
    )

    parser.add_argument(
        "--base-path",
        default="C:\\ies4-military-database-analysis",
        help=(
            "Base path for the analysis "
            "(default: C:\\ies4-military-database-analysis)"
        ),
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run without saving files"
    )

    args = parser.parse_args()

    # Validate base path exists
    base_path = Path(args.base_path)
    if not base_path.exists():
        print(f"Error: Base path does not exist: {base_path}")
        sys.exit(1)

    print("IES4 JSON Consolidator")
    print(f"Base Path: {base_path}")
    print(f"Data Path: {base_path / 'data'}")
    print(f"Output Path: {base_path / 'output' / 'consolidated'}")
    print("-" * 50)

    if args.dry_run:
        print("DRY RUN MODE - No files will be saved")
        print("-" * 50)

    try:
        # Initialize consolidator
        consolidator = IES4Consolidator(str(base_path))

        if args.dry_run:
            # For dry run, just discover and report
            country_folders = consolidator._discover_country_folders()
            print(f"Found {len(country_folders)} country folders:")
            for folder in country_folders:
                json_files = list(folder.glob("*.json"))
                print(f"  {folder.name}: {len(json_files)} JSON files")
            return

        # Run actual consolidation
        print("Starting consolidation process...")
        results = consolidator.consolidate_by_country()

        # Generate and display summary
        consolidator.generate_summary_report(results)

        # Return appropriate exit code
        failed_count = sum(1 for success in results.values() if not success)
        if failed_count > 0:
            print(f"\nWarning: {failed_count} consolidations failed.")
            sys.exit(1)
        else:
            print("\nAll consolidations completed successfully!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
