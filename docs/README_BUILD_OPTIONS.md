# Container Build Options

## TL;DR

**Default (Recommended):**
```bash
./docker-build.sh
```
- Fast build: ~2-3 minutes
- Small image: ~500MB
- Use `--fake` flag in tests (validates specs without compiling)
- **Perfect for CI/CD and quick validation** ✅

**With Pre-built Dependencies (Optional):**
```bash
./docker-build.sh with-deps
```
- Slow build: ~30-60 minutes ⏰
- Large image: ~5-10GB 📦
- Pre-installs: Kokkos, Boost, OpenMPI, OpenBLAS, Kokkos-Kernels
- Use when doing real installations (without `--fake`)
- **Only needed for actual compilation testing**

## Build Stages

The Dockerfile has multiple build stages:

### Stage 1: `app` (Default)
```bash
./docker-build.sh           # or
./docker-build.sh app
```

**Contains:**
- Base OS (RHEL UBI9)
- Spack package manager
- CMake, compilers, Python
- pytest, test dependencies
- Your Trilinos package definitions

**Does NOT contain:**
- Pre-built Kokkos, Boost, OpenMPI, etc.
- These get built on-demand during tests (or skipped with `--fake`)

**Use for:**
- ✅ CI/CD pipelines
- ✅ Quick validation
- ✅ Testing package specs
- ✅ Daily development

### Stage 2: `with-deps` (Optional, Expensive)
```bash
./docker-build.sh with-deps
```

**Contains everything from `app` PLUS:**
- Pre-installed Kokkos 5.1.1 (~15-30 min)
- Pre-installed Kokkos-Kernels (~10-15 min)
- Pre-installed OpenBLAS (~5-10 min)
- Pre-installed Boost (~10-30 min)
- Pre-installed OpenMPI 4.1.6 (~5-15 min)

**Build time:** ~30-60 minutes total
**Image size:** ~5-10GB (vs ~500MB for default)

**Use for:**
- ✅ Real installation testing (remove `--fake` from tests)
- ✅ Benchmarking actual build times
- ✅ Development environment with deps ready
- ❌ NOT for CI/CD (too slow/large)

## When to Use Each

### Use Default (`app` stage):

**Your current workflow (recommended):**
```bash
# Build fast, test fast
./docker-build.sh
./docker-cdash.sh Experimental 'test_spack_(version|list|find)' --no-submit
# Result: 3 seconds per package, validates specs ✅
```

**Advantages:**
- Quick iteration cycle
- Small container images
- Easy to rebuild after changes
- Validates package definitions perfectly
- Enough for 99% of testing needs

### Use With-Deps (`with-deps` stage):

**When you need real compilation:**
```bash
# Build once (30-60 min)
./docker-build.sh with-deps

# Edit test/long_test.py to remove --fake flag
# Then run real installs (much faster with pre-built deps)
./docker-cdash.sh Experimental 'test_spack_install[trilinos-teuchos]' --no-submit
# Result: 5-10 minutes instead of 30-45 minutes ✅
```

**Advantages:**
- First real install is much faster
- Tests actual compilation/linking
- Good for comprehensive testing
- Shared cache speeds up subsequent installs

**Disadvantages:**
- Initial build takes 30-60 minutes
- 10x larger image size
- Slower to iterate on code changes
- Overkill if using `--fake`

## Example Workflows

### Quick Development (Current)
```bash
# 1. Edit package definitions
vim spack_repo/trilinos/packages/trilinos_foo/package.py

# 2. Rebuild (2-3 min)
./docker-build.sh

# 3. Test quickly (seconds)
./docker-cdash.sh Experimental 'test_spack_info' --no-submit --output-on-failure

# 4. Submit to CDash when ready
./docker-cdash.sh Experimental 'test_spack_(version|list|find)'
```

### Comprehensive Testing (Occasional)
```bash
# 1. Build with deps (30-60 min, do this once)
./docker-build.sh with-deps

# 2. Remove --fake from test/long_test.py
vim test/long_test.py  # Change: install --fake → install

# 3. Rebuild (quick, just code changed)
./docker-build.sh with-deps

# 4. Test real installations (5-10 min each)
./docker-cdash.sh Experimental 'test_spack_install[trilinos-teuchos]' --no-submit
```

### CI/CD Pipeline (Recommended)
```bash
# Use default build (fast, small)
./docker-build.sh

# Run quick validation
./docker-run.sh quick

# Submit to CDash
./docker-cdash.sh Experimental

# Optional: Weekly full install test on separate schedule
# (Use with-deps stage on dedicated builder)
```

## Comparison Table

| Feature | Default (`app`) | With Deps (`with-deps`) |
|---------|----------------|------------------------|
| Build time | 2-3 min ⚡ | 30-60 min ⏰ |
| Image size | ~500MB 📦 | ~5-10GB 📦💥 |
| Rebuild after code change | 30 sec | 1-2 min |
| Test with `--fake` | Instant ✅ | Instant ✅ |
| Test real install (first) | 30-45 min | 5-10 min ✅ |
| Test real install (later) | 5-10 min | 2-5 min |
| Use case | Daily dev, CI/CD | Weekly comprehensive |

## Recommendation

**Stick with the default** unless you have a specific need for real compilation testing:

```bash
# This is perfect for your use case:
./docker-build.sh                    # Fast
./docker-cdash.sh Experimental       # Validates all packages
# Result: Complete validation in ~5 minutes ✅
```

The `--fake` flag is doing exactly what you need - validating that:
- Package specs are correct
- Dependencies are specified properly  
- Variants work correctly
- No conflicts or missing requirements

You don't need to actually compile Kokkos/Boost/etc to know your package definitions are right!

## Advanced: Custom Dependency Pre-build

If you only need specific deps, edit the Dockerfile `with-deps` stage:

```dockerfile
# Only pre-build what you need
RUN bash -c "source /opt/spack-src/share/spack/setup-env.sh && \
    spack install -y kokkos@5.1.1 && \
    spack install -y openmpi@4.1.6"
```

This saves time by not building everything.
