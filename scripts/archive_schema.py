#!/usr/bin/env python3
"""
Archive schema versions when template.yaml is updated.
Ensures all versions are preserved in the schemas directory.
"""
import yaml
import sys
import shutil
from pathlib import Path

def load_yaml(file_path):
    """Load YAML file and return its content."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def save_yaml(data, file_path):
    """Save data to YAML file."""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def main():
    """Main archive function."""
    template_path = Path(__file__).parent.parent / 'template.yaml'
    schemas_dir = Path(__file__).parent.parent / 'schemas'
    
    # Create schemas directory if it doesn't exist
    schemas_dir.mkdir(exist_ok=True)
    
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
    
    version = current_template['version']
    archive_path = schemas_dir / f"v{version}.yaml"
    
    # Check if this version already exists
    if archive_path.exists():
        # Compare content to see if it's the same
        try:
            existing_content = load_yaml(archive_path)
            if existing_content == current_template:
                print(f"Schema version {version} already archived and unchanged.")
                sys.exit(0)
            else:
                print(f"Error: Version {version} already exists with different content!")
                print("Please increment the version number in template.yaml")
                sys.exit(1)
        except Exception as e:
            print(f"Error reading existing schema: {e}")
            sys.exit(1)
    
    # Archive the current version
    try:
        shutil.copy2(template_path, archive_path)
        print(f"✓ Archived schema version {version} to {archive_path}")
    except Exception as e:
        print(f"Error archiving schema: {e}")
        sys.exit(1)
    
    # Create/update version index
    index_path = schemas_dir / 'versions.txt'
    versions = []
    
    if index_path.exists():
        with open(index_path, 'r') as f:
            versions = [line.strip() for line in f if line.strip()]
    
    if version not in versions:
        versions.append(version)
        versions.sort(key=lambda v: list(map(int, v.split('.'))))
        
        with open(index_path, 'w') as f:
            f.write('\n'.join(versions) + '\n')
    
    sys.exit(0)

if __name__ == "__main__":
    main()