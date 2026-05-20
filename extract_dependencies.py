#!/usr/bin/env python3
"""
Extract dependency versions from trilinos_base_class/package.py
Generates:
1. dependencies.txt - List of spack specs for Docker build
2. dependencies.lock - Hash of current versions for cache invalidation
"""

import re
import hashlib
import json
from pathlib import Path


def extract_dependency_versions(package_file):
    """Parse package.py and extract version variables."""
    with open(package_file, 'r') as f:
        content = f.read()

    # Extract version variables (e.g., kokkos_version="5.2.0")
    # Look for pattern: variable_name_version="X.Y.Z"
    version_pattern = r'(\w+)_version\s*=\s*["\']([^"\']+)["\']'
    version_vars = dict(re.findall(version_pattern, content))

    # Extract depends_on statements with versions
    # Look for: depends_on("package@X.Y.Z") or depends_on(f"package@{var}")
    depends_pattern = r'depends_on\(["\']([^"\']+)@([\d\.]+)["\']'
    depends_versions = dict(re.findall(depends_pattern, content))

    # Merge: version_vars takes precedence (they're the source of truth)
    versions = {}
    for key, value in version_vars.items():
        # Remove _version suffix to get package name
        pkg_name = key.replace('_version', '')
        versions[pkg_name] = value

    # Add any explicit depends_on versions not in variables
    for pkg, ver in depends_versions.items():
        if pkg not in versions:
            versions[pkg] = ver

    return versions


def extract_common_dependencies():
    """
    Extract common heavy dependencies that should be pre-installed.
    These are the dependencies that:
    1. Take longest to build (10+ minutes)
    2. Are used by most Trilinos packages
    3. Change infrequently
    """

    # Try multiple possible locations for the base package
    possible_paths = [
        Path(__file__).parent / "spack_repo/trilinos/packages/trilinos_base_class/package.py",
        Path.cwd() / "spack_repo/trilinos/packages/trilinos_base_class/package.py",
        Path("/projects/trilinos-spack-packages/spack_repo/trilinos/packages/trilinos_base_class/package.py"),
    ]

    base_package = None
    for path in possible_paths:
        if path.exists():
            base_package = path
            break

    if base_package is None:
        raise FileNotFoundError(
            f"Base package not found. Tried:\n" +
            "\n".join(f"  - {p}" for p in possible_paths)
        )

    versions = extract_dependency_versions(base_package)

    # Define heavy dependencies to pre-install
    # Order matters: independent packages first, then dependent ones
    dependencies = {
        'independent': [],  # Can install in parallel
        'dependent': []      # Must install after independent
    }

    # Independent packages (can be installed in parallel)
    if 'kokkos' in versions:
        dependencies['independent'].append(f"kokkos@{versions['kokkos']}")
    if 'openmpi' in versions:
        dependencies['independent'].append(f"openmpi@{versions['openmpi']}")

    # Add common dependencies without version (use spack defaults)
    dependencies['independent'].extend([
        "openblas",
        "boost"
    ])

    # Dependent packages (kokkos-kernels needs kokkos)
    dependencies['dependent'].append("kokkos-kernels")

    return dependencies, versions


def generate_dependency_files(output_dir="."):
    """Generate dependency files for Docker build."""
    output_dir = Path(output_dir)

    try:
        deps, versions = extract_common_dependencies()
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Using fallback dependencies")
        deps = {
            'independent': ["kokkos@5.2.0", "openmpi@4.1.6", "openblas", "boost"],
            'dependent': ["kokkos-kernels"]
        }
        versions = {'kokkos': '5.2.0', 'openmpi': '4.1.6'}

    # Write dependencies.txt (for Docker to read)
    deps_file = output_dir / "dependencies.txt"
    with open(deps_file, 'w') as f:
        f.write("# Independent dependencies (install in parallel)\n")
        f.write('\n'.join(deps['independent']) + '\n')
        f.write("\n# Dependent packages (install after independent)\n")
        f.write('\n'.join(deps['dependent']) + '\n')

    # Write dependencies.lock (hash for cache invalidation)
    lock_data = {
        'versions': versions,
        'independent': deps['independent'],
        'dependent': deps['dependent']
    }
    lock_hash = hashlib.sha256(json.dumps(lock_data, sort_keys=True).encode()).hexdigest()

    lock_file = output_dir / "dependencies.lock"
    with open(lock_file, 'w') as f:
        json.dump({
            'hash': lock_hash,
            'versions': versions,
            'dependencies': deps
        }, f, indent=2)

    print(f"Generated {deps_file}")
    print(f"Generated {lock_file}")
    print(f"\nDependency hash: {lock_hash[:12]}")
    print(f"\nVersions:")
    for pkg, ver in sorted(versions.items()):
        print(f"  {pkg}: {ver}")

    return deps_file, lock_file, lock_hash


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_dependency_files(output_dir)
