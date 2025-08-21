#!/usr/bin/env python3
"""
IES4 Military Database JSON File Consolidator

This script examines the data folder structure and combines multiple JSON files
per country subfolder into single IES4-compliant files.

Supports IES4 r4.3.0 2024-12-16 specification with enhanced compliance,
multi-folder support, and comprehensive metadata preservation.

Author: Military Database Analysis System
Version: 2.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import jsonschema
from collections import defaultdict

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

        # IES4 r4.3.0 entity types that can be consolidated
        self.entity_types = [
            "countries",
            "areas",
            "vehicles",
            "vehicleTypes",
            "peopleTypes",
            "people",
            "representations",
            "organizations",  # Added for r4.3.0
            "events",  # Added for r4.3.0
            "activities",  # Added for r4.3.0
            "facilities",  # Added for r4.3.0
            "items",  # Added for r4.3.0
            "locations",  # Enhanced for r4.3.0
            "relationships",  # Added for r4.3.0
        ]

        # IES4 r4.3.0 required metadata fields
        self.required_ies4_fields = ["id", "type", "timestamp", "version"]

        # Configuration for IES4 version support
        self.ies4_version = "4.3.0"
        self.ies4_spec_date = "2024-12-16"

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
        Enhanced validation of JSON data against IES4 r4.3.0 schema with
        comprehensive compliance checking.

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
                validation_errors.append(f"Schema error: {e}")
        else:
            logger.warning("No schema available for validation")

        # IES4 r4.3.0 specific validation
        ies4_errors = self._validate_ies4_compliance(data)
        validation_errors.extend(ies4_errors)

        if validation_errors:
            for error in validation_errors:
                logger.error(f"Validation error: {error}")
            return False

        return True

    def _validate_ies4_compliance(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate IES4 r4.3.0 specific compliance requirements.

        Args:
            data: JSON data to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Check for required IES4 metadata
        if "ies4Version" not in data:
            data["ies4Version"] = self.ies4_version

        if "specificationDate" not in data:
            data["specificationDate"] = self.ies4_spec_date

        # Validate entity structures
        for entity_type in self.entity_types:
            if entity_type in data and isinstance(data[entity_type], list):
                for i, entity in enumerate(data[entity_type]):
                    if not isinstance(entity, dict):
                        errors.append(f"{entity_type}[{i}]: Entity must be an object")
                        continue

                    # Check required fields
                    for field in self.required_ies4_fields:
                        if field not in entity:
                            errors.append(
                                f"{entity_type}[{i}]: Missing required field '{field}'"
                            )

                    # Validate ID format
                    if "id" in entity:
                        if (
                            not isinstance(entity["id"], str)
                            or not entity["id"].strip()
                        ):
                            errors.append(f"{entity_type}[{i}]: Invalid ID format")

                    # Validate timestamp format
                    if "timestamp" in entity:
                        if not self._validate_timestamp(entity["timestamp"]):
                            errors.append(
                                f"{entity_type}[{i}]: Invalid timestamp format"
                            )

        return errors

    def _validate_timestamp(self, timestamp: Any) -> bool:
        """
        Validate timestamp format according to IES4 r4.3.0 specification.

        Args:
            timestamp: Timestamp value to validate

        Returns:
            bool: True if valid timestamp format
        """
        if not isinstance(timestamp, str):
            return False

        try:
            # Try parsing ISO 8601 format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False

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
        Enhanced merge of multiple JSON files into a single IES4 r4.3.0 compliant
        structure with comprehensive metadata preservation and audit trail.

        Args:
            json_files (List[Path]): List of JSON file paths to merge

        Returns:
            Dict containing the merged data with enhanced metadata
        """
        timestamp = datetime.now().isoformat()

        merged_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Consolidated IES4 Military Database",
            "description": f"Consolidated database created on {timestamp}",
            "ies4Version": self.ies4_version,
            "specificationDate": self.ies4_spec_date,
            "consolidationMetadata": {
                "timestamp": timestamp,
                "consolidatedFiles": [],
                "sourceFileCount": len(json_files),
                "consolidationTool": "IES4Consolidator",
                "toolVersion": "2.0",
            },
        }

        # Initialize all entity type arrays
        for entity_type in self.entity_types:
            merged_data[entity_type] = []

        # Track unique entities by ID with enhanced metadata
        entity_tracker = defaultdict(set)
        entity_versions = defaultdict(dict)  # Track entity versions
        source_tracking = defaultdict(list)  # Track source files per entity

        for file_path in json_files:
            logger.info(f"Processing file: {file_path}")
            data = self._load_json_file(file_path)

            if not data:
                continue

            # Add to source file tracking
            relative_path = str(file_path.relative_to(self.data_path))
            merged_data["consolidationMetadata"]["consolidatedFiles"].append(
                {
                    "path": relative_path,
                    "size": file_path.stat().st_size,
                    "processedAt": timestamp,
                }
            )

            # Preserve metadata from source files
            self._preserve_source_metadata(merged_data, data, relative_path)

            # Merge each entity type with enhanced tracking
            for entity_type in self.entity_types:
                if entity_type in data and isinstance(data[entity_type], list):
                    for entity in data[entity_type]:
                        if isinstance(entity, dict) and "id" in entity:
                            entity_id = entity["id"]

                            # Enhanced duplicate handling with versioning
                            if entity_id not in entity_tracker[entity_type]:
                                # Add source tracking to entity
                                entity_with_metadata = entity.copy()
                                entity_with_metadata["_sourceFiles"] = [relative_path]
                                entity_with_metadata["_consolidatedAt"] = timestamp

                                # Ensure required IES4 fields
                                if "timestamp" not in entity_with_metadata:
                                    entity_with_metadata["timestamp"] = timestamp
                                if "version" not in entity_with_metadata:
                                    entity_with_metadata["version"] = "1.0"

                                merged_data[entity_type].append(entity_with_metadata)
                                entity_tracker[entity_type].add(entity_id)
                                entity_versions[entity_type][entity_id] = entity.get(
                                    "version", "1.0"
                                )
                                source_tracking[entity_type].append(relative_path)

                                logger.debug(f"Added {entity_type}: {entity_id}")
                            else:
                                # Handle version conflicts
                                existing_version = entity_versions[entity_type][
                                    entity_id
                                ]
                                new_version = entity.get("version", "1.0")

                                if (
                                    self._compare_versions(
                                        new_version, existing_version
                                    )
                                    > 0
                                ):
                                    # Update with newer version
                                    for i, existing_entity in enumerate(
                                        merged_data[entity_type]
                                    ):
                                        if existing_entity["id"] == entity_id:
                                            entity_with_metadata = entity.copy()
                                            entity_with_metadata["_sourceFiles"] = [
                                                relative_path
                                            ]
                                            entity_with_metadata["_consolidatedAt"] = (
                                                timestamp
                                            )
                                            entity_with_metadata["_replacedVersion"] = (
                                                existing_version
                                            )

                                            merged_data[entity_type][
                                                i
                                            ] = entity_with_metadata
                                            entity_versions[entity_type][
                                                entity_id
                                            ] = new_version
                                            logger.info(
                                                f"Updated {entity_type}: {entity_id} "
                                                f"from v{existing_version} to v{new_version}"
                                            )
                                            break
                                else:
                                    logger.debug(
                                        f"Skipped {entity_type}: {entity_id} "
                                        f"(older/same version: {new_version} <= {existing_version})"
                                    )

        # Add consolidation summary
        merged_data["consolidationMetadata"]["entityCounts"] = {}
        for entity_type in self.entity_types:
            count = len(merged_data[entity_type])
            if count > 0:
                merged_data["consolidationMetadata"]["entityCounts"][
                    entity_type
                ] = count
                logger.info(f"Consolidated {count} {entity_type}")

        return merged_data

    def _preserve_source_metadata(
        self, merged_data: Dict[str, Any], source_data: Dict[str, Any], source_path: str
    ) -> None:
        """
        Preserve important metadata from source files.

        Args:
            merged_data: Target merged data structure
            source_data: Source file data
            source_path: Relative path of source file
        """
        # Copy metadata from first file if not already set
        if (
            "title" not in merged_data
            or merged_data["title"] == "Consolidated IES4 Military Database"
        ):
            if "title" in source_data:
                merged_data["title"] = (
                    f"Consolidated {source_data.get('title', 'IES4 Database')}"
                )
            if "description" in source_data:
                merged_data["description"] = source_data["description"]

        # Preserve source IES4 metadata
        if (
            "ies4Version" in source_data
            and source_data["ies4Version"] != self.ies4_version
        ):
            if "sourceVersions" not in merged_data["consolidationMetadata"]:
                merged_data["consolidationMetadata"]["sourceVersions"] = {}
            merged_data["consolidationMetadata"]["sourceVersions"][source_path] = (
                source_data["ies4Version"]
            )

    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            int: 1 if version1 > version2, -1 if version1 < version2, 0 if equal
        """
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]

            # Pad with zeros to make equal length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1
            return 0
        except (ValueError, AttributeError):
            # Fallback to string comparison
            return 1 if version1 > version2 else (-1 if version1 < version2 else 0)

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
        Discover country/region folders in the data directory with enhanced
        support for nested subfolder structures (e.g., data/uk/army/, data/uk/navy/).

        Returns:
            List of Path objects for country folders
        """
        country_folders = []

        if not self.data_path.exists():
            logger.error(f"Data path does not exist: {self.data_path}")
            return country_folders

        # First pass: direct country folders with JSON files
        for item in self.data_path.iterdir():
            if item.is_dir():
                # Check if folder contains JSON files directly
                json_files = list(item.glob("*.json"))
                if json_files:
                    country_folders.append(item)
                    logger.debug(
                        f"Found country folder: {item.name} "
                        f"({len(json_files)} JSON files)"
                    )
                else:
                    # Check for nested subfolders with JSON files
                    nested_folders = self._discover_nested_folders(item)
                    if nested_folders:
                        country_folders.extend(nested_folders)
                        logger.debug(
                            f"Found {len(nested_folders)} nested folders in {item.name}"
                        )

        return country_folders

    def _discover_nested_folders(self, parent_folder: Path) -> List[Path]:
        """
        Recursively discover nested folders containing JSON files.

        Args:
            parent_folder: Parent directory to scan

        Returns:
            List of nested folders containing JSON files
        """
        nested_folders = []

        try:
            for item in parent_folder.rglob("*.json"):
                folder = item.parent
                if folder != parent_folder and folder not in nested_folders:
                    json_count = len(list(folder.glob("*.json")))
                    if json_count > 0:
                        nested_folders.append(folder)
                        logger.debug(
                            f"Found nested folder: {folder.relative_to(self.data_path)} "
                            f"({json_count} JSON files)"
                        )
        except Exception as e:
            logger.error(f"Error scanning nested folders in {parent_folder}: {e}")

        return nested_folders

    def consolidate_by_country(self) -> Dict[str, bool]:
        """
        Enhanced method to consolidate JSON files by country/region with support
        for nested folder structures and improved error handling.

        Returns:
            Dict mapping folder paths to consolidation success status
        """
        logger.info("Starting IES4 r4.3.0 JSON file consolidation process")

        country_folders = self._discover_country_folders()
        results = {}

        if not country_folders:
            logger.warning("No country folders with JSON files found")
            return results

        for country_folder in country_folders:
            # Create unique identifier for nested folders
            folder_key = (
                str(country_folder.relative_to(self.data_path))
                .replace("/", "_")
                .replace("\\", "_")
            )
            logger.info(f"Processing folder: {folder_key} ({country_folder})")

            # Find all JSON files in the folder
            json_files = list(country_folder.glob("*.json"))

            if len(json_files) == 0:
                logger.warning(f"No JSON files found in {country_folder}")
                results[folder_key] = False
                continue

            try:
                if len(json_files) == 1:
                    logger.info(
                        f"Single JSON file in {country_folder}, enhancing with metadata"
                    )
                    # Process single file with enhanced metadata
                    source_file = json_files[0]
                    data = self._load_json_file(source_file)

                    if data:
                        # Add consolidation metadata even for single files
                        enhanced_data = self._enhance_single_file_metadata(
                            data, source_file
                        )
                        output_file = (
                            self.output_path / f"ies4_{folder_key}_consolidated.json"
                        )
                        results[folder_key] = self._save_consolidated_file(
                            enhanced_data, output_file
                        )
                    else:
                        results[folder_key] = False
                else:
                    logger.info(
                        f"Merging {len(json_files)} JSON files for {folder_key}"
                    )

                    # Merge multiple files with enhanced processing
                    merged_data = self._merge_json_files(json_files)

                    # Save consolidated file
                    output_file = (
                        self.output_path / f"ies4_{folder_key}_consolidated.json"
                    )
                    results[folder_key] = self._save_consolidated_file(
                        merged_data, output_file
                    )

            except Exception as e:
                logger.error(f"Error processing {folder_key}: {e}")
                results[folder_key] = False

        return results

    def _enhance_single_file_metadata(
        self, data: Dict[str, Any], source_file: Path
    ) -> Dict[str, Any]:
        """
        Enhance single file with consolidation metadata for consistency.

        Args:
            data: Original file data
            source_file: Source file path

        Returns:
            Enhanced data with consolidation metadata
        """
        timestamp = datetime.now().isoformat()
        relative_path = str(source_file.relative_to(self.data_path))

        enhanced_data = data.copy()

        # Add IES4 r4.3.0 compliance metadata
        enhanced_data["ies4Version"] = self.ies4_version
        enhanced_data["specificationDate"] = self.ies4_spec_date

        # Add consolidation metadata
        enhanced_data["consolidationMetadata"] = {
            "timestamp": timestamp,
            "consolidatedFiles": [
                {
                    "path": relative_path,
                    "size": source_file.stat().st_size,
                    "processedAt": timestamp,
                }
            ],
            "sourceFileCount": 1,
            "consolidationTool": "IES4Consolidator",
            "toolVersion": "2.0",
            "entityCounts": {},
        }

        # Count entities
        for entity_type in self.entity_types:
            if entity_type in enhanced_data and isinstance(
                enhanced_data[entity_type], list
            ):
                count = len(enhanced_data[entity_type])
                if count > 0:
                    enhanced_data["consolidationMetadata"]["entityCounts"][
                        entity_type
                    ] = count

        return enhanced_data

    def generate_summary_report(self, results: Dict[str, bool]) -> None:
        """
        Generate a summary report of the consolidation process.

        Args:
            results (Dict): Results from consolidation process
        """
        successful = sum(1 for success in results.values() if success)
        total = len(results)

        report = f"""
IES4 JSON Consolidation Summary Report
=====================================
Generated: {datetime.now().isoformat()}

Total Countries/Regions Processed: {total}
Successful Consolidations: {successful}
Failed Consolidations: {total - successful}

Details:
"""

        for country, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            report += f"  {country.upper()}: {status}\n"

        report += f"\nOutput Directory: {self.output_path}\n"
        report += "Log File: ies4_consolidator.log\n"

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
