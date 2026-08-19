# Trilinos Spack Packages

Modular Spack packages for individual Trilinos components, enabling fine-grained dependency management and faster builds.

## Quick Start

```bash
# 1. Clone the repository
git clone git@github.com:trilinos/trilinos-spack-packages.git
cd trilinos-spack-packages

# 2. Setup spack
source setup-spack.sh

# 3. List available packages
spack list trilinos-
```

## Testing

### Docker/Podman (Recommended)

```bash
# Build container
./docker-build.sh

# Run quick tests
./docker-run.sh quick

# Submit to CDash
./docker-cdash.sh Experimental
```

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run quick tests
pytest test/ -m quick -n auto
```

## CDash Integration

Submit test results to https://my.cdash.org/index.php?project=Trilinos

```bash
# Run and submit to CDash
./docker-cdash.sh Experimental

# Run specific tests only
./docker-cdash.sh Experimental 'test_spack_(version|list|find)'

# Run without submitting (local validation)
./docker-cdash.sh Experimental --no-submit --output-on-failure
```

## Available Packages

List all Trilinos packages:

```bash
spack list trilinos-
```

Example packages:
- `trilinos-teuchos` - Core utilities
- `trilinos-tpetra` - Parallel linear algebra
- `trilinos-belos` - Iterative solvers
- `trilinos-muelu` - Multigrid preconditioners
- `trilinos-ifpack2` - Preconditioners
- And ~40 more...

## Installation

```bash
# Install a specific package
spack install trilinos-teuchos

# Install with MPI support
spack install trilinos-tpetra +mpi

# Install with CUDA support
spack install trilinos-tpetra +cuda
```

## Documentation

### Testing
- **[README_TESTING.md](README_TESTING.md)** - Complete testing guide
  - Docker/Podman workflows
  - pytest usage
  - CTest integration
  - Test markers and filtering

### CDash
- **[README_CDASH.md](README_CDASH.md)** - CDash integration guide
  - Dashboard types (Experimental, Nightly, Continuous)
  - Submission configuration
  - Troubleshooting SSL issues
  - Automated submissions

### Docker/Podman
- **[README_DOCKER.md](README_DOCKER.md)** - Container usage guide
  - Building containers
  - Running tests
  - Multi-stage builds
  - Cache optimization

- **[README_PODMAN.md](README_PODMAN.md)** - Podman-specific details
  - Rootless containers
  - Podman vs Docker differences

### Build Options
- **[README_BUILD_OPTIONS.md](README_BUILD_OPTIONS.md)** - Container build strategies
  - Default vs with-deps builds
  - When to pre-build dependencies
  - Build time comparisons
  - Recommendations

### Performance
- **[README_INSTALL_TIMES.md](README_INSTALL_TIMES.md)** - Why installs take long
  - Dependency analysis
  - Build time estimates
  - Optimization strategies
  - Pre-building common dependencies

### SSL/Corporate Networks
- **[README_SSL_FIXES.md](README_SSL_FIXES.md)** - SSL certificate workarounds
  - Corporate proxy configuration
  - Certificate verification bypass
  - Git SSL settings

## Package Structure

```
trilinos-spack-packages/
├── spack_repo/trilinos/packages/     # Spack package definitions
│   ├── trilinos_teuchos/
│   ├── trilinos_tpetra/
│   └── ...
├── test/                              # Test suite
│   ├── quick_test.py                  # Fast smoke tests
│   └── long_test.py                   # Comprehensive tests
├── docker-build.sh                    # Build container
├── docker-run.sh                      # Run tests in container
├── docker-cdash.sh                    # Run and submit to CDash
└── generate_spack_packages.py         # Package generator
```

## Development Workflow

### 1. Make Changes

Edit package definitions:
```bash
vim spack_repo/trilinos/packages/trilinos_foo/package.py
```

### 2. Test Locally

```bash
# Quick validation
pytest test/ -m quick -v

# Full validation (without actual installs)
pytest test/ -m "not slow" -v
```

### 3. Test in Container

```bash
# Rebuild container
./docker-build.sh

# Run tests
./docker-run.sh quick
```

### 4. Submit to CDash

```bash
# Submit experimental results
./docker-cdash.sh Experimental
```

## Common Tasks

### Add a New Package

1. Update the XML dependency file in `xml_files/`
2. Regenerate packages:
   ```bash
   python3 generate_spack_packages.py --xml xml_files/TrilinosPackageDependencies.xml
   ```
3. Test the new package:
   ```bash
   spack info trilinos-newpackage
   spack spec trilinos-newpackage
   ```

### Update Package Dependencies

1. Edit `base_package.py` for common dependencies
2. Or edit specific package files in `spack_repo/trilinos/packages/`
3. Test changes:
   ```bash
   pytest test/ -k "newpackage" -v
   ```

### Debug Test Failures

```bash
# Run specific test with verbose output
./docker-cdash.sh Experimental 'test_spack_info\[trilinos-teuchos\]' \
  --no-submit --output-on-failure

# Or get interactive shell
./docker-run.sh shell
pytest test/ -k "teuchos" -vv
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build container
        run: ./docker-build.sh
      
      - name: Run tests
        run: ./docker-run.sh quick
      
      - name: Submit to CDash
        run: ./docker-cdash.sh Experimental
```

### Jenkins Example

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh './docker-build.sh'
            }
        }
        stage('Test') {
            steps {
                sh './docker-run.sh fast'
            }
        }
        stage('CDash') {
            steps {
                sh './docker-cdash.sh Nightly'
            }
        }
    }
}
```

## Troubleshooting

### Spack can't find packages

```bash
# Re-add the repository
spack repo add spack_repo/trilinos

# Verify it's added
spack repo list
```

### Tests not discovering

Make sure test files use underscores (`test_*.py` not `test-*.py`):
```bash
ls test/
# Should see: quick_test.py, long_test.py
```

### Container build fails

Check you have enough disk space:
```bash
df -h
```

For corporate networks, see [README_SSL_FIXES.md](README_SSL_FIXES.md)

### CDash submission fails

Already fixed (uses HTTP instead of HTTPS). Rebuild container:
```bash
./docker-build.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker: `./docker-run.sh quick`
5. Submit PR with passing CDash results

## License

See [LICENSE](LICENSE) file.

## Support

- Issues: https://github.com/trilinos/trilinos-spack-packages/issues
- Trilinos Homepage: https://trilinos.github.io
- CDash Results: https://my.cdash.org/index.php?project=Trilinos

## Related Projects

- [Trilinos](https://github.com/trilinos/Trilinos) - Main Trilinos repository
- [Spack](https://github.com/spack/spack) - Package manager for supercomputers
