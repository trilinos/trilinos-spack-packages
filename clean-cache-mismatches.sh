#!/bin/bash
# Smart cache cleanup: removes only dependency versions that don't match package.py
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Smart Spack Cache Cleanup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Ensure spack is loaded
if ! command -v spack &> /dev/null; then
    echo -e "${RED}Error: spack not found in PATH${NC}"
    echo "Run: source spack_src/share/spack/setup-env.sh"
    exit 1
fi

# Extract expected versions from trilinos_base_class/package.py
BASE_CLASS="spack_repo/trilinos/packages/trilinos_base_class/package.py"
if [ ! -f "$BASE_CLASS" ]; then
    echo -e "${RED}Error: Cannot find $BASE_CLASS${NC}"
    exit 1
fi

echo -e "${BLUE}Reading expected versions from $BASE_CLASS...${NC}"
KOKKOS_VERSION=$(grep 'kokkos_version=' "$BASE_CLASS" | sed 's/.*kokkos_version="\([^"]*\)".*/\1/')
OPENMPI_VERSION=$(grep 'openmpi_version=' "$BASE_CLASS" | sed 's/.*openmpi_version="\([^"]*\)".*/\1/')
SUPERLU_VERSION=$(grep 'superlu_version=' "$BASE_CLASS" | sed 's/.*superlu_version="\([^"]*\)".*/\1/')

echo -e "  Kokkos:  ${GREEN}${KOKKOS_VERSION}${NC}"
echo -e "  OpenMPI: ${GREEN}${OPENMPI_VERSION}${NC}"
echo -e "  SuperLU: ${GREEN}${SUPERLU_VERSION}${NC}"
echo ""

# Function to check and clean a package
check_and_clean() {
    local pkg_name=$1
    local expected_version=$2

    echo -e "${BLUE}Checking ${pkg_name}...${NC}"

    # Get all installed versions
    local installed=$(spack find --format "{version}" "$pkg_name" 2>/dev/null || true)

    if [ -z "$installed" ]; then
        echo -e "  ${YELLOW}No ${pkg_name} installations found${NC}"
        return
    fi

    local removed=0
    while IFS= read -r version; do
        if [ "$version" != "$expected_version" ]; then
            echo -e "  ${YELLOW}Removing ${pkg_name}@${version} (expected ${expected_version})${NC}"
            spack uninstall -y "${pkg_name}@${version}" 2>&1 | sed 's/^/    /'
            removed=$((removed + 1))
        else
            echo -e "  ${GREEN}Keeping ${pkg_name}@${version} ✓${NC}"
        fi
    done <<< "$installed"

    if [ $removed -eq 0 ]; then
        echo -e "  ${GREEN}All versions match!${NC}"
    fi
    echo ""
}

# Clean mismatched versions
check_and_clean "kokkos" "$KOKKOS_VERSION"
check_and_clean "openmpi" "$OPENMPI_VERSION"
# SuperLU is disabled in our packages, but clean it anyway if present
check_and_clean "superlu" "$SUPERLU_VERSION"

# Also check kokkos-kernels (should match kokkos version)
echo -e "${BLUE}Checking kokkos-kernels compatibility...${NC}"
KKERNELS_INSTALLED=$(spack find --format "{name}@{version} ^{dependencies}" kokkos-kernels 2>/dev/null | grep -oP "kokkos@\K[0-9.]+" | sort -u || true)
if [ -n "$KKERNELS_INSTALLED" ]; then
    while IFS= read -r kversion; do
        if [ "$kversion" != "$KOKKOS_VERSION" ]; then
            echo -e "  ${YELLOW}Removing kokkos-kernels built against kokkos@${kversion}${NC}"
            spack uninstall -y "kokkos-kernels ^kokkos@${kversion}" 2>&1 | sed 's/^/    /'
        else
            echo -e "  ${GREEN}kokkos-kernels built against kokkos@${kversion} ✓${NC}"
        fi
    done <<< "$KKERNELS_INSTALLED"
else
    echo -e "  ${YELLOW}No kokkos-kernels installations found${NC}"
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cache cleanup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Remaining packages:"
spack find
