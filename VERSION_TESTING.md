# Testing Different Trilinos Versions/Branches

This guide explains how to test different Trilinos branches (develop, master, custom branches) instead of just the default.

## Available Trilinos Versions

From `trilinos_base_class/package.py`:

```python
version("jfrye-spack-changes", branch="changes-for-spack")
version("develop", branch="develop")
# version("master", branch="master")  # Can be uncommented
```

You can test any defined version or branch.

---

## Quick Start

### Test Develop Branch (Default)

```bash
# Using the version-aware script
./docker-run-with-version.sh quick develop
./docker-run-with-version.sh fast develop
./docker-run-with-version.sh full develop
```

### Test Custom Branch

```bash
# Test the custom changes branch
./docker-run-with-version.sh quick jfrye-spack-changes
./docker-run-with-version.sh fast jfrye-spack-changes
```

### Test Without Specifying (Uses develop)

```bash
# Defaults to develop
./docker-run-with-version.sh quick
```

---

## New Scripts

### 1. docker-run-with-version.sh

Enhanced version of `docker-run.sh` with version support.

**Usage:**
```bash
./docker-run-with-version.sh [TEST_TYPE] [TRILINOS_VERSION] [EXTRA_PYTEST_ARGS]
```

**Examples:**
```bash
# Quick tests with develop branch
./docker-run-with-version.sh quick develop

# Fast tests with custom branch
./docker-run-with-version.sh fast jfrye-spack-changes

# Full tests with develop and specific test filter
./docker-run-with-version.sh full develop -k "tpetra or muelu"

# Interactive shell with develop
./docker-run-with-version.sh shell develop
```

### 2. nightly-with-version.sh

Nightly script that supports version selection.

**Usage:**
```bash
./nightly-with-version.sh [TRILINOS_VERSION]
```

**Examples:**
```bash
# Test develop nightly
./nightly-with-version.sh develop

# Test custom branch nightly
./nightly-with-version.sh jfrye-spack-changes

# Default (develop)
./nightly-with-version.sh
```

### 3. test/long_test_with_version.py

Enhanced test file that reads version from environment.

**Key features:**
- Reads `TRILINOS_VERSION` environment variable
- Formats package specs as `trilinos-package@version`
- Falls back to `develop` if not specified

---

## How It Works

### Environment Variable

All scripts pass the version via environment variable:

```bash
# Script sets:
export TRILINOS_VERSION=develop

# Tests read:
version = os.environ.get('TRILINOS_VERSION', 'develop')

# Tests format specs:
"trilinos-teuchos@develop"
"trilinos-tpetra@jfrye-spack-changes"
```

### Package Specification

```python
# Without version (old way):
spack install trilinos-teuchos

# With version (new way):
spack install trilinos-teuchos@develop
spack install trilinos-teuchos@jfrye-spack-changes
```

This ensures you're testing the exact branch you want!

---

## Testing Different Branches

### Scenario 1: Test Develop Daily

```bash
# In crontab:
0 3 * * * cd /projects/trilinos-spack-packages && ./nightly-with-version.sh develop
```

### Scenario 2: Test Multiple Branches

```bash
# Monday-Friday: develop
0 3 * * 1-5 cd /projects/trilinos-spack-packages && ./nightly-with-version.sh develop

# Saturday: custom branch
0 3 * * 6 cd /projects/trilinos-spack-packages && ./nightly-with-version.sh jfrye-spack-changes

# Sunday: master (if defined)
0 3 * * 0 cd /projects/trilinos-spack-packages && ./nightly-with-version.sh master
```

### Scenario 3: Test Before Merging

```bash
# Test your branch before merging to develop
./docker-run-with-version.sh fast jfrye-spack-changes

# If passes, test develop to compare
./docker-run-with-version.sh fast develop
```

---

## Comparing Branches

### Test Both and Compare Results

```bash
# Test develop
./docker-run-with-version.sh fast develop 2>&1 | tee results-develop.log

# Test custom branch
./docker-run-with-version.sh fast jfrye-spack-changes 2>&1 | tee results-custom.log

# Compare
diff results-develop.log results-custom.log
```

### CDash Comparison

Submit both to CDash with different names:

```bash
# Develop submission
TRILINOS_VERSION=develop ./docker-cdash.sh Experimental

# Custom branch submission
TRILINOS_VERSION=jfrye-spack-changes ./docker-cdash.sh Experimental
```

View both on CDash dashboard and compare.

---

## Adding New Branches

### Step 1: Add to trilinos_base_class/package.py

```python
# Edit: spack_repo/trilinos/packages/trilinos_base_class/package.py
version("my-feature", branch="feature/my-awesome-feature")
trilinos_versions.append("my-feature")
```

### Step 2: Rebuild Container

```bash
# Rebuild to pick up new version
./docker-build-optimized.sh
```

### Step 3: Test New Branch

```bash
# Test it!
./docker-run-with-version.sh quick my-feature
./docker-run-with-version.sh fast my-feature
```

---

## Migration from Original Scripts

### Option 1: Use New Scripts Alongside Old

```bash
# Old way (no version control)
./docker-run.sh quick

# New way (with version)
./docker-run-with-version.sh quick develop
```

Both work! Choose based on needs.

### Option 2: Replace Original Scripts

```bash
# Backup
cp docker-run.sh docker-run.sh.backup

# Replace
cp docker-run-with-version.sh docker-run.sh

# Update to accept version as second arg
# (Edit docker-run.sh to add version parameter)
```

### Option 3: Symlink for Convenience

```bash
# Default to develop
ln -s docker-run-with-version.sh docker-run-develop.sh

# Create aliases for common branches
ln -s docker-run-with-version.sh docker-run-custom.sh

# Use like:
./docker-run-develop.sh quick  # Tests develop
./docker-run-custom.sh quick   # Tests jfrye-spack-changes
```

---

## Environment Variable Method (Alternative)

If you prefer environment variables over arguments:

```bash
# Set once
export TRILINOS_VERSION=develop

# Run tests (will use develop)
./docker-run.sh quick
./docker-run.sh fast

# Change version
export TRILINOS_VERSION=jfrye-spack-changes

# Run tests (will use custom branch)
./docker-run.sh fast
```

The test files already support this!

---

## Troubleshooting

### Version Not Found

```bash
# Error: No version 'my-branch' found

# Check what versions exist:
spack info trilinos-teuchos

# Make sure it's defined in:
spack_repo/trilinos/packages/trilinos_base_class/package.py
```

### Tests Still Use Wrong Version

```bash
# Verify environment variable is set
docker run --rm trilinos-spack-packages:latest \
    bash -c 'echo $TRILINOS_VERSION'

# Should show your version
```

### Spec Fails for Version

```bash
# Test if version resolves
spack spec trilinos-teuchos@develop

# If fails, check dependency constraints
```

---

## Summary

**New capabilities:**
- ✓ Test any defined Trilinos branch
- ✓ Compare multiple branches
- ✓ Schedule different branches on different days
- ✓ Environment variable or argument based
- ✓ Backward compatible with existing scripts

**Use cases:**
1. **Daily CI**: Test develop every night
2. **Feature branches**: Test before merging
3. **Regression testing**: Compare develop vs release
4. **Multi-branch validation**: Test multiple branches weekly

**Get started:**
```bash
# Test develop (default)
./docker-run-with-version.sh quick develop

# Test custom branch
./docker-run-with-version.sh quick jfrye-spack-changes

# Nightly with develop
./nightly-with-version.sh develop
```
