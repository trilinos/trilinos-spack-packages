#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    echo -e "${RED}Error: Neither podman nor docker found${NC}"
    exit 1
fi

BENCHMARK_LOG="benchmark-results-$(date +%Y%m%d-%H%M%S).log"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Container Build Benchmark${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo "Results will be saved to: $BENCHMARK_LOG"
echo ""

# Function to time a build
time_build() {
    local name=$1
    local script=$2
    local no_cache=$3

    echo -e "${BLUE}========================================${NC}" | tee -a "$BENCHMARK_LOG"
    echo -e "${BLUE}Benchmarking: $name${NC}" | tee -a "$BENCHMARK_LOG"
    echo -e "${BLUE}========================================${NC}" | tee -a "$BENCHMARK_LOG"

    # Clean up previous builds if no-cache
    if [ "$no_cache" = "true" ]; then
        echo -e "${YELLOW}Removing cached images...${NC}" | tee -a "$BENCHMARK_LOG"
        $CONTAINER_CMD rmi -f trilinos-spack-packages:app trilinos-spack-packages:latest \
            trilinos-spack-packages:deps-cache trilinos-spack-packages:python-deps \
            trilinos-spack-packages:spack-base trilinos-spack-packages:base 2>/dev/null || true
    fi

    START=$(date +%s)
    echo "Start time: $(date)" | tee -a "$BENCHMARK_LOG"

    # Run build
    if [ "$no_cache" = "true" ]; then
        USE_CACHE=false $script 2>&1 | tee -a "$BENCHMARK_LOG"
    else
        $script 2>&1 | tee -a "$BENCHMARK_LOG"
    fi

    END=$(date +%s)
    DURATION=$((END - START))
    MINUTES=$((DURATION / 60))
    SECONDS=$((DURATION % 60))

    echo "" | tee -a "$BENCHMARK_LOG"
    echo -e "${GREEN}$name completed in: ${MINUTES}m ${SECONDS}s${NC}" | tee -a "$BENCHMARK_LOG"
    echo "" | tee -a "$BENCHMARK_LOG"

    # Store result
    echo "${name}:${DURATION}" >> "$BENCHMARK_LOG.timings"
}

# Function to get image size
get_image_size() {
    local image=$1
    if $CONTAINER_CMD image inspect "$image" &> /dev/null; then
        $CONTAINER_CMD image inspect "$image" --format='{{.Size}}' | \
            awk '{print $1/1024/1024 " MB"}'
    else
        echo "N/A"
    fi
}

# Clear timing file
rm -f "$BENCHMARK_LOG.timings"

echo -e "${YELLOW}Select benchmark mode:${NC}"
echo "1. Quick comparison (cached builds only)"
echo "2. Full comparison (clean + cached builds)"
echo "3. Dependency change simulation"
echo "4. All of the above"
echo ""
read -p "Enter choice [1-4]: " CHOICE

case $CHOICE in
    1)
        echo -e "${CYAN}Running quick comparison...${NC}"
        echo ""

        if [ -f "docker-build.sh" ]; then
            time_build "Original (Cached)" "./docker-build.sh" false
        fi

        if [ -f "docker-build-optimized.sh" ]; then
            time_build "Optimized (Cached)" "./docker-build-optimized.sh" false
        fi
        ;;

    2)
        echo -e "${CYAN}Running full comparison (this will take a while)...${NC}"
        echo ""

        if [ -f "docker-build.sh" ]; then
            time_build "Original (No Cache)" "./docker-build.sh" true
            time_build "Original (Cached)" "./docker-build.sh" false
        fi

        if [ -f "docker-build-optimized.sh" ]; then
            time_build "Optimized (No Cache)" "./docker-build-optimized.sh" true
            time_build "Optimized (Cached)" "./docker-build-optimized.sh" false
        fi
        ;;

    3)
        echo -e "${CYAN}Simulating dependency change...${NC}"
        echo ""

        if [ ! -f "docker-build-optimized.sh" ]; then
            echo -e "${RED}Optimized build script not found${NC}"
            exit 1
        fi

        # Initial build
        time_build "Optimized (Initial)" "./docker-build-optimized.sh" false

        # Simulate version change
        echo -e "${YELLOW}Simulating Kokkos version change...${NC}" | tee -a "$BENCHMARK_LOG"
        TEMP_FILE="spack_repo/trilinos/packages/trilinos_base_class/package.py.bak"
        cp spack_repo/trilinos/packages/trilinos_base_class/package.py "$TEMP_FILE"

        # Change version
        sed -i 's/kokkos_version=".*"/kokkos_version="9.9.9"/' \
            spack_repo/trilinos/packages/trilinos_base_class/package.py

        # Rebuild
        time_build "Optimized (After Dependency Change)" "./docker-build-optimized.sh" false

        # Restore
        mv "$TEMP_FILE" spack_repo/trilinos/packages/trilinos_base_class/package.py
        echo -e "${GREEN}Restored original package.py${NC}"
        ;;

    4)
        echo -e "${CYAN}Running complete benchmark suite...${NC}"
        echo -e "${RED}WARNING: This will take several hours!${NC}"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi

        # Run all benchmarks
        $0 <<< "2"  # Full comparison
        $0 <<< "3"  # Dependency change
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Benchmark Summary${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Display results
if [ -f "$BENCHMARK_LOG.timings" ]; then
    echo -e "${BLUE}Build Times:${NC}"
    while IFS=: read -r name seconds; do
        minutes=$((seconds / 60))
        secs=$((seconds % 60))
        printf "  %-35s %3dm %2ds (%d seconds)\n" "$name" "$minutes" "$secs" "$seconds"
    done < "$BENCHMARK_LOG.timings"

    # Calculate speedup if we have both original and optimized
    ORIG_TIME=$(grep "Original (Cached)" "$BENCHMARK_LOG.timings" | cut -d: -f2)
    OPT_TIME=$(grep "Optimized (Cached)" "$BENCHMARK_LOG.timings" | cut -d: -f2)

    if [ -n "$ORIG_TIME" ] && [ -n "$OPT_TIME" ]; then
        SPEEDUP=$(echo "scale=2; $ORIG_TIME / $OPT_TIME" | bc)
        SAVED=$((ORIG_TIME - OPT_TIME))
        echo ""
        echo -e "${GREEN}Speedup: ${SPEEDUP}x faster${NC}"
        echo -e "${GREEN}Time saved: ${SAVED} seconds${NC}"
    fi
fi

echo ""
echo -e "${BLUE}Image Sizes:${NC}"
echo "  Base:        $(get_image_size trilinos-spack-packages:base)"
echo "  Spack:       $(get_image_size trilinos-spack-packages:spack-base)"
echo "  Python deps: $(get_image_size trilinos-spack-packages:python-deps)"
echo "  Deps cache:  $(get_image_size trilinos-spack-packages:deps-cache)"
echo "  App:         $(get_image_size trilinos-spack-packages:app)"

echo ""
echo -e "${GREEN}Full benchmark log saved to: $BENCHMARK_LOG${NC}"
echo ""
