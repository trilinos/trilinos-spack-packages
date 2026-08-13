#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo "Error: Neither podman nor docker found"
    exit 1
fi

echo -e "${BLUE}Quick rebuild of app layer...${NC}"

$CONTAINER_CMD rmi trilinos-spack-packages:app 2>/dev/null || true
$CONTAINER_CMD rmi trilinos-spack-packages:latest 2>/dev/null || true

$CONTAINER_CMD build --target app -t trilinos-spack-packages:app -t trilinos-spack-packages:latest .

echo ""
echo -e "${GREEN}Done! Testing pytest -n flag...${NC}"
$CONTAINER_CMD run --rm trilinos-spack-packages:latest pytest --version
$CONTAINER_CMD run --rm trilinos-spack-packages:latest pytest -n 2 --co -q test/ | head -5

echo ""
echo -e "${GREEN}Now try: ./docker-run.sh quick${NC}"
