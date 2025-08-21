#!/usr/bin/env python3
"""
IES4 Military Database JSON File Consolidator

This script examines the data folder structure and combines multiple JSON files 
per country subfolder into single IES4-compliant files.

Author: Military Database Analysis System
Version: 1.0
"""

import os
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ies4_consolidator.log'),
        logging.StreamHandler()
    ]
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
            "countries", "areas", "vehicles", "vehicleTypes", 
            "peopleTypes", "people", "representations"
        ]
    
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load the IES4 JSON schema for validation.
        
        Returns:
            Dict containing the schema or None if loading fails
        """
        try:
            if self.schema_path.exists():
                with open(self.schema_path, 'r', encoding='utf-8') as f:
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
        Validate JSON data against IES4 schema.
        
        Args:
            data (Dict): JSON data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.schema:
            logger.warning("No schema available for validation")
            return True
            
        try:
            jsonschema.validate(data, self.schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Schema validation error: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
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
            with open(file_path, 'r', encoding='utf-8') as f:
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
        
        Args:
            json_files (List[Path]): List of JSON file paths to merge
            
        Returns:
            Dict containing the merged data
        """
        merged_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"Consolidated IES4 Military Database",
            "description": f"Consolidated database created on {datetime.now().isoformat()}",
        }
        
        # Initialize all entity type arrays
        for entity_type in self.entity_types:
            merged_data[entity_type] = []
        
        # Track unique entities by ID to avoid duplicates
        entity_tracker = defaultdict(set)
        
        for file_path in json_files:
            logger.info(f"Processing file: {file_path}")
            data = self._load_json_file(file_path)
            
            if not data:
                continue
            
            # Copy metadata from first file if not already set
            if "title" not in merged_data or merged_data["title"] == "Consolidated IES4 Military Database":
                if "title" in data:
                    merged_data["title"] = f"Consolidated {data.get('title', 'IES4 Database')}"
                if "description" in data and "description" not in merged_data:
                    merged_data["description"] = data["description"]
            
            # Merge each entity type
            for entity_type in self.entity_types:
                if entity_type in data and isinstance(data[entity_type], list):
                    for entity in data[entity_type]:
                        if isinstance(entity, dict) and "id" in entity:
                            entity_id = entity["id"]
                            
                            # Only add if not already present
                            if entity_id not in entity_tracker[entity_type]:
                                merged_data[entity_type].append(entity)
                                entity_tracker[entity_type].add(entity_id)
                                logger.debug(f"Added {entity_type}: {entity_id}")
                            else:
                                logger.debug(f"Skipped duplicate {entity_type}: {entity_id}")
        
        # Log consolidation summary
        for entity_type in self.entity_types:
            count = len(merged_data[entity_type])
            if count > 0:
                logger.info(f"Consolidated {count} {entity_type}")
        
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
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved consolidated file: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving {output_file}: {e}")
            return False
    
    def _discover_country_folders(self) -> List[Path]:
        """
        Discover country/region folders in the data directory.
        
        Returns:
            List of Path objects for country folders
        """
        country_folders = []
        
        if not self.data_path.exists():
            logger.error(f"Data path does not exist: {self.data_path}")
            return country_folders
        
        for item in self.data_path.iterdir():
            if item.is_dir():
                # Check if folder contains JSON files
                json_files = list(item.glob("*.json"))
                if json_files:
                    country_folders.append(item)
                    logger.debug(f"Found country folder: {item.name} ({len(json_files)} JSON files)")
        
        return country_folders
    
    def consolidate_by_country(self) -> Dict[str, bool]:
        """
        Main method to consolidate JSON files by country/region.
        
        Returns:
            Dict mapping country names to consolidation success status
        """
        logger.info("Starting IES4 JSON file consolidation process")
        
        country_folders = self._discover_country_folders()
        results = {}
        
        if not country_folders:
            logger.warning("No country folders with JSON files found")
            return results
        
        for country_folder in country_folders:
            country_name = country_folder.name.lower()
            logger.info(f"Processing country: {country_name}")
            
            # Find all JSON files in the country folder
            json_files = list(country_folder.glob("*.json"))
            
            if len(json_files) == 0:
                logger.warning(f"No JSON files found in {country_folder}")
                results[country_name] = False
                continue
            
            if len(json_files) == 1:
                logger.info(f"Only one JSON file in {country_folder}, copying to output")
                # Just copy the single file
                source_file = json_files[0]
                output_file = self.output_path / f"ies4_{country_name}_consolidated.json"
                
                try:
                    data = self._load_json_file(source_file)
                    if data:
                        results[country_name] = self._save_consolidated_file(data, output_file)
                    else:
                        results[country_name] = False
                except Exception as e:
                    logger.error(f"Error copying file for {country_name}: {e}")
                    results[country_name] = False
            else:
                logger.info(f"Merging {len(json_files)} JSON files for {country_name}")
                
                # Merge multiple files
                merged_data = self._merge_json_files(json_files)
                
                # Save consolidated file
                output_file = self.output_path / f"ies4_{country_name}_consolidated.json"
                results[country_name] = self._save_consolidated_file(merged_data, output_file)
        
        return results
    
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
        report += f"Log File: ies4_consolidator.log\n"
        
        # Save report
        report_file = self.output_path / "consolidation_report.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
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
