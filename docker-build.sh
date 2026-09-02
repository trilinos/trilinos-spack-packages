#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect container runtime (podman or docker)
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    echo -e "${GREEN}Using Podman${NC}"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    echo -e "${GREEN}Using Docker${NC}"
else
    echo -e "${YELLOW}Error: Neither podman nor docker found${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Trilinos Spack Packages${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse arguments
BUILD_STAGE="${1:-app}"
USE_CACHE="${USE_CACHE:-true}"
DISABLE_SSL_VERIFY="${DISABLE_SSL_VERIFY:-false}"

# Check if building with-deps stage
if [ "$BUILD_STAGE" = "with-deps" ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}WARNING: Building with pre-installed dependencies${NC}"
    echo -e "${YELLOW}This will take 30-60 minutes!${NC}"
    echo -e "${YELLOW}========================================${NC}"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Build cancelled."
        exit 0
    fi
fi

# Determine cache flag
if [ "$USE_CACHE" = "false" ]; then
    CACHE_FLAG="--no-cache"
    echo -e "${YELLOW}Building without cache${NC}"
else
    CACHE_FLAG=""
    echo -e "${GREEN}Using layer cache${NC}"
fi

# SSL verification flag
if [ "$DISABLE_SSL_VERIFY" = "true" ]; then
    SSL_FLAG="--build-arg DISABLE_SSL_VERIFY=true"
    echo -e "${YELLOW}WARNING: SSL verification disabled${NC}"
else
    SSL_FLAG=""
fi

echo -e "${BLUE}Target stage: ${BUILD_STAGE}${NC}"
echo ""

# Build with optimal caching
echo -e "${BLUE}Step 1/5: Building base system...${NC}"
$CONTAINER_CMD build $CACHE_FLAG $SSL_FLAG \
    --target base \
    -t trilinos-spack-packages:base \
    .

echo ""
echo -e "${BLUE}Step 2/5: Setting up Spack (may take 5-10 minutes)...${NC}"
$CONTAINER_CMD build $CACHE_FLAG $SSL_FLAG \
    --target spack-base \
    -t trilinos-spack-packages:spack-base \
    .

echo ""
echo -e "${BLUE}Step 3/5: Installing Python dependencies...${NC}"
$CONTAINER_CMD build $CACHE_FLAG $SSL_FLAG \
    --target python-deps \
    -t trilinos-spack-packages:python-deps \
    .

echo ""
echo -e "${BLUE}Step 4/5: Adding application code...${NC}"
# Calculate source hash if not provided
if [ -z "$SOURCE_HASH" ]; then
    SOURCE_HASH=$(./calculate-build-hash.sh 2>/dev/null || echo "unknown")
fi
echo -e "${GREEN}Source hash: $SOURCE_HASH${NC}"

$CONTAINER_CMD build $CACHE_FLAG $SSL_FLAG \
    --target app \
    --label "source-hash=$SOURCE_HASH" \
    -t trilinos-spack-packages:app \
    -t trilinos-spack-packages:latest \
    .

if [ "$BUILD_STAGE" = "test" ]; then
    echo ""
    echo -e "${BLUE}Step 5/5: Running build-time tests...${NC}"
    $CONTAINER_CMD build $CACHE_FLAG $SSL_FLAG \
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
