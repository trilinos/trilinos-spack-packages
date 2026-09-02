#!/bin/bash
set -e

# Nightly script for REAL compilation testing (OPTIMIZED)
# Uses intelligent caching to speed up builds when dependencies unchanged

# Configuration
REPO_DIR="$HOME/trilinos-spack-packages"
LOG_DIR="$HOME/nightly-test-logs"
DATE=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/nightly-real-install-$DATE.log"

# Detect container runtime (podman or docker)
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo "Error: Neither podman nor docker found"
    exit 1
fi

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Nightly Real Install Test Started (OPTIMIZED) ==="
log "Repository: $REPO_DIR"
log "Log file: $LOG_FILE"

# Navigate to repository
cd "$REPO_DIR" || exit 1

# Pull latest changes
log "Pulling latest changes from git..."

# Clean up generated dependency files before pull (they'll be regenerated after)
log "Resetting generated dependency files to avoid merge conflicts..."
git checkout -- dependencies.txt dependencies.lock 2>/dev/null || true

export GIT_TERMINAL_PROMPT=0  # Prevent credential prompts in cron
timeout 900 git fetch origin --progress 2>&1 | tee -a "$LOG_FILE" || { log "ERROR: git fetch timed out or failed"; exit 1; }
BEFORE_PULL=$(git rev-parse HEAD)
timeout 900 git pull origin main --progress 2>&1 | tee -a "$LOG_FILE" || { log "ERROR: git pull timed out or failed"; exit 1; }
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

# Check if source files changed
if [ "$COMMITS_CHANGED" = "true" ]; then
    if git diff --name-only $BEFORE_PULL $AFTER_PULL | grep -qE "^(Dockerfile|docker-build|extract_dependencies.py|requirements.txt|setup-spack.sh|generate_spack_packages.py|parse_tribits_xml.py|spack_repo/|xml_files/.*\.xml|.*trilinos_base_class/package.py)"; then
        log "Source files changed in commits"
        REBUILD_REASON="source_files_changed"
    fi
fi

# Check if container exists
if ! $CONTAINER_CMD image inspect trilinos-spack-packages:latest &> /dev/null; then
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
        log "Using standard build (no optimization)..."
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

# Run ALL tests (including real install tests) and submit to CDash
log "Running FULL test suite (takes 8-9 hours)..."
log "Test includes:"
log "  - Quick smoke tests (~1 min)"
log "  - Spec concretization tests (~5-30 min)"
log "  - Real package compilation and installation (~8 hours)"
log "  - CDash submission"

TEST_START=$(date +%s)

# Nightly runs ALL tests (quick + spec + install)
./docker-cdash.sh Nightly >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

TEST_END=$(date +%s)
TEST_DURATION=$((TEST_END - TEST_START))
TEST_HOURS=$((TEST_DURATION / 3600))
TEST_MINUTES=$(((TEST_DURATION % 3600) / 60))

# Calculate total runtime
TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - $(date -d "$(head -1 "$LOG_FILE" | cut -d']' -f1 | tr -d '[')" +%s)))
TOTAL_HOURS=$((TOTAL_DURATION / 3600))
TOTAL_MINUTES=$(((TOTAL_DURATION % 3600) / 60))

if [ $EXIT_CODE -eq 0 ]; then
    log "=== Nightly Real Install Test SUCCEEDED ==="
else
    log "=== Nightly Real Install Test FAILED (exit code: $EXIT_CODE) ==="
fi

log "Test runtime: ${TEST_HOURS}h ${TEST_MINUTES}m"
log "Total runtime: ${TOTAL_HOURS}h ${TOTAL_MINUTES}m"

# Optimization summary
if [ "$REBUILD_REASON" = "none" ]; then
    log "Optimization: Skipped container rebuild (saved ~30-60 min)"
elif [ "$REBUILD_REASON" = "dependencies_changed" ]; then
    log "Optimization: Smart dependency cache (rebuilt only changed deps)"
fi

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "nightly-real-install-*.log" -mtime +30 -delete

# Generate summary report
cat >> "$LOG_FILE" << EOF

========================================
NIGHTLY TEST SUMMARY
========================================
Date: $(date)
Commit: $AFTER_PULL
Dependencies: $CURRENT_DEPS_HASH
Rebuild: $REBUILD_REASON
Test Result: $([ $EXIT_CODE -eq 0 ] && echo "PASSED" || echo "FAILED")
Test Time: ${TEST_HOURS}h ${TEST_MINUTES}m
Total Time: ${TOTAL_HOURS}h ${TOTAL_MINUTES}m
CDash: https://my.cdash.org/index.php?project=Trilinos
Log: $LOG_FILE
========================================
EOF

log "View results: https://my.cdash.org/index.php?project=Trilinos"
log "Tests compiled and installed real Trilinos packages"

# Optional: Send email notification
if [ $EXIT_CODE -ne 0 ]; then
    SUBJECT="Trilinos Nightly Test FAILED"
    BODY="Real install test failed after ${TEST_HOURS}h ${TEST_MINUTES}m

Commit: $AFTER_PULL
Dependencies: $CURRENT_DEPS_HASH
Rebuild reason: $REBUILD_REASON

Check log: $LOG_FILE
View CDash: https://my.cdash.org/index.php?project=Trilinos"

    echo "$BODY" | mail -s "$SUBJECT" your-email@example.com 2>/dev/null || true
fi

# Exit with test result
exit $EXIT_CODE
