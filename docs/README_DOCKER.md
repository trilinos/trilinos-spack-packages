# Container Testing Guide (Podman/Docker)

This guide covers running tests in containers (Podman or Docker) with maximum pre-built optimization.

**Note:** All scripts automatically detect and use either Podman or Docker.

## Quick Start

```bash
# 1. Build the image (one-time, ~15-20 minutes)
./docker-build.sh

# 2. Run tests
./docker-run.sh quick    # Fast smoke tests (~30 seconds)
./docker-run.sh fast     # All except installs (~2-3 minutes)
./docker-run.sh full     # Complete suite (~30+ minutes)
```

## Podman vs Docker

The scripts automatically detect which container runtime you have:
- **Podman** (recommended for rootless operation)
- **Docker** (traditional container runtime)

All commands work identically with both. If you have Podman, simply run the scripts - they'll use `podman` automatically.

## Using Make (Simplest)

```bash
make build        # Build once
make test-quick   # Run quick tests
make test-fast    # Run fast tests
make test-full    # Run full suite
make shell        # Interactive debugging
```

## Build Strategy

The Dockerfile uses **multi-stage builds** to maximize caching:

### Build Stages (Cached Separately)

1. **base** - OS and system packages (~2 min)
2. **spack-base** - Spack setup + core deps (~10-15 min) ⚠️ SLOWEST
3. **python-deps** - Python packages (~1 min)
4. **app** - Application code (~30 sec)
5. **test** - Optional validation stage

### Cache Benefits

- **First build**: ~15-20 minutes
- **Code changes only**: ~30 seconds (stages 1-3 cached)
- **requirements.txt changes**: ~1 minute (stages 1-2 cached)
- **System dependency changes**: Full rebuild

### Layer Caching Optimization

```bash
# Maximum cache reuse (default)
./docker-build.sh

# Force fresh build
USE_CACHE=false ./docker-build.sh

# Build to specific stage
./docker-build.sh spack-base  # Stop at spack setup
./docker-build.sh app         # Full app (default)
./docker-build.sh test        # Include test validation
```

## Running Tests

### Method 1: Simple Scripts (Recommended)

```bash
# Quick smoke tests (30 sec)
./docker-run.sh quick

# All except installs (2-3 min)
./docker-run.sh fast

# Full suite with installs (30+ min)
./docker-run.sh full

# Interactive shell for debugging
./docker-run.sh shell

# Pass extra pytest args
./docker-run.sh fast -k test_spack_info
./docker-run.sh quick --maxfail=1 -v
```

### Method 2: Compose (Advanced)

**Note:** Requires `podman-compose` or `docker-compose` to be installed separately.

```bash
# Install podman-compose (if using Podman)
pip3 install podman-compose

# Run specific service
podman-compose up test-quick
podman-compose up test-fast
podman-compose up test-full

# Interactive shell
podman-compose run shell

# View logs
podman-compose logs test-quick
```

### Method 3: Direct Container Commands

```bash
# Quick tests (use podman or docker)
podman run --rm trilinos-spack-packages:latest \
    pytest test/ -m quick -n auto -v

# Custom command
podman run --rm -it trilinos-spack-packages:latest \
    /bin/bash

# Mount local code for development
podman run --rm -v $(pwd)/test:/opt/trilinos-spack-packages/test \
    trilinos-spack-packages:latest \
    pytest test/ -m quick -v
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: ./docker-build.sh
      
      - name: Run quick tests
        run: ./docker-run.sh quick
      
      - name: Run fast tests
        run: ./docker-run.sh fast
```

### GitLab CI Example

```yaml
stages:
  - build
  - test

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
  
test:quick:
  stage: test
  script:
    - docker run --rm $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA pytest test/ -m quick -n auto

test:fast:
  stage: test
  script:
    - docker run --rm $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA pytest test/ -m "not slow" -n auto
```

## Advanced Usage

### Caching Spack Builds

For faster repeated installs, use a volume for spack cache:

```bash
podman run --rm \
    -v spack-cache:/opt/spack-src/var/spack \
    trilinos-spack-packages:latest \
    pytest test/long-test.py -m install -n auto
```

### Development Workflow

```bash
# 1. Build once
make build

# 2. Edit code locally

# 3. Run tests with live code mount
podman run --rm \
    -v $(pwd)/test:/opt/trilinos-spack-packages/test:ro \
    trilinos-spack-packages:latest \
    pytest test/ -m quick -v

# Or use shell for iteration
make shell
# Inside container:
pytest test/ -m quick -v
# Edit code outside, rerun tests inside
```

### Debugging Failed Tests

```bash
# Open shell in container
./docker-run.sh shell

# Inside container, run tests manually:
pytest test/quick-test.py::test_spack_info -v -s
pytest test/ -m quick --pdb  # Drop into debugger on failure
```

## Performance Comparison

| Method | First Build | Code Change | Dep Change |
|--------|-------------|-------------|------------|
| No cache | 15-20 min | 15-20 min | 15-20 min |
| **With cache** | **15-20 min** | **~30 sec** | **~1 min** |

| Test Suite | Runtime (parallel) |
|------------|-------------------|
| Quick only | ~30 seconds |
| Fast (no installs) | ~2-3 minutes |
| Full (with installs) | ~30+ minutes |

## Troubleshooting

### Image not found
```bash
./docker-build.sh  # Rebuild image
```

### Out of space
```bash
# Podman
podman system prune -a    # Clean everything
make clean                # Remove project images

# Docker
docker system prune -a    # Clean everything
```

### Cache issues
```bash
USE_CACHE=false ./docker-build.sh  # Force rebuild
```

### SELinux issues (Podman on RHEL/CentOS)
If you get permission errors with mounted volumes:
```bash
# Add :z or :Z flag to volumes
podman run --rm -v $(pwd)/test:/opt/trilinos-spack-packages/test:z \
    trilinos-spack-packages:latest pytest test/
```

### Permission errors
```bash
chmod +x docker-build.sh docker-run.sh
```

## Files Created

- `Dockerfile` - Multi-stage build with optimal caching
- `docker-compose.yml` - Service orchestration
- `.dockerignore` - Build context optimization
- `docker-build.sh` - Build helper script
- `docker-run.sh` - Test runner script
- `Makefile` - Convenience targets
