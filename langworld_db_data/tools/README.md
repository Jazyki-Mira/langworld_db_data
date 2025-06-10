# LangWorld Tools Package

This package contains various tools for working with the LangWorld database, organized into domain-specific and domain-agnostic modules.

## Package Structure

### Domain-Specific Tools

#### `featureprofiles/`
Tools for working with feature profiles, including conversion from Excel and dictionary operations.

#### `features/`
Tools for managing language features, including adding new features.

#### `listed_values/`
Tools for managing listed values, including adding, moving, and renaming values.

### Domain-Agnostic Tools (`common/`)

#### `files/`
General-purpose file operations:
- `csv_xls.py`: CSV and Excel file handling
- `json_toml_yaml.py`: JSON, TOML, and YAML serialization
- `txt.py`: Text file operations

#### `ids/`
Utilities for working with LangWorld IDs:
- ID generation and validation
- ID index management
- ID update operations after modifications

## Development

When adding new tools:
1. Place domain-agnostic tools in the appropriate `common/` subpackage
2. Place domain-specific tools in their respective domain packages
