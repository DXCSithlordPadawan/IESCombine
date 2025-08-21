#!/usr/bin/env python3
"""
IES4 Military Database JSON File Consolidator v2.0

This script examines the data folder structure and combines multiple JSON files
per country subfolder into single IES4 r4.3.0 compliant files with enhanced
metadata, nested folder support, and improved validation.

Features:
- Full IES4 r4.3.0 compliance with enhanced validation
- Nested subfolder support (e.g., data/uk/army/, data/uk/navy/)
- Enhanced metadata preservation and source file tracking
- Performance monitoring and progress tracking
- Comprehensive audit trails and compliance reporting
- Improved error handling and recovery mechanisms

Author: Military Database Analysis System
Version: 2.0 (IES4 r4.3.0 Enhanced)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import jsonschema
from collections import defaultdict
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ies4_consolidator.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class IES4Consolidator:
    """
    Main class for consolidating IES4-compliant JSON files by country/region.
    """

    def __init__(self, base_path: str = "C:\\ies4-military-database-analysis"):
        """
        Initialize the consolidator with base path.

        Args:
            base_path (str): Base directory path for the analysis
        """
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.schema_path = self.base_path / "ies4_json_schema.json"
        self.output_path = self.base_path / "output" / "consolidated"

        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Load IES4 schema for validation
        self.schema = self._load_schema()

        # IES4 entity types that can be consolidated
        self.entity_types = [
            "countries",
            "areas",
            "vehicles",
            "vehicleTypes",
            "peopleTypes",
            "people",
            "representations",
        ]

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load the IES4 JSON schema for validation.

        Returns:
            Dict containing the schema or None if loading fails
        """
        try:
            if self.schema_path.exists():
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                logger.info(f"Loaded IES4 schema from {self.schema_path}")
                return schema
            else:
                logger.warning(f"Schema file not found at {self.schema_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            return None

    def _validate_json_structure(self, data: Dict[str, Any]) -> bool:
        """
        Enhanced validation of JSON data against IES4 r4.3.0 schema requirements.

        Args:
            data (Dict): JSON data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        validation_errors = []

        # Basic schema validation if available
        if self.schema:
            try:
                jsonschema.validate(data, self.schema)
            except jsonschema.ValidationError as e:
                validation_errors.append(f"Schema validation: {e.message}")
            except Exception as e:
                validation_errors.append(f"Validation error: {e}")

        # Enhanced IES4 r4.3.0 compliance checks
        try:
            # Check for required top-level fields
            required_fields = ["$schema", "title"]
            for field in required_fields:
                if field not in data:
                    validation_errors.append(f"Missing required field: {field}")

            # Check version compliance
            if "version" in data and data["version"] != "4.3.0":
                logger.warning(
                    f"Version mismatch: found {data.get('version')}, " "expected 4.3.0"
                )

            # Validate entity types and their required fields
            for entity_type in self.entity_types:
                if entity_type in data and isinstance(data[entity_type], list):
                    for i, entity in enumerate(data[entity_type]):
                        if not isinstance(entity, dict):
                            validation_errors.append(
                                f"{entity_type}[{i}]: must be an object"
                            )
                            continue

                        # Check required entity fields for IES4 r4.3.0
                        if "id" not in entity:
                            validation_errors.append(
                                f"{entity_type}[{i}]: missing required 'id' field"
                            )

                        if "type" not in entity:
                            validation_errors.append(
                                f"{entity_type}[{i}]: missing required 'type' field"
                            )

                        # Check timestamp field (required in r4.3.0)
                        if "timestamp" not in entity:
                            logger.warning(
                                f"{entity_type}[{i}] (id: {entity.get('id', 'unknown')}): "
                                "missing 'timestamp' field, will be added during processing"
                            )

            # Check consolidation metadata if present
            if "consolidation_metadata" in data:
                meta = data["consolidation_metadata"]
                required_meta_fields = ["created_timestamp", "ies4_compliance_version"]
                for field in required_meta_fields:
                    if field not in meta:
                        validation_errors.append(
                            f"Missing consolidation metadata field: {field}"
                        )

        except Exception as e:
            validation_errors.append(f"Validation processing error: {e}")

        # Log validation results
        if validation_errors:
            for error in validation_errors:
                logger.error(f"Validation error: {error}")
            return False
        else:
            logger.debug("JSON structure validation passed")
            return True

    def _load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse a JSON file.

        Args:
            file_path (Path): Path to the JSON file

        Returns:
            Dict containing the parsed JSON or None if loading fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded JSON file: {file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    def _merge_json_files(self, json_files: List[Path]) -> Dict[str, Any]:
        """
        Merge multiple JSON files into a single IES4-compliant structure.
        Enhanced for IES4 r4.3.0 with improved metadata and source tracking.

        Args:
            json_files (List[Path]): List of JSON file paths to merge

        Returns:
            Dict containing the merged data with enhanced metadata
        """
        # Enhanced metadata structure for IES4 r4.3.0
        merged_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Consolidated IES4 Military Database",
            "description": (
                f"Consolidated database created on {datetime.now().isoformat()}"
            ),
            "version": "4.3.0",
            "consolidation_metadata": {
                "created_timestamp": datetime.now().isoformat(),
                "source_files": [],
                "total_source_files": len(json_files),
                "consolidation_tool": "IES4 Consolidator v2.0",
                "ies4_compliance_version": "r4.3.0 2024-12-16",
            },
        }

        # Initialize all entity type arrays
        for entity_type in self.entity_types:
            merged_data[entity_type] = []

        # Track unique entities by ID to avoid duplicates
        entity_tracker = defaultdict(set)
        # Track source file information for each entity
        entity_sources = defaultdict(dict)

        for file_path in json_files:
            logger.info(f"Processing file: {file_path}")
            data = self._load_json_file(file_path)

            if not data:
                continue

            # Track source file metadata
            source_file_info = {
                "file_path": str(file_path.relative_to(self.base_path)),
                "file_name": file_path.name,
                "processing_timestamp": datetime.now().isoformat(),
            }

            # Add file size if available
            try:
                source_file_info["file_size_bytes"] = file_path.stat().st_size
            except Exception:
                pass

            merged_data["consolidation_metadata"]["source_files"].append(
                source_file_info
            )

            # Copy and enhance metadata from source files
            if (
                "title" not in merged_data
                or merged_data["title"] == "Consolidated IES4 Military Database"
            ):
                if "title" in data:
                    merged_data["title"] = (
                        f"Consolidated {data.get('title', 'IES4 Database')}"
                    )
                if "description" in data and "description" not in merged_data:
                    merged_data["description"] = data["description"]

            # Preserve version information from source files
            if "version" in data:
                if "source_versions" not in merged_data["consolidation_metadata"]:
                    merged_data["consolidation_metadata"]["source_versions"] = []
                source_versions = merged_data["consolidation_metadata"][
                    "source_versions"
                ]
                if data["version"] not in source_versions:
                    source_versions.append(data["version"])

            # Merge each entity type with enhanced tracking
            entities_added_from_file = 0
            for entity_type in self.entity_types:
                if entity_type in data and isinstance(data[entity_type], list):
                    for entity in data[entity_type]:
                        if isinstance(entity, dict) and "id" in entity:
                            entity_id = entity["id"]

                            # Only add if not already present
                            if entity_id not in entity_tracker[entity_type]:
                                # Enhance entity with source tracking
                                enhanced_entity = entity.copy()
                                enhanced_entity["_source_file"] = file_path.name
                                enhanced_entity["_consolidation_timestamp"] = (
                                    datetime.now().isoformat()
                                )

                                # Add timestamp if not present (IES4 r4.3.0 requirement)
                                if "timestamp" not in enhanced_entity:
                                    enhanced_entity["timestamp"] = (
                                        datetime.now().isoformat()
                                    )

                                merged_data[entity_type].append(enhanced_entity)
                                entity_tracker[entity_type].add(entity_id)
                                entity_sources[entity_type][entity_id] = file_path.name
                                entities_added_from_file += 1
                                logger.debug(
                                    f"Added {entity_type}: {entity_id} "
                                    f"from {file_path.name}"
                                )
                            else:
                                source_file = entity_sources[entity_type][entity_id]
                                logger.debug(
                                    f"Skipped duplicate {entity_type}: {entity_id} "
                                    f"(already from {source_file})"
                                )

            logger.info(
                f"Added {entities_added_from_file} entities from {file_path.name}"
            )

        # Add consolidation summary to metadata
        consolidated_counts = {}
        for entity_type in self.entity_types:
            count = len(merged_data[entity_type])
            if count > 0:
                consolidated_counts[entity_type] = count
                logger.info(f"Consolidated {count} {entity_type}")

        merged_data["consolidation_metadata"]["entity_counts"] = consolidated_counts
        merged_data["consolidation_metadata"]["total_entities"] = sum(
            consolidated_counts.values()
        )

        return merged_data

    def _save_consolidated_file(self, data: Dict[str, Any], output_file: Path) -> bool:
        """
        Save consolidated data to output file.

        Args:
            data (Dict): Data to save
            output_file (Path): Output file path

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate before saving
            if not self._validate_json_structure(data):
                logger.error(f"Data validation failed for {output_file}")
                return False

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved consolidated file: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving {output_file}: {e}")
            return False

    def _discover_country_folders(self) -> List[Path]:
        """
        Discover country/region folders and their subfolders in the data directory.
        Now supports nested subfolders like data/uk/army/, data/uk/navy/

        Returns:
            List of Path objects for country folders and subfolders
        """
        country_folders = []

        if not self.data_path.exists():
            logger.error(f"Data path does not exist: {self.data_path}")
            return country_folders

        for item in self.data_path.iterdir():
            if item.is_dir():
                # Check if main folder contains JSON files
                json_files = list(item.glob("*.json"))
                if json_files:
                    country_folders.append(item)
                    logger.debug(
                        f"Found country folder: {item.name} "
                        f"({len(json_files)} JSON files)"
                    )

                # Also check for nested subfolders that contain JSON files
                for subfolder in item.iterdir():
                    if subfolder.is_dir():
                        subfolder_json_files = list(subfolder.glob("*.json"))
                        if subfolder_json_files:
                            country_folders.append(subfolder)
                            logger.debug(
                                f"Found nested folder: {subfolder.relative_to(self.data_path)} "
                                f"({len(subfolder_json_files)} JSON files)"
                            )

        return country_folders

    def consolidate_by_country(self) -> Dict[str, bool]:
        """
        Main method to consolidate JSON files by country/region.
        Enhanced with performance monitoring and progress tracking.

        Returns:
            Dict mapping country names to consolidation success status
        """
        start_time = time.time()
        logger.info("Starting IES4 JSON file consolidation process")
        logger.info("IES4 Compliance Version: r4.3.0 2024-12-16")

        country_folders = self._discover_country_folders()
        results = {}
        total_folders = len(country_folders)

        if not country_folders:
            logger.warning("No country folders with JSON files found")
            return results

        logger.info(f"Found {total_folders} folders to process")

        for i, country_folder in enumerate(country_folders, 1):
            folder_start_time = time.time()

            # Generate appropriate name for nested folders
            if country_folder.parent == self.data_path:
                # Top-level country folder
                country_name = country_folder.name.lower()
            else:
                # Nested subfolder - use parent/subfolder format
                parent_name = country_folder.parent.name.lower()
                subfolder_name = country_folder.name.lower()
                country_name = f"{parent_name}_{subfolder_name}"

            logger.info(
                f"[{i}/{total_folders}] Processing folder: "
                f"{country_folder.relative_to(self.data_path)} as '{country_name}'"
            )

            # Find all JSON files in the country folder
            json_files = list(country_folder.glob("*.json"))

            if len(json_files) == 0:
                logger.warning(f"No JSON files found in {country_folder}")
                results[country_name] = False
                continue

            # Performance warning for large datasets
            total_size = sum(f.stat().st_size for f in json_files if f.exists())
            if total_size > 50 * 1024 * 1024:  # 50MB
                logger.warning(
                    f"Large dataset detected: {total_size / (1024*1024):.1f}MB "
                    f"across {len(json_files)} files"
                )

            if len(json_files) == 1:
                logger.info(
                    f"Only one JSON file in {country_folder}, copying to output"
                )
                # Just copy the single file
                source_file = json_files[0]
                output_file = (
                    self.output_path / f"ies4_{country_name}_consolidated.json"
                )

                try:
                    data = self._load_json_file(source_file)
                    if data:
                        # Still enhance with metadata even for single files
                        if "consolidation_metadata" not in data:
                            # Ensure required schema field is present
                            if "$schema" not in data:
                                data["$schema"] = (
                                    "http://json-schema.org/draft-07/schema#"
                                )

                            data["consolidation_metadata"] = {
                                "created_timestamp": datetime.now().isoformat(),
                                "source_files": [
                                    {
                                        "file_path": str(
                                            source_file.relative_to(self.base_path)
                                        ),
                                        "file_name": source_file.name,
                                        "processing_timestamp": datetime.now().isoformat(),
                                        "file_size_bytes": source_file.stat().st_size,
                                    }
                                ],
                                "total_source_files": 1,
                                "consolidation_tool": "IES4 Consolidator v2.0",
                                "ies4_compliance_version": "r4.3.0 2024-12-16",
                            }
                        results[country_name] = self._save_consolidated_file(
                            data, output_file
                        )
                    else:
                        results[country_name] = False
                except Exception as e:
                    logger.error(
                        f"Error processing single file for {country_name}: {e}"
                    )
                    results[country_name] = False
            else:
                logger.info(f"Merging {len(json_files)} JSON files for {country_name}")

                # Merge multiple files
                merged_data = self._merge_json_files(json_files)

                # Save consolidated file
                output_file = (
                    self.output_path / f"ies4_{country_name}_consolidated.json"
                )
                results[country_name] = self._save_consolidated_file(
                    merged_data, output_file
                )

            # Log processing time for this folder
            folder_time = time.time() - folder_start_time
            logger.info(
                f"Completed {country_name} in {folder_time:.2f} seconds "
                f"[{i}/{total_folders}]"
            )

        # Log overall processing time
        total_time = time.time() - start_time
        logger.info(f"Consolidation process completed in {total_time:.2f} seconds")

        return results

    def generate_summary_report(self, results: Dict[str, bool]) -> None:
        """
        Generate an enhanced summary report of the consolidation process
        with IES4 r4.3.0 compliance information.

        Args:
            results (Dict): Results from consolidation process
        """
        successful = sum(1 for success in results.values() if success)
        total = len(results)

        report = f"""
IES4 JSON Consolidation Summary Report
=====================================
Generated: {datetime.now().isoformat()}
IES4 Compliance Version: r4.3.0 2024-12-16
Consolidator Version: 2.0

Processing Summary:
------------------
Total Folders Processed: {total}
Successful Consolidations: {successful}
Failed Consolidations: {total - successful}
Success Rate: {(successful/total*100) if total > 0 else 0:.1f}%

Detailed Results:
----------------"""

        for country, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            report += f"  {country.upper()}: {status}\n"

        report += f"""
Output Information:
------------------
Output Directory: {self.output_path}
Log File: ies4_consolidator.log

IES4 r4.3.0 Enhancements:
------------------------
✓ Enhanced metadata preservation with source file tracking
✓ Nested subfolder support (e.g., uk/army/, uk/navy/)
✓ Improved schema validation with r4.3.0 compliance checks
✓ Entity timestamp management and versioning
✓ Comprehensive audit trail in consolidation metadata
✓ Enhanced error handling and recovery mechanisms

For detailed processing information, review the log file.
        """

        # Save report
        report_file = self.output_path / "consolidation_report.txt"
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"Summary report saved: {report_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

        # Print to console
        print(report)


def main():
    """
    Main execution function.
    """
    try:
        # Initialize consolidator
        consolidator = IES4Consolidator()

        # Run consolidation
        results = consolidator.consolidate_by_country()

        # Generate summary report
        consolidator.generate_summary_report(results)

        logger.info("IES4 JSON consolidation process completed")

    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()
