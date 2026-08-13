# Trilinos Spack Install Times - What Takes Long?

## TL;DR - The Slowest Builds

The packages that take the longest to build in spack (in order):

### 1. **Kokkos** (~10-30 minutes)
- C++ performance portability library
- Required by 16+ Trilinos packages
- Compiles templated code for multiple backends
- **This is the #1 bottleneck** - first test that needs it will take longest

### 2. **Kokkos-Kernels** (~5-15 minutes)
- Math kernels built on Kokkos
- Required by 13 packages
- Depends on Kokkos (so adds to build time)

### 3. **MPI (OpenMPI)** (~5-20 minutes)
- Message Passing Interface implementation
- Required when `+mpi` variant is enabled (default)
- Version pinned to 4.1.6 in base class

### 4. **BLAS/LAPACK** (~5-15 minutes)
- Linear algebra libraries
- Required by most Trilinos packages
- Usually OpenBLAS on Linux

### 5. **Boost** (~10-30 minutes)
- Large C++ library collection
- Required by many packages when `+boost` variant is enabled
- Very template-heavy = slow compilation

### 6. **Trilinos Core Packages** (~5-10 minutes each)
- **Teuchos** - Used by 15 packages (utility classes)
- **Tpetra** - Used by 15 packages (parallel linear algebra)
- These build faster than external deps but still take time

## Dependency Chain Analysis

Most common dependencies (number of packages that depend on them):

```
Kokkos:               16 packages → Build once, used everywhere
Kokkos-Kernels:       13 packages → Depends on Kokkos
Trilinos-Tpetra:      15 packages → Core parallel linear algebra
Trilinos-Teuchos:     15 packages → Core utilities
Trilinos-Belos:        9 packages → Iterative solvers
Boost:                 6 packages (when +boost)
MPI:                   8 packages (when +mpi)
BLAS/LAPACK:          ~45 packages → Almost everything
```

## Why First Tests Take Longest

When you run install tests in order:

**First test (e.g., `trilinos-adelus`):**
```
Build: OpenMPI + BLAS + LAPACK + Kokkos + Kokkos-Kernels + Teuchos + ... + adelus
Time: ~30-60 minutes
```

**Second test (e.g., `trilinos-amesos2`):**
```
Build: (reuses OpenMPI, BLAS, Kokkos, etc.) + amesos2-specific deps
Time: ~5-10 minutes (much faster!)
```

**Later tests:**
```
Build: (reuses almost everything) + package-specific code
Time: ~2-5 minutes (very fast!)
```

## Optimization Strategies

### 1. **Use `--fake` for validation** (current approach)
```bash
# Validates package specs without building
spack install --fake trilinos-teuchos
Time: < 5 seconds ✅
```

### 2. **Pre-build common dependencies**
```bash
# Build the slow stuff once
spack install kokkos@5.1.1
spack install kokkos-kernels
spack install openmpi@4.1.6
spack install openblas

# Then run install tests - they'll reuse these
Time saved: ~30-45 minutes on first test
```

### 3. **Use spack buildcache**
```bash
# Download pre-built binaries instead of compiling
spack buildcache list
spack install --use-buildcache trilinos-teuchos
Time: ~1-2 minutes (download time) ✅
```

### 4. **Test in order of increasing dependencies**

Best order to minimize total test time:

1. **Teuchos** (minimal deps: BLAS, LAPACK, Kokkos, Boost, MPI)
2. **Base packages** (depend on Teuchos)
3. **Mid-level packages** (depend on Tpetra, Belos)
4. **High-level packages** (depend on many others)

### 5. **Parallel testing with shared cache**

Since later tests reuse builds from earlier tests:
```bash
# DON'T parallelize install tests - they benefit from sequential execution
# First test builds the deps, rest reuse them

# Good: Sequential (later tests are fast)
for pkg in adelus amesos2 anasazi; do
  spack install trilinos-$pkg
done

# Bad: Parallel (each builds deps independently)
parallel spack install ::: adelus amesos2 anasazi
```

## Build Time Estimates

With **cold cache** (nothing pre-installed):

| Package Type | First Time | Subsequent |
|-------------|------------|------------|
| Minimal deps (Teuchos) | 30-45 min | 5-10 min |
| Medium deps (Tpetra) | 40-60 min | 10-15 min |
| Heavy deps (Panzer) | 60-90 min | 15-20 min |

With **warm cache** (common deps installed):
- Most packages: 5-10 minutes
- Complex packages: 10-20 minutes

With **`--fake` flag** (current approach):
- All packages: < 5 seconds ✅

## Real-World Timing for Full Test Suite

Assuming 49 packages with install tests:

**Sequential with cold cache:**
- First package: ~45 min (builds all deps)
- Next 48 packages: ~10 min each (reuse deps)
- **Total: ~8-9 hours**

**Sequential with warm cache (deps pre-built):**
- All 49 packages: ~10 min each
- **Total: ~8 hours**

**With --fake flag (current):**
- All 49 packages: ~5 sec each
- **Total: ~4 minutes** ✅

## Recommendation

**For CI/CD and quick validation:**
- Keep `--fake` flag (current approach)
- Validates package specs without actual compilation
- Catches dependency errors, missing variants, etc.
- Run time: ~5 minutes for full suite

**For actual installation testing:**
- Pre-build common dependencies in a separate step
- Run install tests sequentially (reuse builds)
- Consider using spack buildcache for external deps
- Limit to a subset of packages (not all 49)

**For nightly/weekly testing:**
- Build full suite with real installs
- Use spack buildcache to share binaries across runs
- Run on dedicated build server with lots of cores
- Archive build cache for reuse
