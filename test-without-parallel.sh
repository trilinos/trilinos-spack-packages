#!/bin/bash
# Temporary script to run tests without parallel execution
# Use this until pytest-xdist is properly installed in container

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Running tests WITHOUT parallel execution${NC}"
echo ""

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo "Error: Neither podman nor docker found"
    exit 1
fi

TEST_TYPE="${1:-quick}"

case $TEST_TYPE in
    quick|q)
        echo -e "${GREEN}Running quick smoke tests...${NC}"
        $CONTAINER_CMD run --rm trilinos-spack-packages:latest \
            pytest test/ -m quick -v
        ;;
    fast|f)
        echo -e "${GREEN}Running fast tests (excluding installs)...${NC}"
        $CONTAINER_CMD run --rm trilinos-spack-packages:latest \
            pytest test/ -m "not slow" -v
        ;;
    full|all)
        echo -e "${GREEN}Running full test suite...${NC}"
        $CONTAINER_CMD run --rm trilinos-spack-packages:latest \
            pytest test/ -v
        ;;
    *)
        echo "Usage: $0 [quick|fast|full]"
        exit 1
        ;;
esac
