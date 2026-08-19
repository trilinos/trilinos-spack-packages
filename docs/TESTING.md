# Testing Guide

This project has three levels of testing for Trilinos Spack packages.

## Test Levels

### 1. Quick Tests (< 1 minute)
Basic smoke tests that verify Spack commands work.

```bash
./docker-run.sh quick
```

**What it runs:**
- `test_spack_version` - Spack is installed
- `test_spack_list` - Can list packages
- `test_spack_find` - Can find installed packages

### 2. Fast Tests (5-30 minutes)
Validates all package definitions WITHOUT compilation. **This is what you want for development.**

```bash
./docker-run.sh fast
```

**What it runs:**
- All quick tests
- `test_spack_info[package]` - Package metadata is valid (for each package)
- `test_spack_spec[package]` - Dependency specs resolve correctly (for each package)

**Skips:**
- `test_spack_install` - Real compilation tests

### 3. Nightly/Full Tests (8-9 hours)
Runs ALL tests including real compilation and installation.

```bash
./docker-run.sh nightly
# or
./docker-run.sh full
# or
./docker-cdash.sh Nightly  # Also submits to CDash
```

**What it runs:**
- All quick tests
- All spec validation tests
- `test_spack_install[package]` - **REAL compilation** for each package

## Test Markers

Tests are marked with pytest markers:
- `@pytest.mark.quick` - Basic smoke tests
- `@pytest.mark.install` - Real compilation tests (excluded in fast mode)

## Performance Optimizations

### Dependency Reuse
The install tests use `--reuse` flag to avoid rebuilding common dependencies:
- OpenMPI, BLAS, Boost, Kokkos, Kokkos-Kernels
- These are pre-built in the `with-deps` Docker stage

### Package Reuse
Set `SPACK_OVERWRITE=1` to force reinstallation of packages:
```bash
# Fast: reuse already-installed packages
./docker-cdash.sh Nightly

# Slow: force reinstall everything
SPACK_OVERWRITE=1 ./docker-cdash.sh Nightly
```

## Recommended Workflow

1. **Development**: Run `./docker-run.sh fast` after changes
2. **Pre-commit**: Ensure fast tests pass
3. **Nightly CI**: Run full suite with real compilation
4. **Debugging**: Use `./docker-run.sh shell` for interactive testing
