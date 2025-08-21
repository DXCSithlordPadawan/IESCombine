#!/usr/bin/env python3
"""
Test suite for the enhanced IES4 Consolidator v2.0
Tests all new functionality including nested folder support and IES4 r4.3.0 compliance.
"""

import json
import tempfile
import unittest
from pathlib import Path
from ies4_consolidator import IES4Consolidator


class TestIES4ConsolidatorEnhanced(unittest.TestCase):
    """Test suite for enhanced IES4 Consolidator functionality."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.consolidator = IES4Consolidator(str(self.base_path))

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def create_test_data(self):
        """Create comprehensive test data structure."""
        data_path = self.base_path / "data"
        data_path.mkdir(exist_ok=True)

        # Create US main folder
        us_path = data_path / "us"
        us_path.mkdir(exist_ok=True)

        us_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "US Military Data",
            "version": "4.3.0",
            "countries": [
                {
                    "id": "us-001",
                    "type": "country", 
                    "name": "United States",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ],
            "vehicles": [
                {
                    "id": "us-tank-001",
                    "type": "tank",
                    "name": "M1A2 Abrams",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }

        with open(us_path / "us_main.json", "w") as f:
            json.dump(us_data, f, indent=2)

        # Create US Army subfolder
        us_army_path = us_path / "army"
        us_army_path.mkdir(exist_ok=True)

        army_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "US Army Data",
            "version": "4.3.0",
            "vehicles": [
                {
                    "id": "us-army-001",
                    "type": "ifv",
                    "name": "Bradley IFV",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ],
            "people": [
                {
                    "id": "us-army-p001",
                    "type": "officer",
                    "name": "General Johnson",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }

        with open(us_army_path / "army_vehicles.json", "w") as f:
            json.dump(army_data, f, indent=2)

        # Create UK folder with multiple files (for merge testing)
        uk_path = data_path / "uk"
        uk_path.mkdir(exist_ok=True)

        uk_vehicles = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "UK Vehicles Database",
            "version": "4.3.0",
            "vehicles": [
                {
                    "id": "uk-tank-001",
                    "type": "tank",
                    "name": "Challenger 2",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }

        uk_personnel = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "UK Personnel Database",
            "version": "4.3.0",
            "people": [
                {
                    "id": "uk-person-001",
                    "type": "officer",
                    "name": "Colonel Smith",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }

        with open(uk_path / "uk_vehicles.json", "w") as f:
            json.dump(uk_vehicles, f, indent=2)

        with open(uk_path / "uk_personnel.json", "w") as f:
            json.dump(uk_personnel, f, indent=2)

    def test_nested_folder_discovery(self):
        """Test discovery of nested subfolders."""
        self.create_test_data()
        
        folders = self.consolidator._discover_country_folders()
        folder_paths = [f.relative_to(self.consolidator.data_path) for f in folders]
        
        # Should find main folders and nested subfolders
        expected_folders = {Path("us"), Path("us/army"), Path("uk")}
        actual_folders = set(folder_paths)
        
        self.assertEqual(actual_folders, expected_folders)
        self.assertEqual(len(folders), 3)

    def test_consolidation_with_nested_folders(self):
        """Test full consolidation process with nested folders."""
        self.create_test_data()
        
        results = self.consolidator.consolidate_by_country()
        
        # Should process all folders successfully
        self.assertEqual(len(results), 3)
        self.assertIn("us", results)
        self.assertIn("us_army", results)  # Nested folder naming
        self.assertIn("uk", results)
        
        # All should succeed
        for country, success in results.items():
            self.assertTrue(success, f"Consolidation failed for {country}")

    def test_enhanced_metadata_generation(self):
        """Test that enhanced metadata is generated correctly."""
        self.create_test_data()
        
        # Test with multi-file consolidation (UK)
        results = self.consolidator.consolidate_by_country()
        
        uk_file = self.consolidator.output_path / "ies4_uk_consolidated.json"
        self.assertTrue(uk_file.exists())
        
        with open(uk_file) as f:
            data = json.load(f)
        
        # Check enhanced metadata
        self.assertIn("consolidation_metadata", data)
        meta = data["consolidation_metadata"]
        
        self.assertIn("ies4_compliance_version", meta)
        self.assertEqual(meta["ies4_compliance_version"], "r4.3.0 2024-12-16")
        
        self.assertIn("source_files", meta)
        self.assertEqual(meta["total_source_files"], 2)
        
        self.assertIn("entity_counts", meta)
        self.assertIn("total_entities", meta)
        
        # Check source file tracking in entities
        for vehicle in data["vehicles"]:
            self.assertIn("_source_file", vehicle)
            self.assertIn("_consolidation_timestamp", vehicle)

    def test_ies4_r430_validation(self):
        """Test IES4 r4.3.0 specific validation features."""
        # Create data with missing required fields
        data_path = self.base_path / "data" / "test"
        data_path.mkdir(parents=True)
        
        invalid_data = {
            "title": "Invalid Data",
            # Missing $schema field
            "vehicles": [
                {
                    # Missing id and type fields
                    "name": "Test Vehicle"
                }
            ]
        }
        
        with open(data_path / "invalid.json", "w") as f:
            json.dump(invalid_data, f)
        
        # Validation should catch these issues
        is_valid = self.consolidator._validate_json_structure(invalid_data)
        self.assertFalse(is_valid)

    def test_duplicate_entity_handling(self):
        """Test handling of duplicate entities across files."""
        data_path = self.base_path / "data" / "duplicate_test"
        data_path.mkdir(parents=True)
        
        # Create two files with same entity ID
        data1 = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Data 1",
            "version": "4.3.0",
            "vehicles": [
                {
                    "id": "duplicate-001",
                    "type": "tank",
                    "name": "Tank from File 1",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }
        
        data2 = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Data 2", 
            "version": "4.3.0",
            "vehicles": [
                {
                    "id": "duplicate-001",
                    "type": "tank",
                    "name": "Tank from File 2",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }
        
        with open(data_path / "data1.json", "w") as f:
            json.dump(data1, f)
        with open(data_path / "data2.json", "w") as f:
            json.dump(data2, f)
        
        results = self.consolidator.consolidate_by_country()
        
        # Should consolidate successfully
        self.assertIn("duplicate_test", results)
        self.assertTrue(results["duplicate_test"])
        
        # Check output file
        output_file = self.consolidator.output_path / "ies4_duplicate_test_consolidated.json"
        with open(output_file) as f:
            data = json.load(f)
        
        # Should have only one vehicle (first one processed wins)
        self.assertEqual(len(data["vehicles"]), 1)
        # Due to file system ordering, we just check that it's one of the expected names
        vehicle_name = data["vehicles"][0]["name"]
        self.assertIn(vehicle_name, ["Tank from File 1", "Tank from File 2"])

    def test_single_file_enhancement(self):
        """Test that single files get enhanced with metadata."""
        data_path = self.base_path / "data" / "single"
        data_path.mkdir(parents=True)
        
        # Create single file without consolidation metadata
        single_data = {
            "title": "Single File Data",
            "version": "4.3.0",
            "vehicles": [
                {
                    "id": "single-001",
                    "type": "tank",
                    "name": "Single Tank",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }
        
        with open(data_path / "single.json", "w") as f:
            json.dump(single_data, f)
        
        results = self.consolidator.consolidate_by_country()
        
        output_file = self.consolidator.output_path / "ies4_single_consolidated.json"
        with open(output_file) as f:
            data = json.load(f)
        
        # Should have enhanced metadata even for single file
        self.assertIn("consolidation_metadata", data)
        self.assertIn("$schema", data)  # Should be auto-added
        
    def test_performance_monitoring(self):
        """Test that performance monitoring features work."""
        self.create_test_data()
        
        # Create a larger file to trigger size warning
        large_data_path = self.base_path / "data" / "large"
        large_data_path.mkdir(parents=True)
        
        # Create data that would be larger
        large_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Large Dataset",
            "version": "4.3.0",
            "vehicles": []
        }
        
        # Add many vehicles to make it larger
        for i in range(1000):
            large_data["vehicles"].append({
                "id": f"large-{i:04d}",
                "type": "vehicle",
                "name": f"Vehicle {i}",
                "timestamp": "2024-01-01T00:00:00Z",
                "description": "A" * 100  # Make each entity larger
            })
        
        with open(large_data_path / "large.json", "w") as f:
            json.dump(large_data, f, indent=2)
        
        # Run consolidation - should complete without errors
        results = self.consolidator.consolidate_by_country()
        
        # All consolidations should succeed
        for country, success in results.items():
            self.assertTrue(success, f"Failed to process {country}")


if __name__ == "__main__":
    unittest.main()