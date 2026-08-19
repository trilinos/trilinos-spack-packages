# Testing Guide

Complete guide to testing Trilinos Spack packages.

## Quick Start

### Docker/Podman (Recommended)

```bash
# Build container (one-time)
./docker-build.sh

# Run quick tests
./docker-run.sh quick

# Submit to CDash
./docker-cdash.sh Experimental
```

See [README_DOCKER.md](README_DOCKER.md) for container details.

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run quick tests
pytest test/ -m quick -n auto

# Run all tests except slow installs
pytest test/ -m "not slow" -n auto
```

## Test Organization

Tests are in the `test/` directory:

- **`test/quick_test.py`** - Fast smoke tests (version, list, find, info)
- **`test/long_test.py`** - Comprehensive tests (info, spec, install)

### Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.quick` - Fast smoke tests (~5 seconds total)
- `@pytest.mark.slow` - Long-running tests (installs take hours)
- `@pytest.mark.install` - Tests that run `spack install`

## Running Tests

### Option 1: Docker (Recommended)

**Quick smoke tests:**
```bash
./docker-run.sh quick
# Runs: test_spack_version, test_spack_list, test_spack_find
# Time: ~5 seconds
```

**Fast tests (no installs):**
```bash
./docker-run.sh fast
# Runs: All tests except those marked @pytest.mark.slow
# Time: ~2-3 minutes
```

**Full test suite:**
```bash
./docker-run.sh full
# Runs: Everything including install tests
# Time: ~8-9 hours (with --fake: ~5 minutes)
```

**Interactive shell (debugging):**
```bash
./docker-run.sh shell
cd build
cat Testing/Temporary/LastTest.log
```

### Option 2: CDash Submission

**Submit to CDash:**
```bash
# All tests
./docker-cdash.sh Experimental

# Just quick tests
./docker-cdash.sh Experimental 'test_spack_(version|list|find)'

# Specific package
./docker-cdash.sh Experimental 'test_spack_info\[trilinos-teuchos\]'
```

**Run without submitting:**
```bash
./docker-cdash.sh Experimental --no-submit
```

**Show output for failures:**
```bash
./docker-cdash.sh Experimental --output-on-failure
```

**Combine options:**
```bash
./docker-cdash.sh Experimental 'test_spack_info' --no-submit --output-on-failure
```

See [README_CDASH.md](README_CDASH.md) for CDash details.

### Option 3: pytest Directly

**Basic usage:**
```bash
# Quick tests only
pytest test/ -m quick -n auto -v

# All except slow
pytest test/ -m "not slow" -n auto -v

# Specific test
pytest test/quick_test.py::test_spack_version -v

# Stop on first failure
pytest test/ -x -v
```

**With detailed output:**
```bash
# Show full traceback
pytest test/ --tb=long

# Show all output (not just failures)
pytest test/ -v -s

# Show output on failure only
pytest test/ -v
```

**Debugging:**
```bash
# Re-run last failed tests
pytest test/ --lf

# Run failed first, then rest
pytest test/ --ff

# Very verbose
pytest test/ -vv
```

### Option 4: CTest/CMake

**Local CTest:**
```bash
mkdir build && cd build
cmake ..
ctest -V                              # Verbose
ctest -R test_spack_version          # Specific test
ctest -j $(nproc)                    # Parallel
```

**Submit to CDash:**
```bash
cd build
ctest -D Experimental
```

## Test Details

### Quick Tests (`@pytest.mark.quick`)

1. **test_spack_version** - Verify `spack --version` works
2. **test_spack_list** - Verify `spack list` works
3. **test_spack_find** - Verify `spack find` works

**Time:** ~1-2 seconds each
**Purpose:** Ensure basic spack functionality

### Info Tests (default, no marker)

**test_spack_info[package-name]** - Run `spack info` for each Trilinos package

**Time:** ~1 second per package
**Count:** ~46 packages
**Purpose:** Verify package metadata is accessible

### Spec Tests (default, no marker)

**test_spack_spec[package-name]** - Run `spack spec` for each Trilinos package

**Time:** ~1-2 seconds per package
**Count:** ~46 packages
**Purpose:** Verify package dependencies resolve correctly

### Install Tests (`@pytest.mark.slow` + `@pytest.mark.install`)

**test_spack_install[package-name]** - Run `spack install` for each package

**Time with --fake:** ~1 second per package (validates specs only)
**Time without --fake:** ~30-45 min first package, ~5-10 min subsequent
**Purpose:** Validate package can be installed (or test actual compilation)

**Current behavior:** Uses `--fake` flag to validate without compiling

See [README_INSTALL_TIMES.md](README_INSTALL_TIMES.md) for details on install times.

## Test Filtering

### By Marker

```bash
# Only quick tests
pytest test/ -m quick

# Only slow tests
pytest test/ -m slow

# Only install tests
pytest test/ -m install

# Everything except slow
pytest test/ -m "not slow"

# Quick OR install (but not both)
pytest test/ -m "quick or install"
```

### By Name Pattern

```bash
# All info tests
pytest test/ -k "spack_info"

# Specific package
pytest test/ -k "trilinos-teuchos"

# Multiple packages
pytest test/ -k "teuchos or tpetra"

# Exclude pattern
pytest test/ -k "not install"
```

### By File

```bash
# Only quick_test.py
pytest test/quick_test.py

# Only long_test.py
pytest test/long_test.py
```

## Test Configuration

### pytest.ini

```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    quick: marks tests as quick smoke tests
    install: marks tests that perform actual package installation

addopts = -v --tb=short
```

### CMakeLists.txt

Defines CTests that wrap pytest tests:
- Each test runs pytest with `-k` filter
- Install tests have 1-hour timeout
- Tests fail on "FAILED" in output

## Troubleshooting

### Tests not found

**Problem:** `pytest` finds 0 items

**Solution:** Test files must be named `test_*.py` or `*_test.py` (underscores, not hyphens)

### Import errors

**Problem:** `ModuleNotFoundError: No module named 'pytest'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Spack command not found

**Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'spack'`

**Solution:** Source the spack environment:
```bash
source setup-spack.sh
pytest test/
```

Or use Docker (spack already configured):
```bash
./docker-run.sh quick
```

### Timeout errors

**Problem:** Test times out after 10 minutes

**Solution:** Install tests have 1-hour timeout in CMakeLists.txt. For pytest directly:
```bash
pytest test/ --timeout=3600
```

### SSL certificate errors (CDash)

**Problem:** `SSL certificate OpenSSL verify result: unable to get local issuer certificate`

**Solution:** Already fixed - we use HTTP instead of HTTPS. Rebuild container:
```bash
./docker-build.sh
```

## Performance Tips

1. **Use parallel execution** (`-n auto`) for 5-10x speedup
2. **Filter tests** with markers to run only what you need
3. **Use Docker** to avoid environment setup issues
4. **Use --fake flag** for install tests (validates without compiling)
5. **Sequential install tests** share build cache (later ones are faster)

## Expected Performance

| Test Type | Count | Time (Parallel) | Time (Sequential) |
|-----------|-------|-----------------|-------------------|
| Quick only | 3 | ~5 sec | ~5 sec |
| Info tests | ~46 | ~30 sec | ~1 min |
| Spec tests | ~46 | ~1 min | ~2 min |
| All non-slow | ~95 | ~2 min | ~3-4 min |
| Install (--fake) | ~46 | ~1 min | ~2 min |
| Install (real, cold) | ~46 | N/A | ~8-9 hours |
| Install (real, warm) | ~46 | N/A | ~8 hours |

## Related Documentation

- [README_DOCKER.md](README_DOCKER.md) - Container workflows
- [README_CDASH.md](README_CDASH.md) - CDash integration
- [README_INSTALL_TIMES.md](README_INSTALL_TIMES.md) - Why installs take long
- [README_BUILD_OPTIONS.md](README_BUILD_OPTIONS.md) - Container build options
