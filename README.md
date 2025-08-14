# mp-yaml-configuration

This repository maintains the template and validation tools for cohort configuration YAML files. It includes version control, backwards compatibility checking, and validation tools to ensure consistent YAML structures across implementations.

## 🚀 Quick Start for New Users

### Prerequisites

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### What You Need to Know

1. **`template.yaml`** - The current template you should reference when creating your YAML files
2. **`validate_yaml.py`** - Tool to check if your YAML files are valid
3. **Pre-commit hooks** - Optional but recommended for template maintainers

### Creating Your YAML Configuration

1. **Look at the template:**
   ```bash
   cat template.yaml
   ```

2. **Create your YAML based on the example:**
   ```bash
   cp example.yaml my_cohort_config.yaml
   # Edit my_cohort_config.yaml with your values
   ```
   
   💡 **Tip**: We recommend copying `example.yaml` rather than `template.yaml` because it contains real values you can modify, while template.yaml has placeholders like `<int>` and `<string>`.

3. **Validate your YAML:**
   ```bash
   python validate_yaml.py my_cohort_config.yaml
   ```
   
   You should see: `✅ Validation PASSED`

### For Template Maintainers Only

**⚠️ IMPORTANT**: Pre-commit hooks must be installed by each person who wants to modify the template. They are NOT automatic when cloning the repo.

If you need to modify `template.yaml`:

1. **Install pre-commit hooks (one-time setup):**
   ```bash
   pip install -r requirements.txt  # If not already done
   pre-commit install
   ```

2. **Make your changes:**
   - Edit `template.yaml`
   - **INCREMENT the version** (e.g., `1.0` → `1.1`)
   - You can only ADD new optional fields
   - You CANNOT remove fields or change types

3. **Commit your changes:**
   ```bash
   git add template.yaml
   git commit -m "Add new optional field X"
   ```
   
   The pre-commit hooks will automatically:
   - Check backwards compatibility
   - Archive the new version to `schemas/`
   - Reject the commit if compatibility is broken

## Features

- **Schema Versioning**: All template changes are versioned for backwards compatibility
- **Pre-commit Hooks**: Automatic validation to ensure template changes don't break existing implementations
- **Schema Archive**: All previous versions are stored in `schemas/` directory
- **YAML Validator**: Tool to validate user implementations against the template

## Repository Structure

```
mp-yaml-configuration/
├── template.yaml           # Current template (always latest version)
├── example.yaml           # Example implementation
├── validate_yaml.py       # Validation tool for user YAMLs
├── schemas/               # Archive of all template versions
│   ├── v1.0.yaml
│   └── versions.txt      # Version index
├── scripts/               # Pre-commit hook scripts
│   ├── check_compatibility.py
│   └── archive_schema.py
└── .pre-commit-config.yaml
```

## Setup

### Installing Pre-commit Hooks

To enable automatic backwards compatibility checking:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

Now, whenever you modify `template.yaml`, the pre-commit hooks will:
1. Check backwards compatibility with the previous version
2. Ensure the version number is incremented
3. Archive the new version to `schemas/`

## Working with Templates

### Modifying the Template

1. Edit `template.yaml`
2. **Increment the version number** (e.g., `1.0` → `1.1`)
3. Commit your changes - hooks will validate automatically

**Important Rules:**
- You can ADD new optional fields
- You CANNOT remove existing fields
- You CANNOT change field types
- All changes must maintain backwards compatibility

### Version Guidelines

- Use semantic versioning (e.g., `1.0`, `1.1`, `2.0`)
- Major version: Breaking changes (though discouraged)
- Minor version: New optional fields or features

## Validating YAML Implementations

Use the included validator to check if YAML files conform to the template:

```bash
# Validate against current template
python validate_yaml.py my_config.yaml

# Validate against specific version
python validate_yaml.py my_config.yaml --schema-version 1.0

# Strict mode (warnings as errors)
python validate_yaml.py my_config.yaml --strict
```

### Validation Checks

The validator performs these checks:
- All required fields are present (`cohort`, `task`, `task_variation`)
- Field types match the template
- Column specifications are valid (name, index, or range)
- Warnings for unknown fields
- Warnings for missing optional fields

### Example Valid YAML

```yaml
cohort: "cohort_5"
task: "LL"
task_variation: "scene_pairs"

input_feature_columns:
  - range:
      start: feature_000
      end: feature_100
  - feature_101

output_feature_columns:
  - accuracy
  - reaction_time

irrelevant_to_ml_models_columns:
  - session_id
  - timestamp

cohort_description: "Cohort 5 with scene pair comparisons"
```

## Template Schema Reference

### Required Fields

- `cohort`: String cohort identifier (e.g., "cohort_5", "pilot_study_A")
- `task`: String task type (e.g., "LL", "MAB")
- `task_variation`: String variation name (keep consistent across cohorts)

### Optional Fields

- `input_feature_columns`: List of input features
- `output_feature_columns`: List of output/target features
- `irrelevant_to_ml_models_columns`: Columns to keep but exclude from ML
- `cohort_description`: Text description of the cohort

### Column Specifications

Columns can be specified as:
1. **Name**: `"feature_001"`
2. **Index**: `42`
3. **Range**: 
   ```yaml
   range:
     start: feature_000
     end: feature_500
   ```

## Contributing

When contributing template changes:
1. Ensure changes are backwards compatible
2. Update version number
3. Test with existing YAML files
4. Document new fields in this README