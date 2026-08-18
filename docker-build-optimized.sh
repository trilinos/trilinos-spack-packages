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
    echo -e "${GREEN}Using Podman${NC}"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    echo -e "${GREEN}Using Docker${NC}"
else
    echo -e "${RED}Error: Neither podman nor docker found${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Building Trilinos Spack Packages (OPTIMIZED)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse arguments
BUILD_STAGE="${1:-app}"
USE_CACHE="${USE_CACHE:-true}"
DISABLE_SSL_VERIFY="${DISABLE_SSL_VERIFY:-false}"
FORCE_DEPS_REBUILD="${FORCE_DEPS_REBUILD:-false}"

# Extract current dependencies
echo -e "${BLUE}Extracting dependency versions...${NC}"
python3 extract_dependencies.py .

CURRENT_DEPS_HASH=$(cat dependencies.lock | grep -o '"hash": "[^"]*"' | cut -d'"' -f4 | cut -c1-12)
echo -e "${GREEN}Current dependency hash: ${CURRENT_DEPS_HASH}${NC}"

# Check if dependencies changed
DEPS_CHANGED=false
PREVIOUS_DEPS_FILE=".docker-deps-cache"

if [ -f "$PREVIOUS_DEPS_FILE" ]; then
    PREVIOUS_DEPS_HASH=$(cat "$PREVIOUS_DEPS_FILE")
    if [ "$CURRENT_DEPS_HASH" != "$PREVIOUS_DEPS_HASH" ]; then
        echo -e "${YELLOW}Dependencies changed!${NC}"
        echo -e "  Previous: ${PREVIOUS_DEPS_HASH}"
        echo -e "  Current:  ${CURRENT_DEPS_HASH}"
        DEPS_CHANGED=true
    else
        echo -e "${GREEN}Dependencies unchanged (cached)${NC}"
    fi
else
    echo -e "${YELLOW}No previous dependency cache found${NC}"
    DEPS_CHANGED=true
fi

# Force rebuild if requested
if [ "$FORCE_DEPS_REBUILD" = "true" ]; then
    echo -e "${YELLOW}Forcing dependency rebuild${NC}"
    DEPS_CHANGED=true
fi

# Determine cache strategy
if [ "$USE_CACHE" = "false" ]; then
    CACHE_FLAG="--no-cache"
    echo -e "${YELLOW}Building without cache${NC}"
else
    if [ "$DEPS_CHANGED" = "true" ]; then
        # Invalidate only deps-cache and later stages
        CACHE_FLAG="--no-cache"
        CACHE_FROM_DEPS=""
        echo -e "${YELLOW}Rebuilding from deps-cache stage${NC}"
    else
        CACHE_FLAG=""
        CACHE_FROM_DEPS="--cache-from=trilinos-spack-packages:deps-cache"
        echo -e "${GREEN}Using full layer cache${NC}"
    fi
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

# Use optimized Dockerfile
DOCKERFILE="Dockerfile.optimized"
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}Error: $DOCKERFILE not found${NC}"
    echo -e "${YELLOW}Falling back to standard Dockerfile${NC}"
    DOCKERFILE="Dockerfile"
fi

# Build with optimal caching
START_TIME=$(date +%s)

echo -e "${BLUE}Step 1/5: Building base system...${NC}"
$CONTAINER_CMD build $SSL_FLAG \
    --target base \
    -t trilinos-spack-packages:base \
    -f "$DOCKERFILE" \
    .

echo ""
echo -e "${BLUE}Step 2/5: Setting up Spack with build cache (may take 5-10 minutes)...${NC}"
$CONTAINER_CMD build $SSL_FLAG \
    --target spack-base \
    -t trilinos-spack-packages:spack-base \
    -f "$DOCKERFILE" \
    .

echo ""
echo -e "${BLUE}Step 3/5: Installing Python dependencies...${NC}"
$CONTAINER_CMD build $SSL_FLAG \
    --target python-deps \
    -t trilinos-spack-packages:python-deps \
    -f "$DOCKERFILE" \
    .

echo ""
if [ "$DEPS_CHANGED" = "true" ]; then
    echo -e "${BLUE}Step 4/5: Installing heavy dependencies (REBUILDING - may take 20-40 minutes)...${NC}"
    $CONTAINER_CMD build $CACHE_FLAG $SSL_FLAG \
        --target deps-cache \
        -t trilinos-spack-packages:deps-cache \
        -f "$DOCKERFILE" \
        .

    # Save new dependency hash
    echo "$CURRENT_DEPS_HASH" > "$PREVIOUS_DEPS_FILE"
    echo -e "${GREEN}Saved new dependency hash: ${CURRENT_DEPS_HASH}${NC}"
else
    echo -e "${BLUE}Step 4/5: Using cached dependencies...${NC}"
    if ! $CONTAINER_CMD image inspect trilinos-spack-packages:deps-cache &> /dev/null; then
        echo -e "${YELLOW}Cache not found, building dependencies...${NC}"
        $CONTAINER_CMD build $SSL_FLAG \
            --target deps-cache \
            -t trilinos-spack-packages:deps-cache \
            -f "$DOCKERFILE" \
            .
        echo "$CURRENT_DEPS_HASH" > "$PREVIOUS_DEPS_FILE"
    else
        echo -e "${GREEN}Using existing deps-cache image${NC}"
    fi
fi

echo ""
echo -e "${BLUE}Step 5/5: Adding application code...${NC}"
$CONTAINER_CMD build $SSL_FLAG $CACHE_FROM_DEPS \
    --target app \
    -t trilinos-spack-packages:app \
    -t trilinos-spack-packages:latest \
    -f "$DOCKERFILE" \
    .

if [ "$BUILD_STAGE" = "test" ]; then
    echo ""
    echo -e "${BLUE}Step 6/5: Running build-time tests...${NC}"
    $CONTAINER_CMD build $SSL_FLAG \
        --target test \
        -t trilinos-spack-packages:test \
        -f "$DOCKERFILE" \
        .
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build Complete in ${MINUTES}m ${SECONDS}s!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Tagged images:"
echo -e "  ${BLUE}trilinos-spack-packages:base${NC}        - Base system"
echo -e "  ${BLUE}trilinos-spack-packages:spack-base${NC}  - Spack setup (cached)"
echo -e "  ${BLUE}trilinos-spack-packages:python-deps${NC} - Python deps"
echo -e "  ${BLUE}trilinos-spack-packages:deps-cache${NC}  - Heavy dependencies (cached)"
echo -e "  ${BLUE}trilinos-spack-packages:app${NC}         - Application ready"
echo -e "  ${BLUE}trilinos-spack-packages:latest${NC}      - Alias for app"
if [ "$BUILD_STAGE" = "test" ]; then
    echo -e "  ${BLUE}trilinos-spack-packages:test${NC}        - With tests run"
fi
echo ""
echo -e "Dependency cache:"
echo -e "  Hash: ${CURRENT_DEPS_HASH}"
echo -e "  File: ${PREVIOUS_DEPS_FILE}"
echo ""
echo -e "Next steps:"
echo -e "  ${GREEN}./docker-run.sh quick${NC}  - Run quick tests"
echo -e "  ${GREEN}./docker-run.sh fast${NC}   - Run all except slow tests"
echo -e "  ${GREEN}./docker-run.sh full${NC}   - Run full test suite"
echo -e "  ${GREEN}./docker-run.sh shell${NC}  - Interactive shell"
echo ""
echo -e "To force dependency rebuild:"
echo -e "  ${YELLOW}FORCE_DEPS_REBUILD=true ./docker-build-optimized.sh${NC}"
echo ""
