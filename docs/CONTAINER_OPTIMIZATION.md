# Container Build Optimizations

This document explains the container build optimizations implemented for the Trilinos Spack Packages nightly testing workflow.

## Problem Statement

The original container build had several inefficiencies:

1. **Fixed dependency versions** in Dockerfile - Required manual updates when Kokkos or other deps changed
2. **No build cache** - All packages compiled from source (30-60 min for heavy deps)
3. **Sequential installs** - Dependencies installed one-by-one instead of in parallel
4. **Poor cache invalidation** - Any code change triggered full dependency rebuild
5. **No change detection** - Couldn't detect when dependencies actually changed

## Solution Overview

### 1. Dynamic Dependency Extraction

**File:** `extract_dependencies.py`

**Purpose:** Automatically extracts dependency versions from `trilinos_base_class/package.py`

**How it works:**
```python
# Parses version variables like:
kokkos_version="5.0.2"

# Generates:
dependencies.txt  - List of spack specs for installation
dependencies.lock - JSON with versions and hash for cache invalidation
```

**Benefits:**
- Dependencies stay in sync with source code
- Automatic cache invalidation when versions change
- No manual Dockerfile updates needed

### 2. Optimized Dockerfile

**File:** `Dockerfile.optimized`

**Key improvements:**

#### a) Spack Build Cache
```dockerfile
RUN spack mirror add binary_mirror https://binaries.spack.io/develop && \
    spack buildcache keys --install --trust
```
- Downloads pre-compiled binaries when available
- Reduces 30-60 min builds to 5-10 min for common packages

#### b) Separate Dependency Layer
```dockerfile
FROM python-deps AS deps-cache
COPY extract_dependencies.py /opt/
RUN python3 /opt/extract_dependencies.py && \
    spack install -y $(cat independent_deps)
```
- Heavy dependencies in isolated layer
- Only rebuilds when `dependencies.lock` hash changes
- Layer reused across builds

#### c) Parallel Installation
```bash
# OLD (sequential):
spack install -y kokkos && \
spack install -y openblas && \
spack install -y boost

# NEW (parallel):
spack install -y kokkos openblas boost
```
- Independent packages install concurrently
- 30-50% faster for multi-package installs

### 3. Smart Build Script

**File:** `docker-build-optimized.sh`

**Intelligence:**

#### Dependency Change Detection
```bash
# Extract current dependencies
python3 extract_dependencies.py .
CURRENT_HASH=$(cat dependencies.lock | grep hash | cut -d'"' -f4)

# Compare with previous build
if [ "$CURRENT_HASH" != "$PREVIOUS_HASH" ]; then
    echo "Dependencies changed - rebuilding deps-cache"
    INVALIDATE_CACHE=true
fi
```

#### Selective Cache Invalidation
- **Unchanged deps:** Use cached deps-cache layer (~5 min build)
- **Changed deps:** Rebuild only deps-cache and later stages (~25 min)
- **Full rebuild:** `USE_CACHE=false` rebuilds everything (~35 min)

#### Build Time Tracking
- Reports build duration
- Saves dependency hash for next build
- Provides clear feedback on what's cached vs rebuilt

## Performance Improvements

### Expected Speedups

| Scenario | Original | Optimized | Speedup |
|----------|----------|-----------|---------|
| **Cold build** (no cache) | 35-45 min | 20-30 min | 1.4-1.7x |
| **Warm build** (deps cached) | 8-12 min | 3-5 min | 2.5-3x |
| **Code-only change** | 8-12 min | 2-3 min | 3-4x |
| **Dependency change** | 35-45 min | 20-25 min | 1.5-1.8x |

*Note: Times vary based on network speed, CPU cores, and Spack cache availability*

### Build Cache Benefits

With Spack build cache enabled:
- **Kokkos**: 15-30 min → 2-5 min (binary download)
- **Boost**: 10-20 min → 2-4 min (binary download)
- **OpenMPI**: 5-15 min → 1-3 min (binary download)

Some packages may still compile from source if:
- Specific version not in cache
- Custom build flags required
- Architecture mismatch

## Usage

### Basic Build
```bash
# Use optimized build (auto-detects dependency changes)
./docker-build-optimized.sh

# Results:
# ✓ Extracts dependencies from source
# ✓ Compares with previous build
# ✓ Rebuilds only what changed
```

### Force Rebuild
```bash
# Force dependency layer rebuild
FORCE_DEPS_REBUILD=true ./docker-build-optimized.sh

# Force complete rebuild (no cache)
USE_CACHE=false ./docker-build-optimized.sh
```

### Check Dependency Status
```bash
# Extract and display current dependencies
python3 extract_dependencies.py .

# Output shows:
# - Dependency versions
# - Cache hash
# - Independent vs dependent packages
```

### Benchmark Performance
```bash
# Run benchmark suite
./benchmark-builds.sh

# Options:
# 1. Quick comparison (cached builds)
# 2. Full comparison (cold + warm builds)
# 3. Dependency change simulation
# 4. Complete benchmark (hours)
```

## Integration with Nightly Testing

The `nightly-real-install.sh` script should be updated to use the optimized build:

```bash
# OLD:
if ! docker image inspect trilinos-spack-packages:latest &> /dev/null; then
    ./docker-build.sh with-deps
fi

# NEW:
./docker-build-optimized.sh
# Automatically handles dependency changes and caching
```

Benefits for nightly runs:
- Faster builds when dependencies unchanged (~5 min vs 35 min)
- Automatic rebuild when Kokkos/deps update
- No manual version updates needed
- Transparent caching with clear feedback

## Architecture

### Layer Structure

```
┌─────────────────────────────────┐
│  base                           │ ← System packages (yum)
│  (~500 MB, rarely changes)      │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  spack-base                     │ ← Spack + core tools
│  (~2 GB, rarely changes)        │ ← + Build cache config
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  python-deps                    │ ← pytest, pytest-xdist
│  (~2.2 GB, rarely changes)      │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  deps-cache ★                   │ ← Kokkos, Boost, OpenMPI
│  (~4 GB, rebuilds on version Δ) │ ← Hash-based invalidation
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  app                            │ ← Application code
│  (~4.1 GB, rebuilds on code Δ)  │ ← Fast layer (no compiling)
└─────────────────────────────────┘
```

★ **Key optimization:** deps-cache layer only rebuilds when `dependencies.lock` hash changes

### Dependency Hash Calculation

```python
lock_data = {
    'versions': {'kokkos': '5.0.2', 'openmpi': '4.1.6'},
    'independent': ['kokkos@5.0.2', 'openmpi@4.1.6', 'openblas', 'boost'],
    'dependent': ['kokkos-kernels']
}
hash = sha256(json.dumps(lock_data, sort_keys=True))
# Result: a7cedac2afea... (first 12 chars used for display)
```

Changes in any of these trigger deps-cache rebuild:
- Dependency versions
- Package list
- Installation order

## Troubleshooting

### Dependency extraction fails
```bash
# Check if base package exists
ls -la spack_repo/trilinos/packages/trilinos_base_class/package.py

# Test extraction manually
python3 extract_dependencies.py .
cat dependencies.txt
cat dependencies.lock
```

### Cache not being used
```bash
# Check for cache file
ls -la .docker-deps-cache

# View saved hash
cat .docker-deps-cache

# Compare with current
python3 extract_dependencies.py . && \
cat dependencies.lock | grep hash
```

### Build cache not working
```bash
# Test spack cache connection
docker run --rm trilinos-spack-packages:spack-base \
    bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
             spack mirror list"

# Should show: binary_mirror https://binaries.spack.io/develop
```

### Force clean build
```bash
# Remove all images
docker rmi -f $(docker images -q trilinos-spack-packages)

# Remove dependency cache
rm -f .docker-deps-cache

# Rebuild from scratch
USE_CACHE=false ./docker-build-optimized.sh
```

## Future Enhancements

### Potential Improvements

1. **Multi-stage parallel builds**
   - Build independent stages concurrently
   - Requires BuildKit and docker buildx

2. **Remote build cache**
   - Push deps-cache to registry
   - Share across CI runners
   - Requires container registry setup

3. **Dependency DAG optimization**
   - Analyze full dependency tree
   - Optimal parallel installation order
   - More complex extraction logic

4. **Layer size optimization**
   - Aggressive `spack clean`
   - Remove build artifacts
   - Multi-stage file copying

5. **Version constraints**
   - Extract version ranges (not just pinned)
   - More flexible caching strategy
   - Requires spack.yaml approach

## Migration Guide

### For Existing Workflows

**Option 1: Side-by-side** (recommended)
```bash
# Keep original scripts
# Add optimized versions
# Compare performance
# Switch when confident
```

**Option 2: Direct replacement**
```bash
# Backup original
cp Dockerfile Dockerfile.original
cp docker-build.sh docker-build.sh.original

# Replace
mv Dockerfile.optimized Dockerfile
mv docker-build-optimized.sh docker-build.sh

# Test
./docker-build.sh
./docker-run.sh quick
```

### For CI/CD Integration

```yaml
# .github/workflows/nightly.yml example
- name: Extract dependencies
  run: python3 extract_dependencies.py .

- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /var/lib/docker
    key: docker-${{ hashFiles('dependencies.lock') }}

- name: Build container
  run: ./docker-build-optimized.sh
```

## Maintenance

### When to Update

**Trigger dependency extraction:**
- Before each nightly build (automatic in script)
- After merging base class changes
- When updating Trilinos version

**Force dependency rebuild:**
- When Spack cache is stale
- After major Spack version update
- If builds consistently fail

**Full rebuild (no cache):**
- After base system updates (RHEL, Python)
- Debugging caching issues
- Monthly maintenance (optional)

### Monitoring

Track these metrics:
- Build time per stage
- Cache hit rate for deps-cache
- Dependency change frequency
- Binary cache download vs compile ratio

```bash
# Log build metrics
./docker-build-optimized.sh 2>&1 | tee build.log

# Extract timing
grep "completed in" build.log

# Check cache usage
grep "Using cached" build.log
```

## References

- Spack build cache: https://spack.readthedocs.io/en/latest/binary_caches.html
- Docker layer caching: https://docs.docker.com/build/cache/
- Multi-stage builds: https://docs.docker.com/build/building/multi-stage/
