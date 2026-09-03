#!/bin/bash
# Calculate a hash representing the current state of files that affect the container build
# Returns a consistent hash that changes only when relevant source files change

set -e

# Find and hash all relevant files
{
    # Infrastructure
    find . -maxdepth 1 -name "Dockerfile*" -o -name "requirements.txt" -o -name "setup-spack.sh" | sort | xargs cat 2>/dev/null

    # Package generation
    cat tools/generate_spack_packages.py tools/parse_tribits_xml.py 2>/dev/null

    # Dependencies
    cat dependencies.lock 2>/dev/null
    find xml_files -name "*.xml" 2>/dev/null | sort | xargs cat 2>/dev/null

    # Spack packages (all package.py files)
    find spack_repo/trilinos/packages -name "package.py" 2>/dev/null | sort | xargs cat 2>/dev/null

} | sha256sum | cut -d' ' -f1
