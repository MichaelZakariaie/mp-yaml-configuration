#!/usr/bin/env python3
"""
Check backwards compatibility of template.yaml changes.
Ensures all required fields from previous versions remain present.
"""
import yaml
import sys
import os
from pathlib import Path

def load_yaml(file_path):
    """Load YAML file and return its content."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def get_schema_structure(data, path=""):
    """Extract the structure of a YAML schema, including field types."""
    structure = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, dict):
                structure[key] = {
                    'type': 'dict',
                    'fields': get_schema_structure(value, current_path)
                }
            elif isinstance(value, list):
                structure[key] = {
                    'type': 'list',
                    'item_structure': get_schema_structure(value[0], current_path) if value else None
                }
            else:
                structure[key] = {'type': type(value).__name__}
    
    return structure

def check_field_compatibility(old_struct, new_struct, path=""):
    """Check if new structure is compatible with old structure."""
    errors = []
    
    for field, old_spec in old_struct.items():
        current_path = f"{path}.{field}" if path else field
        
        if field not in new_struct:
            errors.append(f"Missing required field: '{current_path}'")
            continue
        
        new_spec = new_struct[field]
        
        # Check type compatibility
        if old_spec['type'] != new_spec['type']:
            errors.append(f"Type changed for '{current_path}': {old_spec['type']} -> {new_spec['type']}")
            continue
        
        # Recursively check nested structures
        if old_spec['type'] == 'dict' and 'fields' in old_spec:
            nested_errors = check_field_compatibility(
                old_spec['fields'], 
                new_spec.get('fields', {}), 
                current_path
            )
            errors.extend(nested_errors)
    
    return errors

def get_latest_schema_version():
    """Get the most recent schema version from schemas directory."""
    schemas_dir = Path(__file__).parent.parent / 'schemas'
    if not schemas_dir.exists():
        return None
    
    schema_files = sorted(schemas_dir.glob('v*.yaml'))
    if not schema_files:
        return None
    
    return schema_files[-1]

def main():
    """Main compatibility check function."""
    template_path = Path(__file__).parent.parent / 'template.yaml'
    
    # Load current template
    try:
        current_template = load_yaml(template_path)
    except Exception as e:
        print(f"Error loading template.yaml: {e}")
        sys.exit(1)
    
    # Check if template has version field
    if 'version' not in current_template:
        print("Error: template.yaml must have a 'version' field")
        sys.exit(1)
    
    # Get latest archived schema
    latest_schema_path = get_latest_schema_version()
    if not latest_schema_path:
        print("No previous schema versions found. First commit allowed.")
        sys.exit(0)
    
    # Load previous schema
    try:
        previous_schema = load_yaml(latest_schema_path)
    except Exception as e:
        print(f"Error loading previous schema: {e}")
        sys.exit(1)
    
    # Extract structures
    current_struct = get_schema_structure(current_template)
    previous_struct = get_schema_structure(previous_schema)
    
    # Check compatibility
    errors = check_field_compatibility(previous_struct, current_struct)
    
    if errors:
        print("Backwards compatibility check failed!")
        print("\nThe following issues were found:")
        for error in errors:
            print(f"  - {error}")
        print("\nTo maintain backwards compatibility, all fields from previous versions must remain.")
        print("You can add new optional fields, but cannot remove or change existing ones.")
        sys.exit(1)
    
    # Check version increment
    current_version = current_template.get('version', '1.0')
    previous_version = previous_schema.get('version', '1.0')
    
    if current_version == previous_version:
        print(f"Error: Version must be incremented. Current: {current_version}, Previous: {previous_version}")
        sys.exit(1)
    
    print(f"✓ Compatibility check passed! (v{previous_version} -> v{current_version})")
    sys.exit(0)

if __name__ == "__main__":
    main()