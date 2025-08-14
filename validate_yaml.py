#!/usr/bin/env python3
"""
YAML Validator for Cohort Configuration Files

This tool validates user YAML implementations against the template schema.
It checks for required fields, correct types, and valid values.
"""
import yaml
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

class YAMLValidator:
    def __init__(self, schema_version: str = None):
        """Initialize validator with optional specific schema version."""
        self.schema_version = schema_version
        self.template = self._load_template()
        self.errors = []
        self.warnings = []
    
    def _load_template(self) -> Dict[str, Any]:
        """Load the template schema (either current or specific version)."""
        if self.schema_version:
            schema_path = Path(__file__).parent / 'schemas' / f'v{self.schema_version}.yaml'
            if not schema_path.exists():
                raise ValueError(f"Schema version {self.schema_version} not found")
        else:
            schema_path = Path(__file__).parent / 'template.yaml'
        
        with open(schema_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _validate_type(self, value: Any, expected_type: str, field_name: str) -> bool:
        """Validate that a value matches the expected type."""
        type_map = {
            '<int>': int,
            '<string>': str,
            '<column_name_or_index>': (str, int),
        }
        
        if expected_type in type_map:
            expected_types = type_map[expected_type]
            if not isinstance(expected_types, tuple):
                expected_types = (expected_types,)
            
            if not isinstance(value, expected_types):
                self.errors.append(
                    f"Field '{field_name}': Expected {expected_type}, got {type(value).__name__}"
                )
                return False
        
        return True
    
    def _validate_column_spec(self, spec: Any, field_name: str) -> bool:
        """Validate column specification (can be name, index, or range)."""
        if isinstance(spec, (str, int)):
            return True
        
        if isinstance(spec, dict) and 'range' in spec:
            range_spec = spec['range']
            if not isinstance(range_spec, dict):
                self.errors.append(f"Field '{field_name}': Range must be a dictionary")
                return False
            
            if 'start' not in range_spec or 'end' not in range_spec:
                self.errors.append(f"Field '{field_name}': Range must have 'start' and 'end'")
                return False
            
            return True
        
        self.errors.append(
            f"Field '{field_name}': Must be column name, index, or range specification"
        )
        return False
    
    def _validate_list_field(self, data: Dict[str, Any], field_name: str, 
                           template_value: Any) -> bool:
        """Validate list fields containing column specifications."""
        if field_name not in data:
            self.warnings.append(f"Optional field '{field_name}' not provided")
            return True
        
        value = data[field_name]
        if not isinstance(value, list):
            self.errors.append(f"Field '{field_name}': Must be a list")
            return False
        
        # Validate each item in the list
        for i, item in enumerate(value):
            if not self._validate_column_spec(item, f"{field_name}[{i}]"):
                return False
        
        return True
    
    def validate(self, yaml_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a YAML file against the template schema."""
        self.errors = []
        self.warnings = []
        
        # Load the YAML file
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to parse YAML: {e}")
            return False, self.errors, self.warnings
        
        if not isinstance(data, dict):
            self.errors.append("YAML must contain a dictionary at the root level")
            return False, self.errors, self.warnings
        
        # Check required fields from template
        for field, template_value in self.template.items():
            if field == 'version':
                continue  # Skip version field
            
            if field not in data:
                # Check if it's a required field
                if field in ['cohort', 'task', 'task_variation']:
                    self.errors.append(f"Missing required field: '{field}'")
                else:
                    self.warnings.append(f"Optional field '{field}' not provided")
                continue
            
            # Validate field type
            if isinstance(template_value, str) and template_value.startswith('<'):
                self._validate_type(data[field], template_value, field)
            elif isinstance(template_value, list):
                self._validate_list_field(data, field, template_value)
        
        # Check for unknown fields
        template_fields = set(self.template.keys()) - {'version'}
        data_fields = set(data.keys())
        unknown_fields = data_fields - template_fields
        
        if unknown_fields:
            self.warnings.append(f"Unknown fields found: {', '.join(unknown_fields)}")
        
        # Validate specific constraints
        if 'cohort' in data and not isinstance(data['cohort'], str):
            self.errors.append("Field 'cohort': Must be a string")
        
        return len(self.errors) == 0, self.errors, self.warnings

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Validate YAML configuration files against the template schema"
    )
    parser.add_argument(
        'yaml_file',
        type=Path,
        help='Path to the YAML file to validate'
    )
    parser.add_argument(
        '--schema-version',
        type=str,
        help='Specific schema version to validate against (e.g., "1.0")'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    
    args = parser.parse_args()
    
    if not args.yaml_file.exists():
        print(f"Error: File '{args.yaml_file}' not found")
        sys.exit(1)
    
    # Create validator and run validation
    try:
        validator = YAMLValidator(schema_version=args.schema_version)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    is_valid, errors, warnings = validator.validate(args.yaml_file)
    
    # Display results
    if errors:
        print("❌ Validation FAILED\n")
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        if errors:
            print()
        print("Warnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    
    if is_valid and not (args.strict and warnings):
        print(f"✅ Validation PASSED for '{args.yaml_file.name}'")
        if args.schema_version:
            print(f"   (validated against schema version {args.schema_version})")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()