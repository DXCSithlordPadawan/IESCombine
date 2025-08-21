# IES4 Military Database JSON Consolidator v2.0

This Python tool consolidates multiple JSON files per country/region folder into single IES4 r4.3.0 compliant files, maintaining data integrity, avoiding duplicates, and providing comprehensive audit trails.

## 🚀 Version 2.0 Features

### NEW in v2.0 - IES4 r4.3.0 Enhanced Compliance
- **Full IES4 r4.3.0 compliance** with Information Exchange Standard r4.3.0 2024-12-16 specifications
- **Enhanced schema validation** with required field checking and compliance reporting
- **Automatic timestamp management** for entities (added if missing)
- **Version compatibility warnings** and handling for mixed-version datasets

### NEW - Multi-folder Support  
- **Recursive nested subfolder scanning** - supports structures like:
  - `data/uk/army/` → consolidated as `ies4_uk_army_consolidated.json`
  - `data/uk/navy/` → consolidated as `ies4_uk_navy_consolidated.json`
  - `data/iran/` → consolidated as `ies4_iran_consolidated.json`
- **Smart naming conventions** for nested folder hierarchies
- **Maintains folder hierarchy information** in consolidation metadata

### NEW - Enhanced Metadata & Source Tracking
- **Comprehensive consolidation metadata** with audit trail information
- **Source file tracking** - each entity knows which file it came from
- **Data lineage preservation** with processing timestamps and file sizes
- **Entity counts and statistics** in consolidated output
- **File processing performance metrics**

### NEW - Performance Monitoring
- **Progress tracking** with `[1/3]` style indicators during processing
- **Performance timing** for individual folders and overall process
- **Large dataset warnings** for files >50MB
- **Memory usage optimization** for processing large files

## Features

- **Automatic Discovery**: Recursively scans the `data/` folder for country subfolders and nested subfolders
- **IES4 r4.3.0 Compliance**: Validates all output against the IES4 r4.3.0 JSON schema with enhanced validation
- **Duplicate Prevention**: Ensures no duplicate entities based on ID fields with source tracking
- **Comprehensive Logging**: Detailed logs of the consolidation process with structured output
- **Enhanced Error Handling**: Robust error handling with detailed IES4 compliance reporting
- **Multiple Formats**: Supports various IES4 entity types (vehicles, areas, people, etc.)
- **Source File Attribution**: Each entity includes metadata about its source file
- **Audit Trail**: Complete audit trail in consolidation metadata

## Directory Structure

### Enhanced Multi-level Support (NEW in v2.0)

The consolidator now supports both traditional flat structure and nested subfolders:

```
C:\ies4-military-database-analysis\
├── data/
│   ├── iran/                    # Country folders
│   │   ├── ies4_iran_drones_Version2.json
│   │   ├── ies4_iran_missiles_Version2.json
│   │   └── ...
│   ├── uk/                      # Country with nested subfolders
│   │   ├── uk_main_assets.json  # Main country-level files
│   │   ├── army/                # Nested subfolder (NEW!)
│   │   │   ├── uk_army_vehicles.json
│   │   │   ├── uk_army_personnel.json
│   │   │   └── ...
│   │   ├── navy/                # Another nested subfolder (NEW!)
│   │   │   ├── uk_naval_assets.json
│   │   │   ├── uk_naval_personnel.json
│   │   │   └── ...
│   │   └── airforce/            # Yet another nested subfolder (NEW!)
│   │       ├── uk_air_vehicles.json
│   │       └── ...
│   └── us/
│       ├── us_main.json
│       ├── special_ops/         # Nested subfolder
│       │   └── classified_data.json
│       └── ...
├── output/
│   └── consolidated/            # Generated consolidated files
│       ├── ies4_iran_consolidated.json
│       ├── ies4_uk_consolidated.json       # Main UK folder
│       ├── ies4_uk_army_consolidated.json  # UK Army subfolder (NEW!)
│       ├── ies4_uk_navy_consolidated.json  # UK Navy subfolder (NEW!)
│       ├── ies4_uk_airforce_consolidated.json  # UK Air Force subfolder (NEW!)
│       ├── ies4_us_consolidated.json
│       ├── ies4_us_special_ops_consolidated.json  # US Special Ops subfolder (NEW!)
│       └── consolidation_report.txt
├── ies4_json_schema.json        # IES4 r4.3.0 validation schema
├── ies4_consolidator.py         # Main consolidator script v2.0
├── run_consolidation.py         # Command-line runner
├── run_consolidation.bat        # Windows batch runner
└── requirements.txt             # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. Clone or download the files to your project directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Windows Batch File (Easiest)
Double-click `run_consolidation.bat` or run from command prompt:
```cmd
run_consolidation.bat
```

### Option 2: Python Command Line
```bash
# Basic usage with default path
python run_consolidation.py

# Specify custom base path
python run_consolidation.py --base-path "D:\my-analysis-folder"

# Verbose output
python run_consolidation.py --verbose

# Dry run (discover files without processing)
python run_consolidation.py --dry-run
```

### Option 3: Direct Python Import
```python
from ies4_consolidator import IES4Consolidator

# Initialize and run
consolidator = IES4Consolidator("C:\\ies4-military-database-analysis")
results = consolidator.consolidate_by_country()
consolidator.generate_summary_report(results)
```

## Configuration

### Modifying Base Path
Edit the `BASE_PATH` variable in `run_consolidation.bat`:
```batch
set BASE_PATH=D:\your-custom-path
```

Or use the command line argument:
```bash
python run_consolidation.py --base-path "D:\your-custom-path"
```

### Supported Entity Types (IES4 r4.3.0)
The consolidator processes these IES4 r4.3.0 entity types:
- `countries` - Country/nation entities with enhanced timestamp support
- `areas` - Geographical areas and locations with coordinate validation
- `vehicles` - Military vehicles and equipment with type classification
- `vehicleTypes` - Vehicle classification types with inheritance support
- `peopleTypes` - Personnel classification types with role definitions
- `people` - Individual person entities with relationship tracking
- `representations` - Documents, images, and other media with metadata preservation

### Enhanced Output Structure (NEW in v2.0)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Consolidated IES4 Military Database - UK Army",
  "description": "Consolidated database created on 2025-01-01T...",
  "version": "4.3.0",
  "consolidation_metadata": {
    "created_timestamp": "2025-01-01T12:00:00.000Z",
    "ies4_compliance_version": "r4.3.0 2024-12-16",
    "consolidation_tool": "IES4 Consolidator v2.0",
    "source_files": [
      {
        "file_path": "data/uk/army/vehicles.json",
        "file_name": "vehicles.json",
        "file_size_bytes": 15432,
        "processing_timestamp": "2025-01-01T12:00:00.000Z"
      }
    ],
    "total_source_files": 3,
    "entity_counts": {
      "vehicles": 25,
      "people": 15
    },
    "total_entities": 40,
    "source_versions": ["4.3.0", "4.2.0"]
  },
  "countries": [...],
  "areas": [...],
  "vehicles": [
    {
      "id": "uk-army-tank-001",
      "type": "main_battle_tank",
      "name": "Challenger 2",
      "timestamp": "2024-12-01T00:00:00Z",
      "_source_file": "vehicles.json",
      "_consolidation_timestamp": "2025-01-01T12:00:00.000Z"
    }
  ],
  "people": [...],
  "representations": [...]
}
```

## Output

### Enhanced Consolidated Files (v2.0)
- **Location**: `output/consolidated/`
- **Naming**: 
  - Main folders: `ies4_{country}_consolidated.json`
  - Nested folders: `ies4_{country}_{subfolder}_consolidated.json`
- **Format**: IES4 r4.3.0 compliant JSON with enhanced metadata and audit trails

### Enhanced Reports (v2.0)
- **Summary Report**: `consolidation_report.txt` - Comprehensive summary with compliance info
- **Log File**: `ies4_consolidator.log` - Detailed processing log with structured output

### Sample Enhanced Output Structure (NEW)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Consolidated IES4 Military Database - Iran",
  "description": "Consolidated database created on 2025-08-21T...",
  "version": "4.3.0",
  "consolidation_metadata": {
    "created_timestamp": "2025-08-21T14:22:02.885Z",
    "ies4_compliance_version": "r4.3.0 2024-12-16",
    "consolidation_tool": "IES4 Consolidator v2.0",
    "source_files": [
      {
        "file_path": "data/iran/iran_drones.json",
        "file_name": "iran_drones.json",
        "file_size_bytes": 1542,
        "processing_timestamp": "2025-08-21T14:22:02.884Z"
      },
      {
        "file_path": "data/iran/iran_missiles.json", 
        "file_name": "iran_missiles.json",
        "file_size_bytes": 1389,
        "processing_timestamp": "2025-08-21T14:22:02.885Z"
      }
    ],
    "total_source_files": 2,
    "entity_counts": {
      "vehicles": 2
    },
    "total_entities": 2,
    "source_versions": ["4.3.0"]
  },
  "countries": [...],
  "areas": [...],
  "vehicles": [
    {
      "id": "iran-drone-001",
      "type": "drone",
      "name": "Shahed-136",
      "timestamp": "2025-08-21T14:22:02.885Z",
      "_source_file": "iran_drones.json",
      "_consolidation_timestamp": "2025-08-21T14:22:02.885Z"
    }
  ],
  "vehicleTypes": [...],
  "peopleTypes": [...],
  "people": [...],
  "representations": [...]
}
```

## Error Handling

### Common Issues

1. **Missing Base Path**
   - Error: `Base path does not exist`
   - Solution: Verify the path exists and update configuration

2. **Schema Validation Errors**
   - Error: `Schema validation error`
   - Solution: Check source JSON files for IES4 compliance

3. **JSON Parse Errors**
   - Error: `JSON decode error`
   - Solution: Validate JSON syntax in source files

4. **Permission Errors**
   - Error: `Permission denied`
   - Solution: Run with appropriate file system permissions

### IES4 r4.3.0 Compliance Issues (NEW)

1. **Missing Required Fields**
   - Error: `Missing required field: id` or `Missing required field: type`
   - Solution: Ensure all entities have required `id` and `type` fields per IES4 r4.3.0 spec

2. **Schema Version Mismatch**
   - Warning: `Version mismatch: found 4.2.0, expected 4.3.0`
   - Solution: Update source files to IES4 r4.3.0 or accept version warnings

3. **Missing Timestamp Fields**
   - Warning: `missing 'timestamp' field, will be added during processing`
   - Solution: Add timestamp fields to entities or allow auto-generation

4. **Large Dataset Warnings**
   - Warning: `Large dataset detected: 75.3MB across 15 files`
   - Solution: Consider splitting large datasets or expect longer processing times

### Troubleshooting

1. **Check Log Files**: Review `ies4_consolidator.log` for detailed errors
2. **Validate JSON**: Use online JSON validators for source files
3. **Test Schema**: Validate individual files against `ies4_json_schema.json`
4. **Dry Run**: Use `--dry-run` to test without making changes

## Advanced Usage

### Custom Validation
```python
# Load and validate a specific file
consolidator = IES4Consolidator()
data = consolidator._load_json_file(Path("my_file.json"))
is_valid = consolidator._validate_json_structure(data)
```

### Selective Processing
```python
# Process only specific countries
consolidator = IES4Consolidator()
country_folders = consolidator._discover_country_folders()
iran_folder = [f for f in country_folders if f.name == 'iran'][0]
json_files = list(iran_folder.glob("*.json"))
merged_data = consolidator._merge_json_files(json_files)
```

## API Reference

### IES4Consolidator Class

#### Constructor
```python
IES4Consolidator(base_path: str = "C:\\ies4-military-database-analysis")
```

#### Key Methods
- `consolidate_by_country()` - Main consolidation method
- `generate_summary_report(results)` - Generate processing report
- `_discover_country_folders()` - Find country directories
- `_merge_json_files(json_files)` - Merge multiple JSON files
- `_validate_json_structure(data)` - Validate against IES4 schema

## Contributing

1. Ensure Python 3.8+ compatibility
2. Follow PEP 8 style guidelines
3. Add logging for new features
4. Update schema validation as needed
5. Test with various JSON file structures

## License

This tool is designed for military database analysis and should be used in accordance with applicable data handling regulations and organizational policies.
