#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect container runtime (podman or docker)
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo -e "${RED}Error: Neither podman nor docker found${NC}"
    exit 1
fi

# Parse arguments
DASHBOARD_TYPE="${1:-Experimental}"
TEST_FILTER="${2}"
VERBOSE_ON_FAILURE=""
NO_SUBMIT=""

# Check for --output-on-failure flag
if [[ "$@" == *"--output-on-failure"* ]]; then
    VERBOSE_ON_FAILURE="--output-on-failure"
fi

# Check for --no-submit flag
if [[ "$@" == *"--no-submit"* ]]; then
    NO_SUBMIT="true"
fi

# Setup logging for Nightly runs
if [ "$DASHBOARD_TYPE" = "Nightly" ]; then
    LOG_DIR="$HOME/nightly-test-logs"
    mkdir -p "$LOG_DIR"
    DATE=$(date +%Y%m%d-%H%M%S)
    LOG_FILE="$LOG_DIR/nightly-cdash-$DATE.log"

    # Function to log with timestamp
    log() {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
    }

    log "=== Nightly CDash Test Started ==="
    log "Log file: $LOG_FILE"

    # Check and rebuild container if necessary
    log "Checking container status..."
    if ./scripts/check-and-rebuild-container.sh 2>&1 | tee -a "$LOG_FILE"; then
        log "Container ready"
    else
        log "ERROR: Container check/rebuild failed"
        exit 1
    fi
else
    # Simple echo function for non-nightly runs
    log() {
        echo "$*"
    }
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running CTest and Submitting to CDash${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}Dashboard type: ${DASHBOARD_TYPE}${NC}"
if [ -n "$TEST_FILTER" ]; then
    echo -e "${BLUE}Test filter: ${TEST_FILTER}${NC}"
fi
echo ""

# Check if image exists
if ! $CONTAINER_CMD image inspect trilinos-spack-packages:latest &> /dev/null; then
    echo -e "${RED}Error: Container image not found${NC}"
    echo -e "${YELLOW}Please build the image first:${NC}"
    echo -e "  ./docker-build-optimized.sh"
    exit 1
fi

# Create a temporary build directory in the container and run CTest
log "Configuring CMake and running CTest..."
TEST_START=$(date +%s)

if [ "$DASHBOARD_TYPE" = "Nightly" ]; then
    # Redirect output to log file for nightly runs
    $CONTAINER_CMD run --rm \
        -e DASHBOARD_TYPE="${DASHBOARD_TYPE}" \
        -e CTEST_TEST_FILTER="${TEST_FILTER}" \
        -e CTEST_NO_SUBMIT="${NO_SUBMIT}" \
        -e GIT_SSL_NO_VERIFY=1 \
        -e CURL_CA_BUNDLE=/dev/null \
        trilinos-spack-packages:latest \
        bash -c "
            # Configure curl to skip SSL verification
            echo 'insecure' > ~/.curlrc && \
            export GIT_SSL_NO_VERIFY=1 && \
            export CURL_CA_BUNDLE=/dev/null && \
            source /opt/spack-src/share/spack/setup-env.sh && \
            spack load python && \
            spack load --first cmake && \
            cd /opt/trilinos-spack-packages && \
            rm -rf build && \
            mkdir -p build && \
            cmake -DCTEST_USE_LAUNCHERS=1 && \
            ctest -S CTestScript.cmake -V --no-compress-output ${VERBOSE_ON_FAILURE}
        " 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=${PIPESTATUS[0]}
else
    # Direct output for experimental runs
    $CONTAINER_CMD run --rm \
        -e DASHBOARD_TYPE="${DASHBOARD_TYPE}" \
        -e CTEST_TEST_FILTER="${TEST_FILTER}" \
        -e CTEST_NO_SUBMIT="${NO_SUBMIT}" \
        -e GIT_SSL_NO_VERIFY=1 \
        -e CURL_CA_BUNDLE=/dev/null \
        trilinos-spack-packages:latest \
        bash -c "
            # Configure curl to skip SSL verification
            echo 'insecure' > ~/.curlrc && \
            export GIT_SSL_NO_VERIFY=1 && \
            export CURL_CA_BUNDLE=/dev/null && \
            source /opt/spack-src/share/spack/setup-env.sh && \
            spack load python && \
            spack load --first cmake && \
            cd /opt/trilinos-spack-packages && \
            rm -rf build && \
            mkdir -p build && \
            cmake -DCTEST_USE_LAUNCHERS=1 && \
            ctest -S CTestScript.cmake -V --no-compress-output ${VERBOSE_ON_FAILURE}
        "
    EXIT_CODE=$?
fi

TEST_END=$(date +%s)
TEST_DURATION=$((TEST_END - TEST_START))
TEST_HOURS=$((TEST_DURATION / 3600))
TEST_MINUTES=$(((TEST_DURATION % 3600) / 60))

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}CDash Submission Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}View results at: https://my.cdash.org/index.php?project=Trilinos${NC}"

    if [ "$DASHBOARD_TYPE" = "Nightly" ]; then
        log "=== Nightly CDash Test SUCCEEDED ==="
        log "Test runtime: ${TEST_HOURS}h ${TEST_MINUTES}m"
        log "View results: https://my.cdash.org/index.php?project=Trilinos"

        # Cleanup old logs (keep last 30 days)
        find "$LOG_DIR" -name "nightly-cdash-*.log" -mtime +30 -delete 2>/dev/null || true
    fi
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}CDash Submission Failed!${NC}"
    echo -e "${RED}========================================${NC}"

    if [ "$DASHBOARD_TYPE" = "Nightly" ]; then
        log "=== Nightly CDash Test FAILED (exit code: $EXIT_CODE) ==="
        log "Test runtime: ${TEST_HOURS}h ${TEST_MINUTES}m"
        log "Check log: $LOG_FILE"
    fi

    exit $EXIT_CODE
fi
