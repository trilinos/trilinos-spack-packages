#!/bin/bash
set -e

# Enhanced docker-run.sh with Trilinos version support

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
TEST_TYPE="${1:-quick}"
TRILINOS_VERSION="${2:-develop}"  # Default to develop branch
shift 2 2>/dev/null || shift 1 2>/dev/null || true
EXTRA_ARGS="$@"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Trilinos Tests in Container${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Trilinos Version: ${TRILINOS_VERSION}${NC}"
echo ""

# Function to run tests
run_tests() {
    local test_type=$1
    local version=$2
    local extra_args="${@:3}"

    echo -e "${BLUE}Test type: ${test_type}${NC}"
    echo -e "${BLUE}Trilinos version: ${version}${NC}"
    echo -e "${BLUE}Extra args: ${extra_args}${NC}"
    echo ""

    # Set environment variable for tests to use
    VERSION_ARG="-e TRILINOS_VERSION=${version}"

    case $test_type in
        quick|q)
            echo -e "${GREEN}Running quick smoke tests (fastest)...${NC}"
            $CONTAINER_CMD run --rm $VERSION_ARG \
                trilinos-spack-packages:latest \
                pytest test/ -m quick -n auto -v $extra_args
            ;;
        fast|f)
            echo -e "${GREEN}Running fast tests (all except install - includes spec validation)...${NC}"
            $CONTAINER_CMD run --rm $VERSION_ARG \
                trilinos-spack-packages:latest \
                pytest test/ -m "not install" -n auto -v $extra_args
            ;;
        full|all|nightly)
            echo -e "${YELLOW}Running full test suite (all tests including real installs - takes 6-10 hours)...${NC}"
            $CONTAINER_CMD run --rm $VERSION_ARG \
                -v spack-cache:/opt/spack-src/var/spack \
                trilinos-spack-packages:latest \
                pytest test/ -n auto -v $extra_args
            ;;
        shell|sh|bash)
            echo -e "${GREEN}Starting interactive shell...${NC}"
            $CONTAINER_CMD run --rm -it $VERSION_ARG \
                -v "$(pwd)":/opt/trilinos-spack-packages \
                trilinos-spack-packages:latest \
                /bin/bash
            ;;
        compose|dc)
            echo -e "${GREEN}Using podman-compose/docker-compose...${NC}"
            if command -v podman-compose &> /dev/null; then
                TRILINOS_VERSION=$version podman-compose up "$@"
            elif command -v docker-compose &> /dev/null; then
                TRILINOS_VERSION=$version docker-compose up "$@"
            else
                echo -e "${RED}Error: Neither podman-compose nor docker-compose found${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}Unknown test type: $test_type${NC}"
            echo ""
            echo "Usage: $0 [TEST_TYPE] [TRILINOS_VERSION] [EXTRA_PYTEST_ARGS]"
            echo ""
            echo "Test types:"
            echo "  quick, q         - Quick smoke tests (default)"
            echo "  fast, f          - All tests except install (includes spec validation)"
            echo "  full, all, nightly - Full suite including real installs (6-10 hours)"
            echo "  shell, sh        - Interactive shell"
            echo "  compose, dc      - Use podman-compose/docker-compose"
            echo ""
            echo "Trilinos versions (from trilinos_base_class/package.py):"
            echo "  develop          - Develop branch (default)"
            echo "  jfrye-spack-changes - Custom branch"
            echo "  master           - Master branch (if defined)"
            echo "  <version>        - Any defined version"
            echo ""
            echo "Examples:"
            echo "  $0 quick                        # Quick tests with develop"
            echo "  $0 quick develop                # Explicitly use develop"
            echo "  $0 fast jfrye-spack-changes     # Test custom branch"
            echo "  $0 quick develop -k test_spack_info  # Run specific test"
            echo "  $0 full develop --maxfail=1     # Stop on first failure"
            echo "  $0 shell develop                # Interactive debugging"
            exit 1
            ;;
    esac
}

# Check if image exists
if ! $CONTAINER_CMD image inspect trilinos-spack-packages:latest &> /dev/null; then
    echo -e "${RED}Error: Container image not found${NC}"
    echo -e "${YELLOW}Please build the image first:${NC}"
    echo -e "  ./docker-build-optimized.sh"
    exit 1
fi

# Run tests
run_tests "$TEST_TYPE" "$TRILINOS_VERSION" $EXTRA_ARGS

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tests Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
