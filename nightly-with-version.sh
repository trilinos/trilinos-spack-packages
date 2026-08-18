#!/bin/bash
set -e

# Nightly script with Trilinos version support
# Usage: ./nightly-with-version.sh [TRILINOS_VERSION]
# Example: ./nightly-with-version.sh develop

# Configuration
REPO_DIR="$HOME/trilinos-spack-packages"
LOG_DIR="$HOME/nightly-test-logs"
DATE=$(date +%Y%m%d-%H%M%S)

# Get Trilinos version from argument, default to "develop"
TRILINOS_VERSION="${1:-develop}"
LOG_FILE="$LOG_DIR/nightly-${TRILINOS_VERSION}-$DATE.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Nightly Test Started (OPTIMIZED) ==="
log "Trilinos Version: $TRILINOS_VERSION"
log "Repository: $REPO_DIR"
log "Log file: $LOG_FILE"

# Navigate to repository
cd "$REPO_DIR" || exit 1

# Pull latest changes
log "Pulling latest changes from git..."
git fetch origin
BEFORE_PULL=$(git rev-parse HEAD)
git pull origin main
AFTER_PULL=$(git rev-parse HEAD)

if [ "$BEFORE_PULL" != "$AFTER_PULL" ]; then
    log "New commits detected: $BEFORE_PULL -> $AFTER_PULL"
    COMMITS_CHANGED=true
else
    log "No new commits"
    COMMITS_CHANGED=false
fi

# Extract current dependencies
log "Extracting dependency versions..."
if [ -f "extract_dependencies.py" ]; then
    python3 extract_dependencies.py . >> "$LOG_FILE" 2>&1
    CURRENT_DEPS_HASH=$(cat dependencies.lock | grep -o '"hash": "[^"]*"' | cut -d'"' -f4 | cut -c1-12)
    log "Current dependency hash: $CURRENT_DEPS_HASH"
else
    log "WARNING: extract_dependencies.py not found, using standard build"
    CURRENT_DEPS_HASH="unknown"
fi

# Check what changed
REBUILD_REASON="none"
PREVIOUS_DEPS_FILE=".docker-deps-cache"

# Check if dependencies changed
if [ -f "$PREVIOUS_DEPS_FILE" ]; then
    PREVIOUS_DEPS_HASH=$(cat "$PREVIOUS_DEPS_FILE")
    if [ "$CURRENT_DEPS_HASH" != "$PREVIOUS_DEPS_HASH" ]; then
        log "Dependencies changed: $PREVIOUS_DEPS_HASH -> $CURRENT_DEPS_HASH"
        REBUILD_REASON="dependencies_changed"
    fi
fi

# Check if Dockerfile changed
if [ "$COMMITS_CHANGED" = "true" ]; then
    if git diff --name-only $BEFORE_PULL $AFTER_PULL | grep -q "Dockerfile\|docker-build\|extract_dependencies.py\|requirements.txt"; then
        log "Build infrastructure changed in commits"
        REBUILD_REASON="build_infra_changed"
    fi
fi

# Check if container exists
if ! docker image inspect trilinos-spack-packages:latest &> /dev/null; then
    log "Container image not found"
    REBUILD_REASON="image_missing"
fi

# Decide whether to rebuild
if [ "$REBUILD_REASON" != "none" ]; then
    log "Container rebuild required: $REBUILD_REASON"

    # Use optimized build script if available
    if [ -f "./docker-build-optimized.sh" ]; then
        log "Using optimized build (smart caching enabled)..."
        BUILD_START=$(date +%s)
        ./docker-build-optimized.sh >> "$LOG_FILE" 2>&1
        BUILD_END=$(date +%s)
        BUILD_DURATION=$((BUILD_END - BUILD_START))
        BUILD_MINUTES=$((BUILD_DURATION / 60))
        log "Container built in ${BUILD_MINUTES}m (optimized)"
    else
        log "Using standard build..."
        BUILD_START=$(date +%s)
        ./docker-build.sh >> "$LOG_FILE" 2>&1
        BUILD_END=$(date +%s)
        BUILD_DURATION=$((BUILD_END - BUILD_START))
        BUILD_MINUTES=$((BUILD_DURATION / 60))
        log "Container built in ${BUILD_MINUTES}m (standard)"
    fi
else
    log "Container is up-to-date, skipping rebuild"
    log "  - No new commits with build changes"
    log "  - Dependencies unchanged: $CURRENT_DEPS_HASH"
    log "  - Image exists and ready"
fi

# Run ALL tests (including real install tests)
log "Running FULL test suite for Trilinos $TRILINOS_VERSION (takes 6-10 hours)..."
log "Test includes:"
log "  - Quick smoke tests (~1 min)"
log "  - Spec concretization tests (~5-30 min)"
log "  - Real package compilation and installation (~6-10 hours)"
log "  - CDash submission"

TEST_START=$(date +%s)

# Run with version support
if [ -f "./docker-run-with-version.sh" ]; then
    log "Using version-aware test runner..."
    ./docker-run-with-version.sh full $TRILINOS_VERSION >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
else
    log "Using standard test runner (no version specification)..."
    docker run --rm \
        -e TRILINOS_VERSION=$TRILINOS_VERSION \
        -v spack-cache:/opt/spack-src/var/spack \
        trilinos-spack-packages:latest \
        pytest test/ -n auto -v >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
fi

TEST_END=$(date +%s)
TEST_DURATION=$((TEST_END - TEST_START))
TEST_HOURS=$((TEST_DURATION / 3600))
TEST_MINUTES=$(((TEST_DURATION % 3600) / 60))

# Calculate total runtime
TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - $(date -d "$(head -1 "$LOG_FILE" | cut -d']' -f1 | tr -d '[')" +%s 2>/dev/null || echo $TEST_START)))
TOTAL_HOURS=$((TOTAL_DURATION / 3600))
TOTAL_MINUTES=$(((TOTAL_DURATION % 3600) / 60))

if [ $EXIT_CODE -eq 0 ]; then
    log "=== Nightly Test SUCCEEDED ==="
else
    log "=== Nightly Test FAILED (exit code: $EXIT_CODE) ==="
fi

log "Trilinos Version: $TRILINOS_VERSION"
log "Test runtime: ${TEST_HOURS}h ${TEST_MINUTES}m"
log "Total runtime: ${TOTAL_HOURS}h ${TOTAL_MINUTES}m"

# Optimization summary
if [ "$REBUILD_REASON" = "none" ]; then
    log "Optimization: Skipped container rebuild (saved ~30-60 min)"
elif [ "$REBUILD_REASON" = "dependencies_changed" ]; then
    log "Optimization: Smart dependency cache (rebuilt only changed deps)"
fi

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "nightly-*.log" -mtime +30 -delete

# Generate summary report
cat >> "$LOG_FILE" << EOF

========================================
NIGHTLY TEST SUMMARY
========================================
Date: $(date)
Trilinos Version: $TRILINOS_VERSION
Commit: $AFTER_PULL
Dependencies: $CURRENT_DEPS_HASH
Rebuild: $REBUILD_REASON
Test Result: $([ $EXIT_CODE -eq 0 ] && echo "PASSED" || echo "FAILED")
Test Time: ${TEST_HOURS}h ${TEST_MINUTES}m
Total Time: ${TOTAL_HOURS}h ${TOTAL_MINUTES}m
Log: $LOG_FILE
========================================
EOF

log "Tests compiled and installed real Trilinos packages for version: $TRILINOS_VERSION"

# Optional: Send email notification
if [ $EXIT_CODE -ne 0 ]; then
    SUBJECT="Trilinos Nightly Test FAILED ($TRILINOS_VERSION)"
    BODY="Nightly test for Trilinos $TRILINOS_VERSION failed after ${TEST_HOURS}h ${TEST_MINUTES}m

Commit: $AFTER_PULL
Dependencies: $CURRENT_DEPS_HASH
Rebuild reason: $REBUILD_REASON

Check log: $LOG_FILE"

    echo "$BODY" | mail -s "$SUBJECT" your-email@example.com 2>/dev/null || true
fi

# Exit with test result
exit $EXIT_CODE
