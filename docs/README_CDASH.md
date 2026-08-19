# CDash Integration Guide

This document explains how to submit test results to CDash (https://my.cdash.org).

## What is CDash?

CDash is an open-source, web-based software testing server. It aggregates, analyzes and displays the results of software testing processes submitted from clients around the world. This project submits test results to the Trilinos project on my.cdash.org.

## Quick Start

Submit test results to CDash using the Docker-based workflow:

```bash
./docker-cdash.sh Experimental
```

View results at: https://my.cdash.org/index.php?project=Trilinos

## Dashboard Types

### Experimental (Default)
One-time test submissions, typically used for:
- Feature development
- Bug fixes
- Manual testing
- Ad-hoc validation

```bash
./docker-cdash.sh Experimental
```

### Nightly
Scheduled nightly builds, used for:
- Automated nightly testing
- Tracking trends over time
- Regression detection

```bash
./docker-cdash.sh Nightly
```

### Continuous
Continuous integration builds, used for:
- CI/CD pipelines
- Pre-merge validation
- Frequent integration testing

```bash
./docker-cdash.sh Continuous
```

## What Gets Submitted?

The CDash submission includes:

1. **Build Information**
   - Build name: `Trilinos_Spack_Packages-<git-branch>`
   - Hostname and system information
   - Build timestamp

2. **Test Results**
   - Test status (Passed/Failed)
   - Test timing
   - Test output
   - Number of tests run

3. **Test Categories** (via CTest)
   - `test_spack_version` - Verify spack version command
   - `test_spack_list` - Verify spack list command
   - `test_spack_find` - Verify spack find command
   - `test_spack_info[<package>]` - Info for each Trilinos package
   - `test_spack_spec[<package>]` - Spec for each Trilinos package
   - `test_spack_install[<package>]` - Installation test for each package

## Configuration

CDash settings are configured in `CTestConfig.cmake`:

```cmake
SET(CTEST_DROP_SITE "my.cdash.org")
SET(CTEST_PROJECT_NAME "Trilinos")
SET(CTEST_DROP_LOCATION "/submit.php?project=Trilinos")
```

## Local (Non-Docker) Submission

If you prefer to run CDash submission locally without Docker:

```bash
# Setup environment
source setup-spack.sh

# Configure and run
mkdir build && cd build
cmake ..
ctest -D Experimental -V
```

The `-V` flag enables verbose output to see submission progress.

## Troubleshooting

### Build not showing up on CDash?

1. Check network connectivity:
   ```bash
   curl -I https://my.cdash.org
   ```

2. Verify project exists on CDash:
   - Visit https://my.cdash.org
   - Search for "Trilinos" project

3. Check submission output for errors:
   ```bash
   ./docker-cdash.sh Experimental 2>&1 | grep -i error
   ```

### SSL/Certificate errors?

The Dockerfile is configured to handle corporate SSL environments:
- `GIT_SSL_NO_VERIFY=1` for git operations
- Spack configured with `verify_ssl: false`

If you still encounter SSL issues with CDash submission, check the CTest output for specific SSL errors.

### Tests failing?

Before submitting to CDash, verify tests pass locally:

```bash
./docker-run.sh quick
```

This runs a quick smoke test to ensure the basic functionality works.

## Automated Submissions

For automated nightly or continuous submissions, you can:

1. **Use cron** (Linux/macOS):
   ```cron
   0 2 * * * cd /path/to/trilinos-spack-packages && ./docker-cdash.sh Nightly
   ```

2. **Use GitHub Actions** (see `.github/workflows/` for examples)

3. **Use Jenkins/GitLab CI** with the `docker-cdash.sh` script

## Viewing Results

After submission, view your results at:
https://my.cdash.org/index.php?project=Trilinos

Results are organized by:
- **Dashboard Type** (Experimental/Nightly/Continuous)
- **Build Name** (includes git branch)
- **Date/Time** of submission

## Advanced: Custom Build Names

To customize the build name shown on CDash, edit `CMakeLists.txt`:

```cmake
set(BUILDNAME "Trilinos_Spack_Packages-${GIT_BRANCH}" CACHE STRING "CDash build name" FORCE)
```

You can add additional identifiers like hostname, OS, or configuration options.

## Integration with pytest

The project uses pytest for test implementation, but CTest for CDash submission:

1. **pytest** - Test execution and discovery
   - Files: `test/quick_test.py`, `test/long_test.py`
   - Markers: `@pytest.mark.quick`, `@pytest.mark.slow`

2. **CTest** - CDash integration layer
   - File: `CMakeLists.txt`
   - Wraps pytest tests as CTest tests
   - Handles CDash submission protocol

This hybrid approach gives us:
- Modern Python testing (pytest)
- CDash dashboard integration (CTest)
- Best of both worlds!
