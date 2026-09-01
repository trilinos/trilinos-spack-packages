#!/bin/bash
# Regenerate packages from Trilinos develop, then run tests
# Usage: regenerate-package-files.sh [--skip-regenerate] [pytest-args...]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SKIP_REGEN=false
if [[ "$1" == "--skip-regenerate" ]]; then
    SKIP_REGEN=true
    shift
fi

if [ "$SKIP_REGEN" = "false" ]; then
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Regenerating packages from Trilinos develop${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
    cd "$SCRIPT_DIR"
    
    mkdir -p tmp-nightly
    cd tmp-nightly
    
    # Clone Trilinos develop (shallow)
    echo -e "${GREEN}Cloning Trilinos develop (shallow)...${NC}"
    rm -rf Trilinos
    git clone --depth 1 --branch develop https://github.com/trilinos/Trilinos.git
    
    # Generate dependency XML
    echo -e "${GREEN}Generating dependency XML from Trilinos...${NC}"
    rm -rf trilinos-configure
    mkdir trilinos-configure
    cd trilinos-configure
    
    DATE=$(date +%F)
    XML_FILE="TrilinosPackageDependencies-${DATE}.xml"
    cmake -D Trilinos_DEPS_XML_OUTPUT_FILE:FILEPATH=$PWD/$XML_FILE ../Trilinos/
    
    # Copy XML to main location
    echo -e "${GREEN}Copying XML to xml_files/...${NC}"
    mkdir -p ../../xml_files
    cp $XML_FILE ../../xml_files/
    
    cd ../..
    
    # Regenerate packages
    echo -e "${GREEN}Regenerating Spack packages...${NC}"
    python3 generate_spack_packages.py --xml xml_files/$XML_FILE
    
    echo -e "${GREEN}Package regeneration complete!${NC}"
    echo ""
else
    echo -e "${YELLOW}Skipping package regeneration (using existing packages)${NC}"
    echo ""
fi

# Run tests
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

pytest test/ -n auto -v "$@"
