# Test Suite Optimization Guide

## Installation

First, install the test dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

### Fast Parallel Execution (Recommended)

Run tests in parallel using all CPU cores:

```bash
# Quick tests only (fastest feedback)
pytest test/ -m quick -n auto

# All tests except slow install tests
pytest test/ -m "not slow" -n auto

# Full test suite in parallel
pytest test/ -n auto
```

### Selective Test Execution

```bash
# Run only quick smoke tests
pytest test/ -m quick

# Run only slow tests
pytest test/ -m slow

# Run only install tests
pytest test/ -m install

# Run everything except install tests
pytest test/ -m "not install"

# Combine markers: quick OR info tests
pytest test/ -m "quick or not slow"
```

### Sequential Execution (Debug Mode)

Run tests sequentially for easier debugging:

```bash
# Quick tests only
pytest test/quick-test.py -v

# Long tests without installs
pytest test/long-test.py -m "not slow" -v

# Full suite
pytest test/ -v
```

### CTest Integration

Run via CMake/CTest with parallel execution:

```bash
# Configure
cmake -B build .

# Run tests in parallel (uses all cores)
cd build && ctest -j $(nproc)

# Run specific test
cd build && ctest -R test_spack_version
```

## Performance Tips

1. **Parallel execution** (`-n auto`) gives the biggest speedup
2. **Quick marker** (`-m quick`) runs only basic sanity checks
3. **Exclude slow tests** (`-m "not slow"`) skips expensive install tests
4. **Package list is cached** for the entire test session

## Expected Performance

- **Quick tests only**: ~5-10 seconds
- **All tests except install** (parallel): ~1-2 minutes
- **Full suite with installs** (parallel): 10-30 minutes (depending on packages)

## Marker Reference

- `quick`: Fast smoke tests (version, list, find commands)
- `slow`: Long-running tests (actual package installations)
- `install`: Tests that perform `spack install`
