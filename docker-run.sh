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

# Default to quick tests
TEST_TYPE="${1:-quick}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Trilinos Tests in Container${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to run tests
run_tests() {
    local test_type=$1
    local extra_args="${@:2}"

    echo -e "${BLUE}Test type: ${test_type}${NC}"
    echo -e "${BLUE}Extra args: ${extra_args}${NC}"
    echo ""

    case $test_type in
        quick|q)
            echo -e "${GREEN}Running quick smoke tests (fastest)...${NC}"
            $CONTAINER_CMD run --rm \
                trilinos-spack-packages:latest \
                pytest test/ -m quick -n auto -v $extra_args
            ;;
        fast|f)
            echo -e "${GREEN}Running fast tests (all except install - includes spec validation)...${NC}"
            $CONTAINER_CMD run --rm \
                trilinos-spack-packages:latest \
                pytest test/ -m "not install" -n auto -v $extra_args
            ;;
        full|all|nightly)
            echo -e "${YELLOW}Running full test suite (all tests including real installs - takes 8-9 hours)...${NC}"
            $CONTAINER_CMD run --rm \
                -v spack-cache:/opt/spack-src/var/spack \
                trilinos-spack-packages:latest \
                ./regenerate-package-files.sh $extra_args
            ;;
        shell|sh|bash)
            echo -e "${GREEN}Starting interactive shell...${NC}"
            $CONTAINER_CMD run --rm -it \
                -v "$(pwd)":/opt/trilinos-spack-packages \
                trilinos-spack-packages:latest \
                /bin/bash
            ;;
        *)
            echo -e "${RED}Unknown test type: $test_type${NC}"
            echo ""
            echo "Usage: $0 [TEST_TYPE] [EXTRA_PYTEST_ARGS]"
            echo ""
            echo "Test types:"
            echo "  quick, q         - Quick smoke tests (default)"
            echo "  fast, f          - All tests except install (includes spec validation)"
            echo "  full, all, nightly - Full suite including real installs (8-9 hours)"
            echo "  shell, sh        - Interactive shell"
            echo ""
            echo "Examples:"
            echo "  $0 quick                    # Run quick tests"
            echo "  $0 fast -k test_spack_info  # Run specific test"
            echo "  $0 full --maxfail=1         # Stop on first failure"
            echo "  $0 shell                    # Interactive debugging"
            exit 1
            ;;
    esac
}

# Check if image exists
if ! $CONTAINER_CMD image inspect trilinos-spack-packages:latest &> /dev/null; then
    echo -e "${RED}Error: Container image not found${NC}"
    echo -e "${YELLOW}Please build the image first:${NC}"
    echo -e "  ./docker-build.sh"
    exit 1
fi

# Run tests
run_tests "$@"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tests Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
