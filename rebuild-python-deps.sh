#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo -e "${YELLOW}Error: Neither podman nor docker found${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Rebuilding Python Dependencies Layer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Removing python-deps and app images to force rebuild...${NC}"
$CONTAINER_CMD rmi trilinos-spack-packages:python-deps 2>/dev/null || true
$CONTAINER_CMD rmi trilinos-spack-packages:app 2>/dev/null || true
$CONTAINER_CMD rmi trilinos-spack-packages:latest 2>/dev/null || true

echo ""
echo -e "${BLUE}Rebuilding python-deps stage...${NC}"
$CONTAINER_CMD build --target python-deps -t trilinos-spack-packages:python-deps .

echo ""
echo -e "${BLUE}Rebuilding app stage...${NC}"
$CONTAINER_CMD build --target app -t trilinos-spack-packages:app -t trilinos-spack-packages:latest .

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Rebuild Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Verifying pytest-xdist installation..."
$CONTAINER_CMD run --rm trilinos-spack-packages:latest bash -c \
    "source /opt/spack-src/share/spack/setup-env.sh && spack load python && pip3 list | grep -i xdist" || \
    echo -e "${YELLOW}Warning: pytest-xdist not found${NC}"

echo ""
echo -e "Now try: ${GREEN}./docker-run.sh quick${NC}"
