#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Trilinos Spack Packages${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse arguments
BUILD_STAGE="${1:-app}"
USE_CACHE="${USE_CACHE:-true}"

# Determine cache flag
if [ "$USE_CACHE" = "false" ]; then
    CACHE_FLAG="--no-cache"
    echo -e "${YELLOW}Building without cache${NC}"
else
    CACHE_FLAG=""
    echo -e "${GREEN}Using Docker layer cache${NC}"
fi

echo -e "${BLUE}Target stage: ${BUILD_STAGE}${NC}"
echo ""

# Build with optimal caching
echo -e "${BLUE}Step 1/5: Building base system...${NC}"
docker build $CACHE_FLAG \
    --target base \
    -t trilinos-spack-packages:base \
    .

echo ""
echo -e "${BLUE}Step 2/5: Setting up Spack (may take 5-10 minutes)...${NC}"
docker build $CACHE_FLAG \
    --target spack-base \
    -t trilinos-spack-packages:spack-base \
    .

echo ""
echo -e "${BLUE}Step 3/5: Installing Python dependencies...${NC}"
docker build $CACHE_FLAG \
    --target python-deps \
    -t trilinos-spack-packages:python-deps \
    .

echo ""
echo -e "${BLUE}Step 4/5: Adding application code...${NC}"
docker build $CACHE_FLAG \
    --target app \
    -t trilinos-spack-packages:app \
    -t trilinos-spack-packages:latest \
    .

if [ "$BUILD_STAGE" = "test" ]; then
    echo ""
    echo -e "${BLUE}Step 5/5: Running build-time tests...${NC}"
    docker build $CACHE_FLAG \
        --target test \
        -t trilinos-spack-packages:test \
        .
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Tagged images:"
echo -e "  ${BLUE}trilinos-spack-packages:base${NC}        - Base system"
echo -e "  ${BLUE}trilinos-spack-packages:spack-base${NC}  - Spack setup (cached)"
echo -e "  ${BLUE}trilinos-spack-packages:python-deps${NC} - Python deps"
echo -e "  ${BLUE}trilinos-spack-packages:app${NC}         - Application ready"
echo -e "  ${BLUE}trilinos-spack-packages:latest${NC}      - Alias for app"
if [ "$BUILD_STAGE" = "test" ]; then
    echo -e "  ${BLUE}trilinos-spack-packages:test${NC}        - With tests run"
fi
echo ""
echo -e "Next steps:"
echo -e "  ${GREEN}./docker-run.sh quick${NC}  - Run quick tests"
echo -e "  ${GREEN}./docker-run.sh fast${NC}   - Run all except slow tests"
echo -e "  ${GREEN}./docker-run.sh full${NC}   - Run full test suite"
echo -e "  ${GREEN}./docker-run.sh shell${NC}  - Interactive shell"
echo ""
