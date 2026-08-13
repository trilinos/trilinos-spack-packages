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
    echo -e "  ./docker-build.sh"
    exit 1
fi

# Create a temporary build directory in the container and run CTest
echo -e "${GREEN}Configuring CMake and running CTest...${NC}"
$CONTAINER_CMD run --rm \
    -e DASHBOARD_TYPE="${DASHBOARD_TYPE}" \
    -e CTEST_TEST_FILTER="${TEST_FILTER}" \
    trilinos-spack-packages:latest \
    bash -c "
        # Configure curl to skip SSL verification
        echo 'insecure' > ~/.curlrc && \
        source /opt/spack-src/share/spack/setup-env.sh && \
        spack load python cmake && \
        cd /opt/trilinos-spack-packages && \
        rm -rf build && \
        mkdir -p build && \
        ctest -S CTestScript.cmake -V
    "

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}CDash Submission Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}View results at: https://my.cdash.org/index.php?project=Trilinos${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}CDash Submission Failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit $EXIT_CODE
fi
