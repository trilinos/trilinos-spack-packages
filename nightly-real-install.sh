#!/bin/bash
set -e

# Nightly script for REAL compilation testing (takes 8-9 hours)

# Configuration
REPO_DIR="$HOME/trilinos-spack-packages"
LOG_DIR="$HOME/nightly-test-logs"
DATE=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/nightly-real-install-$DATE.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Nightly Real Install Test Started ==="
log "WARNING: This will take 8-9 hours"
log "Repository: $REPO_DIR"
log "Log file: $LOG_FILE"

# Navigate to repository
cd "$REPO_DIR" || exit 1

# Pull latest changes
log "Pulling latest changes from git..."
git fetch origin
git pull origin main

# Check if we need to rebuild with-deps container
# (only if Dockerfile changed or container doesn't exist)
if ! docker image inspect trilinos-spack-packages:latest &> /dev/null; then
    log "Container not found, building with pre-built dependencies (30-60 min)..."
    ./docker-build.sh with-deps >> "$LOG_FILE" 2>&1
elif git diff --name-only HEAD@{1} | grep -q "Dockerfile\|base_package.py\|requirements.txt"; then
    log "Core files changed, rebuilding container..."
    ./docker-build.sh with-deps >> "$LOG_FILE" 2>&1
else
    log "Container exists and no core changes, skipping rebuild"
fi

# Run ALL tests (including real install tests) and submit to CDash
log "Running FULL test suite (ALL tests including installs - takes 8-9 hours)..."
START_TIME=$(date +%s)

# Nightly runs ALL tests (quick + spec + install)
./docker-cdash.sh Nightly >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HOURS=$((DURATION / 3600))
MINUTES=$(((DURATION % 3600) / 60))

if [ $EXIT_CODE -eq 0 ]; then
    log "=== Nightly Real Install Test SUCCEEDED ==="
else
    log "=== Nightly Real Install Test FAILED (exit code: $EXIT_CODE) ==="
fi

log "Total runtime: ${HOURS}h ${MINUTES}m"

# Cleanup old logs (keep last 30 days)
find "$LOG_DIR" -name "nightly-real-install-*.log" -mtime +30 -delete

# Print summary
log "View results: https://my.cdash.org/index.php?project=Trilinos"
log "Tests actually compiled and installed packages"

# Optional: Send email on failure
if [ $EXIT_CODE -ne 0 ]; then
    echo "Real install test failed after ${HOURS}h ${MINUTES}m. Check log: $LOG_FILE" | \
        mail -s "Trilinos Real Install Test FAILED" your-email@example.com 2>/dev/null || true
fi

exit $EXIT_CODE
