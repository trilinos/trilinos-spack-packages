#!/bin/bash
# Add the trilinos package repository to spack
# Run this after spack is already set up and sourced

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRILINOS_REPO="${SCRIPT_DIR}/spack_repo/trilinos"

# Check if spack is available
if ! command -v spack &> /dev/null; then
    echo "ERROR: spack command not found"
    echo "Please source spack's setup-env.sh first:"
    echo "  source /path/to/spack/share/spack/setup-env.sh"
    exit 1
fi

# Check if trilinos repo directory exists
if [ ! -d "$TRILINOS_REPO" ]; then
    echo "ERROR: Trilinos repo not found at $TRILINOS_REPO"
    exit 1
fi

echo "Adding trilinos package repository to spack..."

# Check if already added
if spack repo list | grep -q "$TRILINOS_REPO"; then
    echo "✓ Trilinos repo is already registered"
    echo ""
    spack repo list | grep -A 1 trilinos
else
    spack repo add "$TRILINOS_REPO"
    echo "✓ Trilinos repo added successfully"
    echo ""
    spack repo list | grep -A 1 trilinos
fi

echo ""
echo "Trilinos packages available:"
spack list trilinos-* | grep -v "trilinos-base-class" | head -10
echo "... (use 'spack list trilinos-*' to see all)"
