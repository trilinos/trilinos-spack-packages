#!/bin/bash
# Generate a Trilinos package dependency XML file from a Trilinos repo/branch.
#
# This ONLY produces the XML (in xml_files/). It does not regenerate the
# Spack packages or run any tests.
#
# Usage: generate-deps-xml.sh [--repo URL] [--branch BRANCH] [--output FILE]
#
#   --repo URL       Trilinos git repo to clone
#                    (default: https://github.com/fryeguy52/Trilinos.git)
#   --branch BRANCH  Branch to clone (default: changes-for-spack)
#   --output FILE    Output XML file name, written into xml_files/
#                    (default: TrilinosPackageDependencies-<YYYY-MM-DD>.xml)

set -e

GREEN='\033[0;32m'
NC='\033[0m'

REPO="https://github.com/fryeguy52/Trilinos.git"
BRANCH="changes-for-spack"
XML_FILE="TrilinosPackageDependencies-$(date +%F).xml"

usage() {
    sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)    REPO="$2"; shift 2 ;;
        --branch)  BRANCH="$2"; shift 2 ;;
        --output)  XML_FILE="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage >&2; exit 1 ;;
    esac
done

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
XML_DIR="$REPO_ROOT/xml_files"

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

echo -e "${GREEN}Cloning $REPO (branch: $BRANCH, shallow)...${NC}"
git clone --depth 1 --branch "$BRANCH" "$REPO" "$WORK_DIR/Trilinos"

echo -e "${GREEN}Generating dependency XML...${NC}"
mkdir -p "$WORK_DIR/configure"
cmake -S "$WORK_DIR/Trilinos" -B "$WORK_DIR/configure" \
    -D Trilinos_DEPS_XML_OUTPUT_FILE:FILEPATH="$WORK_DIR/configure/$XML_FILE"

mkdir -p "$XML_DIR"
cp "$WORK_DIR/configure/$XML_FILE" "$XML_DIR/$XML_FILE"

echo -e "${GREEN}Wrote $XML_DIR/$XML_FILE${NC}"
