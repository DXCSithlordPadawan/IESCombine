# IES4 Military Database JSON Consolidator

This Python tool consolidates multiple JSON files per country/region folder into single IES4-compliant files, maintaining data integrity and avoiding duplicates.

## Features

- **Automatic Discovery**: Scans the `data/` folder for country subfolders
- **IES4 Compliance**: Validates all output against the IES4 JSON schema
- **Duplicate Prevention**: Ensures no duplicate entities based on ID fields
- **Comprehensive Logging**: Detailed logs of the consolidation process
- **Error Handling**: Robust error handling with detailed reporting
- **Multiple Formats**: Supports various IES4 entity types (vehicles, areas, people, etc.)

## Directory Structure

```
C:\ies4-military-database-analysis\
├── data/
│   ├── iran/                    # Country folders
│   │   ├── ies4_iran_drones_Version2.json
│   │   ├── ies4_iran_missiles_Version2.json
│   │   └── ...
│   ├── uk/
│   │   ├── uk_army_vehicles.json
│   │   ├── uk_naval_assets.json
│   │   └── ...
│   └── ...
├── output/
│   └── consolidated/            # Generated consolidated files
│       ├── ies4_iran_consolidated.json
│       ├── ies4_uk_consolidated.json
│       └── consolidation_report.txt
├── ies4_json_schema.json        # IES4 validation schema
├── ies4_consolidator.py         # Main consolidator script
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

### Supported Entity Types
The consolidator processes these IES4 entity types:
- `countries` - Country/nation entities
- `areas` - Geographical areas and locations
- `vehicles` - Military vehicles and equipment
- `vehicleTypes` - Vehicle classification types
- `peopleTypes` - Personnel classification types
- `people` - Individual person entities
- `representations` - Documents, images, and other media

## Output

### Consolidated Files
- **Location**: `output/consolidated/`
- **Naming**: `ies4_{country}_consolidated.json`
- **Format**: IES4-compliant JSON with merged entities

### Reports
- **Summary Report**: `consolidation_report.txt` - High-level summary
- **Log File**: `ies4_consolidator.log` - Detailed processing log

### Sample Output Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Consolidated IES4 Military Database - Iran",
  "description": "Consolidated database created on 2025-08-21T...",
  "countries": [...],
  "areas": [...],
  "vehicles": [...],
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
