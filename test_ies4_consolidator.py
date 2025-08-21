#!/usr/bin/env python3
"""
Comprehensive unit tests for the enhanced IES4 Consolidator.

Tests cover IES4 r4.3.0 compliance, nested folder support, metadata preservation,
version management, and error handling.
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ies4_consolidator import IES4Consolidator


class TestIES4Consolidator(unittest.TestCase):
    """Test suite for enhanced IES4 Consolidator functionality."""

    def setUp(self):
        """Set up test environment with temporary directories and test data."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create test directory structure
        self.data_path = self.test_path / "data"
        self.data_path.mkdir()

        # Create nested country folders
        (self.data_path / "uk" / "army").mkdir(parents=True)
        (self.data_path / "uk" / "navy").mkdir(parents=True)
        (self.data_path / "iran").mkdir()

        # Create test JSON files
        self._create_test_files()

        # Initialize consolidator
        self.consolidator = IES4Consolidator(str(self.test_path))

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def _create_test_files(self):
        """Create test JSON files with various scenarios."""

        # UK Army file - basic structure
        uk_army_data = {
            "title": "UK Army Database",
            "ies4Version": "4.2.0",
            "vehicles": [
                {
                    "id": "uk-tank-001",
                    "type": "MainBattleTank",
                    "timestamp": "2024-12-01T10:00:00Z",
                    "version": "1.0",
                    "name": "Challenger 2",
                }
            ],
            "vehicleTypes": [
                {
                    "id": "type-001",
                    "type": "VehicleType",
                    "timestamp": "2024-12-01T09:00:00Z",
                    "version": "1.0",
                    "name": "Tank",
                }
            ],
        }

        # UK Navy file - with new entity types
        uk_navy_data = {
            "title": "UK Navy Database",
            "ies4Version": "4.3.0",
            "vehicles": [
                {
                    "id": "uk-ship-001",
                    "type": "Destroyer",
                    "timestamp": "2024-12-01T11:00:00Z",
                    "version": "1.0",
                    "name": "HMS Daring",
                }
            ],
            "facilities": [
                {
                    "id": "uk-base-001",
                    "type": "NavalBase",
                    "timestamp": "2024-12-01T08:00:00Z",
                    "version": "1.0",
                    "name": "Portsmouth",
                }
            ],
        }

        # Iran file 1 - older version
        iran_v1_data = {
            "title": "Iran Database v1",
            "ies4Version": "4.1.0",
            "vehicles": [
                {
                    "id": "iran-drone-001",
                    "type": "Drone",
                    "timestamp": "2024-11-01T10:00:00Z",
                    "version": "1.0",
                    "name": "Shahed-136",
                }
            ],
        }

        # Iran file 2 - newer version with updates
        iran_v2_data = {
            "title": "Iran Database v2",
            "ies4Version": "4.3.0",
            "vehicles": [
                {
                    "id": "iran-drone-001",
                    "type": "Drone",
                    "timestamp": "2024-12-01T10:00:00Z",
                    "version": "2.0",
                    "name": "Shahed-136 Enhanced",
                },
                {
                    "id": "iran-drone-002",
                    "type": "Drone",
                    "timestamp": "2024-12-01T11:00:00Z",
                    "version": "1.0",
                    "name": "Mohajer-10",
                },
            ],
            "organizations": [
                {
                    "id": "iran-org-001",
                    "type": "MilitaryOrganization",
                    "timestamp": "2024-12-01T09:00:00Z",
                    "version": "1.0",
                    "name": "IRGC",
                }
            ],
        }

        # Invalid JSON file for error testing
        invalid_data = "{ invalid json content"

        # Write test files
        with open(self.data_path / "uk" / "army" / "army_data.json", "w") as f:
            json.dump(uk_army_data, f, indent=2)

        with open(self.data_path / "uk" / "navy" / "navy_data.json", "w") as f:
            json.dump(uk_navy_data, f, indent=2)

        with open(self.data_path / "iran" / "iran_v1.json", "w") as f:
            json.dump(iran_v1_data, f, indent=2)

        with open(self.data_path / "iran" / "iran_v2.json", "w") as f:
            json.dump(iran_v2_data, f, indent=2)

        with open(self.data_path / "iran" / "invalid.json", "w") as f:
            f.write(invalid_data)

    def test_initialization(self):
        """Test consolidator initialization with IES4 r4.3.0 settings."""
        self.assertEqual(self.consolidator.ies4_version, "4.3.0")
        self.assertEqual(self.consolidator.ies4_spec_date, "2024-12-16")
        self.assertIn("organizations", self.consolidator.entity_types)
        self.assertIn("facilities", self.consolidator.entity_types)
        self.assertIn("events", self.consolidator.entity_types)

    def test_enhanced_folder_discovery(self):
        """Test enhanced folder discovery with nested structures."""
        folders = self.consolidator._discover_country_folders()

        # Should find 3 folders: iran, uk/army, uk/navy
        self.assertEqual(len(folders), 3)

        folder_names = [str(f.relative_to(self.data_path)) for f in folders]
        self.assertIn("iran", folder_names)
        self.assertIn("uk/army", folder_names)
        self.assertIn("uk/navy", folder_names)

    def test_nested_folder_discovery(self):
        """Test specific nested folder discovery functionality."""
        uk_folder = self.data_path / "uk"
        nested_folders = self.consolidator._discover_nested_folders(uk_folder)

        self.assertEqual(len(nested_folders), 2)
        folder_names = [f.name for f in nested_folders]
        self.assertIn("army", folder_names)
        self.assertIn("navy", folder_names)

    def test_ies4_compliance_validation(self):
        """Test IES4 r4.3.0 compliance validation."""
        # Valid data
        valid_data = {
            "vehicles": [
                {
                    "id": "test-001",
                    "type": "Tank",
                    "timestamp": "2024-12-01T10:00:00Z",
                    "version": "1.0",
                }
            ]
        }

        errors = self.consolidator._validate_ies4_compliance(valid_data)
        self.assertEqual(len(errors), 0)

        # Invalid data - missing required fields
        invalid_data = {
            "vehicles": [
                {
                    "id": "test-001"
                    # Missing type, timestamp, version
                }
            ]
        }

        errors = self.consolidator._validate_ies4_compliance(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Missing required field" in error for error in errors))

    def test_timestamp_validation(self):
        """Test timestamp validation functionality."""
        # Valid timestamps
        valid_timestamps = [
            "2024-12-01T10:00:00Z",
            "2024-12-01T10:00:00+00:00",
            "2024-12-01T10:00:00.123Z",
        ]

        for timestamp in valid_timestamps:
            self.assertTrue(self.consolidator._validate_timestamp(timestamp))

        # Invalid timestamps
        invalid_timestamps = [
            "invalid-timestamp",
            "2024-13-01T10:00:00Z",  # Invalid month
            "not-a-date",
            None,
            123,
        ]

        for timestamp in invalid_timestamps:
            self.assertFalse(self.consolidator._validate_timestamp(timestamp))

    def test_version_comparison(self):
        """Test version comparison functionality."""
        # Test version comparisons
        self.assertEqual(self.consolidator._compare_versions("2.0", "1.0"), 1)
        self.assertEqual(self.consolidator._compare_versions("1.0", "2.0"), -1)
        self.assertEqual(self.consolidator._compare_versions("1.0", "1.0"), 0)
        self.assertEqual(self.consolidator._compare_versions("1.2.3", "1.2.1"), 1)

    def test_consolidation_with_version_management(self):
        """Test consolidation with entity version management."""
        results = self.consolidator.consolidate_by_country()

        # All consolidations should succeed
        self.assertTrue(all(results.values()))

        # Check Iran consolidation (has version conflicts)
        iran_file = self.consolidator.output_path / "ies4_iran_consolidated.json"
        self.assertTrue(iran_file.exists())

        with open(iran_file, "r") as f:
            iran_data = json.load(f)

        # Should have 2 vehicles (iran-drone-001 updated to v2.0, iran-drone-002 added)
        self.assertEqual(len(iran_data["vehicles"]), 2)

        # Check that iran-drone-001 was updated to version 2.0
        drone_001 = next(
            v for v in iran_data["vehicles"] if v["id"] == "iran-drone-001"
        )
        self.assertEqual(drone_001["version"], "2.0")
        self.assertEqual(drone_001["name"], "Shahed-136 Enhanced")

    def test_enhanced_metadata_preservation(self):
        """Test comprehensive metadata preservation."""
        results = self.consolidator.consolidate_by_country()

        # Check consolidated file metadata
        iran_file = self.consolidator.output_path / "ies4_iran_consolidated.json"
        with open(iran_file, "r") as f:
            iran_data = json.load(f)

        # Check IES4 r4.3.0 metadata
        self.assertEqual(iran_data["ies4Version"], "4.3.0")
        self.assertEqual(iran_data["specificationDate"], "2024-12-16")

        # Check consolidation metadata
        metadata = iran_data["consolidationMetadata"]
        self.assertEqual(metadata["toolVersion"], "2.0")
        self.assertEqual(metadata["sourceFileCount"], 3)  # Including invalid file
        self.assertIn("timestamp", metadata)
        self.assertIn("consolidatedFiles", metadata)
        self.assertIn("entityCounts", metadata)

        # Check source version tracking
        self.assertIn("sourceVersions", metadata)

    def test_single_file_enhancement(self):
        """Test single file enhancement with metadata."""
        # Test UK Army (single file)
        army_file = self.consolidator.output_path / "ies4_uk_army_consolidated.json"

        # Run consolidation
        self.consolidator.consolidate_by_country()

        self.assertTrue(army_file.exists())

        with open(army_file, "r") as f:
            army_data = json.load(f)

        # Should have enhanced metadata even for single file
        self.assertEqual(army_data["ies4Version"], "4.3.0")
        self.assertIn("consolidationMetadata", army_data)
        self.assertEqual(army_data["consolidationMetadata"]["sourceFileCount"], 1)

    def test_error_handling(self):
        """Test error handling for invalid files."""
        results = self.consolidator.consolidate_by_country()

        # Iran should still succeed despite invalid.json file
        self.assertTrue(results.get("iran", False))

    def test_output_file_naming(self):
        """Test proper output file naming for nested folders."""
        results = self.consolidator.consolidate_by_country()

        expected_files = [
            "ies4_iran_consolidated.json",
            "ies4_uk_army_consolidated.json",
            "ies4_uk_navy_consolidated.json",
        ]

        for filename in expected_files:
            file_path = self.consolidator.output_path / filename
            self.assertTrue(file_path.exists(), f"Expected file {filename} not found")

    def test_summary_report_generation(self):
        """Test generation of comprehensive summary report."""
        results = self.consolidator.consolidate_by_country()
        self.consolidator.generate_summary_report(results)

        report_file = self.consolidator.output_path / "consolidation_report.txt"
        self.assertTrue(report_file.exists())

        with open(report_file, "r") as f:
            report_content = f.read()

        self.assertIn("IES4 JSON Consolidation Summary Report", report_content)
        self.assertIn("Total Countries/Regions Processed: 3", report_content)
        self.assertIn("IRAN: ✓ SUCCESS", report_content)
        self.assertIn("UK_ARMY: ✓ SUCCESS", report_content)


if __name__ == "__main__":
    unittest.main()
