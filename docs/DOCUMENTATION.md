# Documentation Index

Complete guide to all documentation in this repository.

## Getting Started

**Start here:** [README.md](README.md)
- Quick start guide
- Basic usage
- Common tasks
- Troubleshooting

## Testing Documentation

### [README_TESTING.md](README_TESTING.md) - Complete Testing Guide
**Read this for:** Running tests locally or in containers

**Contents:**
- Docker/Podman workflows (recommended)
- pytest usage and options
- CTest/CMake integration
- Test markers (`@pytest.mark.quick`, `@pytest.mark.slow`)
- Test filtering and selection
- Performance tips
- Expected test times
- Troubleshooting test issues

**Quick commands:**
```bash
./docker-run.sh quick           # Fast smoke tests
./docker-run.sh fast            # All non-slow tests
pytest test/ -m quick -n auto   # Local pytest
```

### [README_CDASH.md](README_CDASH.md) - CDash Integration
**Read this for:** Submitting test results to CDash dashboards

**Contents:**
- What is CDash
- Dashboard types (Experimental, Nightly, Continuous)
- How to submit results
- What gets submitted
- Viewing results on my.cdash.org
- Configuration files (CTestConfig.cmake)
- Automated submissions for CI/CD
- Troubleshooting SSL issues
- Integration with pytest

### [README_NIGHTLY.md](README_NIGHTLY.md) - Automated Nightly Testing
**Read this for:** Setting up automated nightly test runs

**Contents:**
- Quick setup with cron (5 minutes)
- Cron schedule examples
- Email notifications
- Test options (fast vs comprehensive)
- Monitoring and troubleshooting
- GitHub Actions alternative
- Jenkins alternative
- Best practices
- Recommended schedules

**Quick commands:**
```bash
./docker-cdash.sh Experimental                        # Submit all tests
./docker-cdash.sh Experimental --no-submit            # Run without submitting
./docker-cdash.sh Experimental 'test_pattern' \
  --no-submit --output-on-failure                     # Debug specific tests
```

**View results:** https://my.cdash.org/index.php?project=Trilinos

## Container Documentation

### [README_DOCKER.md](README_DOCKER.md) - Container Workflows
**Read this for:** Using Docker or Podman to run tests

**Contents:**
- Quick start guide
- Podman vs Docker detection
- Build process and stages
- Cache optimization
- Make targets
- Interactive debugging
- Multi-stage build benefits
- Volume mounting

**Quick commands:**
```bash
./docker-build.sh              # Build container
./docker-run.sh quick          # Run quick tests
./docker-run.sh shell          # Interactive shell
```

### [README_PODMAN.md](README_PODMAN.md) - Podman Details
**Read this for:** Podman-specific features and differences

**Contents:**
- Podman advantages (rootless, daemonless)
- Differences from Docker
- Installation instructions
- Podman-compose usage
- Performance considerations

### [README_BUILD_OPTIONS.md](README_BUILD_OPTIONS.md) - Build Strategies
**Read this for:** Understanding container build options and when to use each

**Contents:**
- Default build (fast, small, recommended)
- With-deps build (slow, large, for real installs)
- Build stage comparison
- When to pre-build dependencies
- Build time estimates
- Image size comparison
- Use case recommendations
- Example workflows

**Key decision:**
- **Default (`app` stage):** 2-3 min build, use with `--fake` tests ← Use this!
- **With-deps (`with-deps` stage):** 30-60 min build, for real compilation testing

## Performance Documentation

### [README_INSTALL_TIMES.md](README_INSTALL_TIMES.md) - Build Time Analysis
**Read this for:** Understanding why builds take long and how to optimize

**Contents:**
- Slowest packages to build (Kokkos, Boost, OpenMPI, etc.)
- Dependency chain analysis
- Why first test takes longest
- Optimization strategies
- Pre-building dependencies
- Using spack buildcache
- Sequential vs parallel testing
- Build time estimates (cold vs warm cache)
- Real-world timing for full suite

**Key insights:**
- Kokkos: 10-30 min (used by 16+ packages)
- First test: 30-60 min (builds all deps)
- Later tests: 5-10 min (reuse deps)
- With `--fake`: <5 sec per package ← Current approach

## Network/SSL Documentation

### [README_SSL_FIXES.md](README_SSL_FIXES.md) - Corporate Network Workarounds
**Read this for:** Working behind corporate firewalls or with SSL issues

**Contents:**
- SSL certificate problems
- Git SSL configuration
- Spack SSL settings
- curl configuration
- CDash submission SSL (now uses HTTP)
- Quick fixes and workarounds

**Current status:** Fixed! CDash now uses HTTP instead of HTTPS to avoid SSL issues.

## Quick Reference

### Common Commands

```bash
# Testing
./docker-build.sh                    # Build container (2-3 min)
./docker-run.sh quick                # Quick tests (5 sec)
./docker-run.sh fast                 # Fast tests (2-3 min)
./docker-cdash.sh Experimental       # Submit to CDash (5 min)

# Local pytest
pytest test/ -m quick -n auto        # Parallel quick tests
pytest test/ -m "not slow" -n auto   # All except installs
pytest test/ -k "teuchos" -v         # Specific package

# Debugging
./docker-run.sh shell                # Interactive container
./docker-cdash.sh Experimental \
  'test_pattern' --no-submit \
  --output-on-failure                # Debug test failures
```

### Documentation Map by Task

**"I want to run tests quickly"**
→ [README_TESTING.md](README_TESTING.md) → Docker Quick Start section

**"I want to submit to CDash"**
→ [README_CDASH.md](README_CDASH.md) → Quick Start section

**"I want to run tests automatically every night"**
→ [README_NIGHTLY.md](README_NIGHTLY.md) → Quick Setup section

**"Tests are taking too long"**
→ [README_INSTALL_TIMES.md](README_INSTALL_TIMES.md) → Optimization Strategies

**"Should I pre-build dependencies?"**
→ [README_BUILD_OPTIONS.md](README_BUILD_OPTIONS.md) → When to Use Each

**"Container build is failing"**
→ [README_DOCKER.md](README_DOCKER.md) → Troubleshooting
→ [README_SSL_FIXES.md](README_SSL_FIXES.md) → If SSL-related

**"I'm getting SSL certificate errors"**
→ [README_SSL_FIXES.md](README_SSL_FIXES.md) → Already fixed, rebuild container

**"How do I debug failing tests?"**
→ [README_TESTING.md](README_TESTING.md) → Troubleshooting section
→ Use: `./docker-cdash.sh Experimental 'test_name' --no-submit --output-on-failure`

**"Why did this package take 45 minutes to install?"**
→ [README_INSTALL_TIMES.md](README_INSTALL_TIMES.md) → Dependency Chain Analysis

## File Reference

### Test Files
- `test/quick_test.py` - Fast smoke tests (version, list, find)
- `test/long_test.py` - Comprehensive tests (info, spec, install)

### Configuration Files
- `pytest.ini` - pytest configuration and markers
- `CMakeLists.txt` - CTest integration, test definitions
- `CTestConfig.cmake` - CDash server configuration
- `CTestScript.cmake` - CDash submission script with SSL workarounds
- `requirements.txt` - Python test dependencies

### Scripts
- `docker-build.sh` - Build container image
- `docker-run.sh` - Run pytest tests in container
- `docker-cdash.sh` - Run CTest and submit to CDash
- `setup-spack.sh` - Initialize spack environment

### Package Definitions
- `spack_repo/trilinos/packages/*/package.py` - Individual package definitions
- `base_package.py` - Base class for all packages
- `generate_spack_packages.py` - Generate packages from XML

## Recent Changes

### August 2026 Updates

**Test Discovery Fix:**
- Renamed `test/quick-test.py` → `test/quick_test.py`
- Renamed `test/long-test.py` → `test/long_test.py`
- Reason: pytest requires underscores, not hyphens

**Parametrization Fix:**
- Removed duplicate `@pytest.mark.parametrize` decorators
- Now using only `pytest_generate_tests` hook
- Fixes "duplicate parametrization" error

**CDash Integration:**
- Changed from HTTPS to HTTP to avoid SSL certificate issues
- Added `docker-cdash.sh` script for easy submission
- Added test filtering support
- Added `--no-submit` and `--output-on-failure` flags

**Install Tests:**
- Added `--fake` flag to validate without compiling
- Fixed invalid `-k` flag (not supported by spack)
- Increased timeout to 1 hour for real installs
- Tests now run in seconds instead of hours

**Documentation:**
- Created comprehensive documentation index (this file)
- Updated all README files with current workflows
- Added build options guide
- Added performance analysis

## Contributing to Documentation

When adding new features or fixing issues:

1. Update relevant README files
2. Add entry to this index
3. Update main README.md with high-level info
4. Add troubleshooting section if applicable
5. Include example commands
6. Test all documented commands

## Questions?

- Check this index for the right documentation
- Search documentation with: `grep -r "your topic" README*.md`
- Open an issue: https://github.com/trilinos/trilinos-spack-packages/issues
