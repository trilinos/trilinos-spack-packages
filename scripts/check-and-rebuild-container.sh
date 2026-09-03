#!/bin/bash
set -e

# Check if container needs rebuilding and rebuild if necessary
# Returns: 0 if container is ready, non-zero on error

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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Checking Container Status${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Pull latest changes
echo -e "${BLUE}Pulling latest changes from git...${NC}"

# Clean up generated dependency files before pull (they'll be regenerated after)
echo -e "${BLUE}Resetting generated dependency files to avoid merge conflicts...${NC}"
git checkout -- dependencies.txt dependencies.lock 2>/dev/null || true

export GIT_TERMINAL_PROMPT=0  # Prevent credential prompts in cron
timeout 900 git fetch origin --progress 2>&1 || { echo -e "${RED}ERROR: git fetch timed out or failed${NC}"; exit 1; }
BEFORE_PULL=$(git rev-parse HEAD)
timeout 900 git pull origin main --progress 2>&1 || { echo -e "${RED}ERROR: git pull timed out or failed${NC}"; exit 1; }
AFTER_PULL=$(git rev-parse HEAD)

if [ "$BEFORE_PULL" != "$AFTER_PULL" ]; then
    echo -e "${GREEN}New commits detected: $BEFORE_PULL -> $AFTER_PULL${NC}"
    COMMITS_CHANGED=true
else
    echo -e "${GREEN}No new commits${NC}"
    COMMITS_CHANGED=false
fi

# Extract current dependencies
echo -e "${BLUE}Extracting dependency versions...${NC}"
if [ -f "extract_dependencies.py" ]; then
    python3 extract_dependencies.py .
    CURRENT_DEPS_HASH=$(cat dependencies.lock | grep -o '"hash": "[^"]*"' | cut -d'"' -f4 | cut -c1-12)
    echo -e "${GREEN}Current dependency hash: $CURRENT_DEPS_HASH${NC}"
else
    echo -e "${YELLOW}WARNING: extract_dependencies.py not found, using standard build${NC}"
    CURRENT_DEPS_HASH="unknown"
fi

# Check what changed using content hash
REBUILD_REASON="none"
SOURCE_HASH=$(./scripts/calculate-build-hash.sh)
echo -e "${GREEN}Current source hash: $SOURCE_HASH${NC}"

# Check if container exists and get its hash
if ! $CONTAINER_CMD image inspect trilinos-spack-packages:latest &> /dev/null; then
    echo -e "${YELLOW}Container image not found${NC}"
    REBUILD_REASON="image_missing"
elif CONTAINER_HASH=$($CONTAINER_CMD inspect trilinos-spack-packages:latest --format '{{index .Config.Labels "source-hash"}}' 2>/dev/null); then
    if [ -z "$CONTAINER_HASH" ]; then
        echo -e "${YELLOW}Container has no source hash label (old build)${NC}"
        REBUILD_REASON="missing_hash_label"
    elif [ "$SOURCE_HASH" != "$CONTAINER_HASH" ]; then
        echo -e "${YELLOW}Source hash mismatch (container: $CONTAINER_HASH, current: $SOURCE_HASH)${NC}"
        REBUILD_REASON="source_changed"
    else
        echo -e "${GREEN}Container matches current source (hash: $CONTAINER_HASH)${NC}"
    fi
else
    echo -e "${YELLOW}Could not read container labels${NC}"
    REBUILD_REASON="cannot_verify"
fi

# Decide whether to rebuild
if [ "$REBUILD_REASON" != "none" ]; then
    echo -e "${YELLOW}Container rebuild required: $REBUILD_REASON${NC}"

    # Use docker-build.sh
    echo -e "${BLUE}Building container (smart caching enabled)...${NC}"
    BUILD_START=$(date +%s)
    CONTAINER_CMD=$CONTAINER_CMD SOURCE_HASH=$SOURCE_HASH ./docker-build.sh
    BUILD_END=$(date +%s)
    BUILD_DURATION=$((BUILD_END - BUILD_START))
    BUILD_MINUTES=$((BUILD_DURATION / 60))
    echo -e "${GREEN}Container built in ${BUILD_MINUTES}m${NC}"
else
    echo -e "${GREEN}Container is up-to-date, skipping rebuild${NC}"
    echo -e "  - Source hash matches: $SOURCE_HASH"
    echo -e "  - Image exists and ready"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Container Ready!${NC}"
echo -e "${GREEN}========================================${NC}"

exit 0
