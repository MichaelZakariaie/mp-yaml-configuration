# Test Script for Quick Start

Run these commands to test the new user flow:

```bash
# 1. Test creating and validating a YAML
cp example.yaml my_test.yaml
python validate_yaml.py my_test.yaml
# Expected: ✅ Validation PASSED

# 2. Test validation with errors
python validate_yaml.py test_invalid.yaml
# Expected: ❌ Validation FAILED with errors listed

# 3. Test breaking backwards compatibility (for maintainers)
# First install pre-commit if not already done:
pip install pre-commit
pre-commit install

# Try to remove a field (should fail):
sed -i '' '/cohort:/d' template.yaml
git add template.yaml
git commit -m "Remove cohort field"
# Expected: Pre-commit hook should REJECT this

# Restore template:
git checkout -- template.yaml

# Try to change version without changes (should fail):
sed -i '' 's/version: "1.0"/version: "1.1"/' template.yaml
git add template.yaml
git commit -m "Bump version without changes"
# Expected: Should work (archives v1.1)

# Try to commit without version change:
git checkout -- template.yaml
echo "new_optional_field: <string>" >> template.yaml
git add template.yaml  
git commit -m "Add field without version bump"
# Expected: Should FAIL - version must be incremented

# Restore:
git checkout -- template.yaml
```