#!/usr/bin/env python3
"""
generate_spack_packages.py

Uses parse_tribits_xml.parse_xml() to load Trilinos package objects from a
TriBITS XML file, then writes one Spack package.py per top-level package.

Output directory structure:
    <outdir>/trilinos_<lower>/package.py

Current scope
-------------
  - Package header  (class declaration, homepage, url, git, versions)
  - Required TPL dependencies  (depends_on("..."))
  - Package footer  (cmake_args stub)

Usage
-----
    python generate_spack_packages.py \
        --xml  xml_files/TrilinosPackageDependencies.xml \
        --outdir spack_repo/trilinos/packages
"""

from __future__ import annotations

import argparse
import os
import sys
import re


from parse_tribits_xml import parse_xml, TrilinosPackage

# Populated in main() after parsing — maps subpackage name → parent package name
# e.g. {"TeuchosCore": "Teuchos", "TpetraCore": "Tpetra", ...}
_SUBPKG_PARENT: dict[str, str] = {}


def _pkg_dep_spec(dep_name: str) -> tuple[str, str | None]:
    """Return (spack_package_name, variant_condition) for a package dep.

    If dep_name is a subpackage (e.g. TeuchosCore), returns:
        ("trilinos-teuchos", "+teuchoscore")

    If dep_name is a top-level generated package (e.g. Teuchos), returns:
        ("trilinos-teuchos", None)

    If dep_name is an external package (e.g. Kokkos), returns:
        ("kokkos", None)
    """
    if dep_name in EXTERNAL_PACKAGES:
        return EXTERNAL_PACKAGES[dep_name], None

    if dep_name in _SUBPKG_PARENT:
        parent = _SUBPKG_PARENT[dep_name]
        if parent in EXTERNAL_PACKAGES:
            # Subpackage of an external — just depend on the external
            return EXTERNAL_PACKAGES[parent], None
        return _spack_pkg_name(parent), f"+{_variant_name(dep_name)}"

    return _spack_pkg_name(dep_name), None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Magic markers for manual sections that survive regeneration
MANUAL_SECTION_BEGIN = "# BEGIN MANUAL SECTION"
MANUAL_SECTION_END = "# END MANUAL SECTION"
MANUAL_CMAKE_BEGIN = "# BEGIN MANUAL CMAKE ARGS"
MANUAL_CMAKE_END = "# END MANUAL CMAKE ARGS"

# Packages that already exist in Spack and should NOT get a generated package.py.
# Any Trilinos package that depends on one of these will use plain depends_on()
# (not depends_on_trilinos_package()) so Spack resolves it from its own repo.
#
# Key   = TriBITS package name (as it appears in the XML)
# Value = Spack package name to use in depends_on()
#
# To add more externals, just append to this dict.
EXTERNAL_PACKAGES: dict[str, str] = {
    "Kokkos":        "kokkos",
    "KokkosKernels": "kokkos-kernels",
    "SEACAS":        "seacas",
}

# Convenience set for fast membership tests
_EXTERNAL_NAMES: set[str] = set(EXTERNAL_PACKAGES.keys())

# Subpackage relationships that the XML doesn't declare via ParentPackage.
# Key   = subpackage TriBITS name
# Value = parent TriBITS package name
# These are injected into _SUBPKG_PARENT at startup alongside the XML-derived ones.
EXTRA_SUBPACKAGES: dict[str, str] = {}

# Variant names already declared as trilinos_variant() in TrilinosBaseClass.
# Generated packages must not re-declare these — the base class owns them.
# Update this set whenever trilinos_variant() calls are added to the base class.
BASE_TRILINOS_VARIANTS: set[str] = {
    "mpi",
    "openmp",
    "cuda",
    "fortran",
    "wrapper",
    "explicit-instantiation",
    "all-optional-packages",
    "tests",
    "double",
    "float",
    "complex-double",
    "complex-float",
}

# Scraped CMake options to exclude from generated packages.
# These are handled globally by the base class cmake_args.
# Key = package TriBITS name, Value = set of CMake variable names to exclude.
EXCLUDE_SCRAPED_OPTIONS: dict[str, set[str]] = {
    "Tpetra": {
        "Tpetra_INST_SERIAL",
        "Tpetra_INST_OPENMP",
        "Tpetra_INST_CUDA",
        "Tpetra_INST_HIP",
        "Tpetra_INST_SYCL",
        "Tpetra_INST_INT_INT",
        "Tpetra_INST_INT_LONG",
        "Tpetra_INST_INT_LONG_LONG",
        "Tpetra_INST_INT_UNSIGNED",
        "Tpetra_INST_INT_UNSIGNED_LONG",
        "Tpetra_INST_DOUBLE",
        "Tpetra_INST_FLOAT",
        "Tpetra_INST_COMPLEX_DOUBLE",
        "Tpetra_INST_COMPLEX_FLOAT",
        "Tpetra_INST_FLOAT128",
        "Tpetra_INST_DD_REAL",
        "Tpetra_INST_LONG_DOUBLE",
        "Tpetra_INST_QD_REAL",
        "Tpetra_INST_PTHREAD",
        "Tpetra_ASSUME_GPU_AWARE_MPI",
        "Tpetra_ASSUME_CUDA_AWARE_MPI",
    },
}

# Synchronization requirements for scalar variants.
# Key: The variant that triggers the requirement.
# Value: List of (type, target, requirement)
# Types: "internal" (conflicts in same package), "external" (depends_on other package)
SCALAR_SYNC_MAP: dict[str, list[tuple[str, str, str]]] = {
    "complex-double": [
        ("internal", "double", "conflict"),
        ("external", "trilinos-teuchos", "complex"),
    ],
    "complex-float": [
        ("internal", "float", "conflict"),
        ("external", "trilinos-teuchos", "complex"),
    ],
}

# TPL allowlist: only TPLs listed here get variants, depends_on, and cmake args.
# Any TriBITS TPL not in this dict is silently ignored.
# Key   = TriBITS TPL name (as it appears in the XML)
# Value = Spack package name to use in depends_on()
INCLUDE_TPLS: dict[str, str] = {
    "MPI":          "mpi",
    "BLAS":         "blas",
    "LAPACK":       "lapack",
    "Boost":        "boost",
    "HDF5":         "hdf5",
    "NetCDF":       "netcdf-c",
    "Netcdf":       "netcdf-c",
    "METIS":        "metis",
    "ParMETIS":     "parmetis",
    "Parmetis":     "parmetis",
    "Zlib":         "zlib-api",
    "ZLIB":         "zlib-api",
    "SuperLU":      "superlu",
    "SuperLUDist":  "superlu-dist",
    "SuperLU_Dist": "superlu-dist",
    "Scotch":       "scotch",
    "CDT":          "cdt",
    "OpenMP":       "llvm-openmp",
    "Gtest":        "googletest",
    "gtest":        "googletest",
    "CGNS":         "cgns",
    "Kokkos":       "kokkos",
    "KokkosKernels":"kokkos-kernels",
    "Python":       "python",
    "Pnetcdf":      "parallel-netcdf",
}

# Package exclusion list: optional package dependencies to skip when generating.
# Use this to exclude broken or incompatible optional dependencies.
# Format: set of TriBITS package names (as they appear in the XML)
EXCLUDE_OPTIONAL_PACKAGES: set[str] = {
    "ShyLU_Node",        # Disabled - header bugs in shylubasker_order_scotch.hpp (line 1225, 1254, 1259, 1283)
    "ShyLU_NodeBasker",  # Part of ShyLU_Node
    "ShyLU_NodeTacho",   # Part of ShyLU_Node
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dep_call(dep_name: str) -> str:
    """Return depends_on or depends_on_trilinos_package based on whether
    the dep (or its parent, if it's a subpackage) is an external."""
    effective = _SUBPKG_PARENT.get(dep_name, dep_name)
    if effective in EXTERNAL_PACKAGES:
        return "depends_on"
    return "depends_on_trilinos_package"


def _tpl_to_spack(tpl_name: str) -> str | None:
    """Map a TriBITS TPL name to its Spack package name.
    Returns None if the TPL is not in the INCLUDE_TPLS allowlist.
    """
    return INCLUDE_TPLS.get(tpl_name)


def _spack_pkg_name(tribits_name: str) -> str:
    """Return the Spack package name: trilinos-<lower>, underscores→hyphens."""
    return f"trilinos-{tribits_name.lower().replace('_', '-')}"


def _dir_name(tribits_name: str) -> str:
    """Return the output directory name: trilinos_<lower> (underscore)."""
    return f"trilinos_{tribits_name.lower()}"


def _variant_name(subpackage_name: str) -> str:
    """Convert a subpackage name to a valid Spack variant name.

    Rules: lowercase, hyphens allowed, underscores replaced with hyphens,
    no spaces.  e.g. 'TeuchosCore' -> 'teuchoscore',
                     'ShyLU_Node'  -> 'shylu-node'
    """
    return subpackage_name.lower().replace("_", "-")


def _cmake_var_to_spack_variant(var: str, pkg_name: str) -> str:
    """Convert a CMake variable name to a Spack variant name.

    1. Omit package name prefix if present.
    2. Omit "use" prefix if it is a distinct word (e.g. starts with "USE_").
    3. Remove all non-alphanumeric characters.
    4. Lowercase.
    """
    res = var
    # 1. Omit package name prefix
    if res.lower().startswith(pkg_name.lower()):
        res = res[len(pkg_name):].lstrip("_- ")

    # 2. Omit "use" prefix if it's a distinct word
    if res.lower().startswith("use") and len(res) > 3 and not res[3].isalnum():
        res = res[3:].lstrip("_- ")

    # 3. Omit "enable" prefix if it's a distinct word
    if res.lower().startswith("enable") and (len(res) == 6 or not res[6].isalnum()):
        res = res[6:].lstrip("_- ")

    # 4 & 5. Keep alphanumeric, underscores, and hyphens; replace underscores with hyphens; lowercase
    clean = "".join(c for c in res if c.isalnum() or c in "_-").lower().replace("_", "-")
    # Remove duplicate hyphens if any
    clean = re.sub(r'-+', '-', clean).strip('-')
    return clean if clean else "".join(c for c in var if c.isalnum() or c in "_-").lower().replace("_", "-")


def _scrape_cmake_options(pkg_name: str) -> dict[str, tuple[str, bool]]:
    """Scrape CMake option() calls from the package directory.

    Returns a mapping: cmake_var -> (description, default_value).
    """
    options = {}
    pkg_dir = f"/projects/Trilinos/packages/{pkg_name.lower()}"
    if not os.path.isdir(pkg_dir):
        return options

    # Pattern for option(VAR "DESC" DEFAULT) — word boundary prevents matching COMBINED_OPTION
    option_pat = re.compile(
        r'\boption\s*\(\s*([A-Za-z0-9_]+)\s*"([^"]*)"\s*([^)]*)\)',
        re.IGNORECASE | re.DOTALL
    )

    # Pattern for TRIBITS_ADD_OPTION_AND_DEFINE(VAR ...)
    tribits_pat = re.compile(
        r'TRIBITS_ADD_OPTION_AND_DEFINE\s*\(\s*([A-Za-z0-9_]+)[,\s]+(?:[^"]*"([^"]*)"\s*[,\s]+)?([^)]*)\)',
        re.IGNORECASE | re.DOTALL
    )

    # Pattern for COMBINED_OPTION(VAR DEP_OPTIONS_NAMES ... DOCSTR "desc")
    combined_pat = re.compile(
        r'COMBINED_OPTION\s*\(\s*([A-Za-z0-9_${}]+)\s+DEP_OPTIONS_NAMES\s+[^)]*?DOCSTR\s+"([^"]*(?:"\s*"[^"]*)*)"?\s*\)',
        re.IGNORECASE | re.DOTALL
    )

    for root, _, files in os.walk(pkg_dir):
        for file in files:
            if file.endswith(".cmake") or file == "CMakeLists.txt":
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()

                        for match in option_pat.finditer(content):
                            var, desc, default = match.group(1), match.group(2), match.group(3)
                            if desc:
                                desc = " ".join(desc.split())
                            default_val = default.strip().upper() == "ON"
                            options[var] = (desc or "", default_val)

                        for match in tribits_pat.finditer(content):
                            var, desc, default = match.group(1), match.group(2), match.group(3)
                            if desc:
                                desc = " ".join(desc.split())
                            default_val = default.strip().upper() == "ON"
                            options[var] = (desc or "", default_val)

                        for match in combined_pat.finditer(content):
                            var, raw_desc = match.group(1), match.group(2)
                            if "${" in var:
                                continue
                            desc = " ".join(raw_desc.replace('"', '').split())
                            options[var] = (desc, False)

                except Exception:
                    continue

    exclusions = EXCLUDE_SCRAPED_OPTIONS.get(pkg_name, set())
    if exclusions:
        options = {k: v for k, v in options.items() if k not in exclusions}

    return options


def _tpl_variant_name(tpl_name: str) -> str:
    """Convert a TriBITS TPL name to a Spack variant name for that TPL.

    e.g. 'MPI' -> 'mpi', 'yaml-cpp' -> 'yaml-cpp', 'CUBLAS' -> 'cublas'
    """
    return tpl_name.lower().replace("_", "-")


def _extract_manual_section(file_path: str, begin_marker: str, end_marker: str) -> str:
    """Extract content between begin and end markers from an existing file.

    Returns the content between markers (including the markers themselves),
    or an empty string with just markers if the file doesn't exist or markers not found.

    Handles markers with or without leading whitespace.
    """
    if not os.path.exists(file_path):
        # File doesn't exist yet - return empty manual section
        return f"    {begin_marker}\n    {end_marker}\n"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find lines containing the markers (handle any leading whitespace)
        begin_line_idx = None
        end_line_idx = None

        for i, line in enumerate(lines):
            if begin_marker in line:
                begin_line_idx = i
            if end_marker in line and begin_line_idx is not None:
                end_line_idx = i
                break

        if begin_line_idx is None or end_line_idx is None or begin_line_idx >= end_line_idx:
            # Markers not found or invalid - return empty manual section
            return f"    {begin_marker}\n    {end_marker}\n"

        # Extract lines from begin to end (inclusive)
        extracted_lines = lines[begin_line_idx:end_line_idx + 1]
        return ''.join(extracted_lines)

    except Exception:
        # If anything goes wrong, return empty manual section
        return f"    {begin_marker}\n    {end_marker}\n"


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def _header(pkg: TrilinosPackage, scraped_options: dict[str, tuple[str, bool]] = None) -> list[str]:
    """Render the package header: copyright, imports, class declaration, variants.

    homepage, url, git, and versions are defined in TrilinosBaseClass.
    """
    lines: list[str] = []
    # Spack derives the class name from the directory name by title-casing each
    # underscore-separated segment of the lowercased name.
    # e.g. trilinos_rol -> TrilinosRol, trilinos_shylu_dd -> TrilinosShyluDd
    class_name = "".join(
        w.title() for w in f"trilinos_{pkg.name.lower()}".split("_")
    )
    if class_name == "TrilinosZoltan2Core":
        class_name = "TrilinosZoltan2core"
    elif class_name == "TrilinosZoltan2Sphynx":
        class_name="TrilinosZoltan2sphynx"

    lines += [
        "# Copyright Spack Project Developers. See COPYRIGHT file for details.",
        "# Auto-generated by generate_spack_packages.py",
        "# Source: TrilinosPackageDependencies.xml",
        "",
        "import os",
        "import pathlib",
        "import re",
        "import sys",
        "from spack.package import *",
        "from ..trilinos_base_class.package import TrilinosBaseClass",
        "from ..trilinos_base_class.package import depends_on_trilinos_package",
        "from ..trilinos_base_class.package import trilinos_variant",
        "from ..trilinos_base_class.package import list_of_trilinos_variants",
        "",
        "",
        f"class {class_name}(TrilinosBaseClass):",
        f'    """Trilinos {pkg.name} package.',
        "",
        "    Part of the Trilinos Project (https://trilinos.github.io).",
        '    """',
        "",
    ]

    # One variant per subpackage — local only, not propagated across packages
    if pkg.subpackages:
        lines.append("    # Subpackage variants")
        for sp in pkg.subpackages:
            vname = _variant_name(sp)
            lines.append(
                f'    variant("{vname}", default=True,'
                f' description="Enable the {sp} subpackage")'
            )
        lines.append("")

    # One variant per optional TPL — package-local, plain variant().
    # Skip any whose variant name is already declared in TrilinosBaseClass.
    visible_opt_tpls = [
        tpl for tpl in pkg.optional_tpl_deps
        if _tpl_to_spack(tpl) is not None
        and _tpl_variant_name(tpl) not in BASE_TRILINOS_VARIANTS
    ]
    if visible_opt_tpls:
        lines.append("    # Optional TPL variants")
        for tpl in visible_opt_tpls:
            vname = _tpl_variant_name(tpl)
            spack_name = _tpl_to_spack(tpl)
            lines.append(
                f'    variant("{vname}", default=True,'
                f' description="Enable {spack_name} support")'
            )
        lines.append("")
        lines.append("")

    # One variant per optional package dependency — package-local, plain variant().
    # These control whether the optional dependency is pulled into the build.
    visible_opt_pkgs = []
    seen_opt_vnames = set()
    for dep in pkg.optional_package_deps:
        vname = _variant_name(dep)
        if vname not in BASE_TRILINOS_VARIANTS and vname not in seen_opt_vnames:
            visible_opt_pkgs.append((dep, vname))
            seen_opt_vnames.add(vname)

    if visible_opt_pkgs:
        lines.append("    # Optional package variants")
        for dep, vname in visible_opt_pkgs:
            lines.append(
                f'    variant("{vname}", default=True,'
                f' description="Enable {dep} support")'
            )
        lines.append("")
        lines.append("")

    # Scraped CMake options as variants
    if scraped_options:
        lines.append("    # Scraped CMake options")
        for var, (desc, default) in scraped_options.items():
            vname = _cmake_var_to_spack_variant(var, pkg.name)
            # Avoid redeclaring base variants
            if vname in BASE_TRILINOS_VARIANTS:
                continue
            lines.append(
                f'    variant("{vname}", default={default}, '
                f'description="{desc}")'
            )
        lines.append("")
        lines.append("")

    return lines


def _dep_call(dep_name: str) -> str:
    """Return depends_on or depends_on_trilinos_package for a package dep."""
    # Resolve through subpackage to its parent if needed
    effective = _SUBPKG_PARENT.get(dep_name, dep_name)
    if effective in EXTERNAL_PACKAGES:
        return "depends_on"
    return "depends_on_trilinos_package"


def _required_package_deps(pkg: TrilinosPackage) -> list[str]:
    """Render depends_on lines for required package dependencies, grouping
    multiple subpackage variant requirements for the same parent into one line.

        TeuchosCore + TeuchosComm → depends_on_trilinos_package("trilinos-teuchos +teuchoscore +teuchoscomm")
        Teuchos (bare, already covered above) → suppressed
        Kokkos → depends_on("kokkos")

    Also includes TEST_REQUIRED dependencies that are external packages, since
    TriBITS will auto-enable them when their Config files are found in CMAKE_PREFIX_PATH.
    """
    # Merge test-required external packages into required deps
    all_required = list(pkg.required_package_deps)
    for test_dep in pkg.test_required_package_deps:
        effective = _SUBPKG_PARENT.get(test_dep, test_dep)
        if effective in EXTERNAL_PACKAGES and test_dep not in all_required:
            all_required.append(test_dep)

    if not all_required:
        return []

    # Group variants by (fn, spack_name), preserving first-seen order
    from collections import defaultdict
    order: list[tuple[str, str]] = []           # ordered (fn, spack_name)
    seen_keys: set[tuple[str, str]] = set()
    variants: dict[tuple[str,str], list[str]] = defaultdict(list)
    bare_parents: set[str] = set()

    for dep in all_required:
        spack_name, variant = _pkg_dep_spec(dep)
        fn = _dep_call(dep)
        key = (fn, spack_name)
        if key not in seen_keys:
            seen_keys.add(key)
            order.append(key)
        if variant and variant not in variants[key]:
            variants[key].append(variant)
            bare_parents.add(spack_name)

    lines = ["    # Required package dependencies"]
    for fn, spack_name in order:
        # Suppress bare parent if subpkg deps already cover it
        if not variants[(fn, spack_name)] and spack_name in bare_parents:
            continue
        vparts = variants[(fn, spack_name)]
        spec = spack_name + ("".join(f" {v}" for v in vparts) if vparts else "")
        lines.append(f'    {fn}("{spec}")')

    lines.append("")
    return lines


def _optional_package_deps(pkg: TrilinosPackage, scraped_options: dict = None) -> list[str]:
    """Render depends_on lines for optional package dependencies, grouping
    multiple subpackage variants for the same parent+when into one line.

        TeuchosCore when=+tpetracore → depends_on_trilinos_package("trilinos-teuchos +teuchoscore", when="+tpetracore")
    """
    if not pkg.optional_package_deps and not scraped_options:
        return []

    from collections import defaultdict
    sp_variant_names: set[str] = {_variant_name(sp) for sp in pkg.subpackages}

    # Group by (fn, spack_name, control_variant) → [dep_variant, ...]
    order: list[tuple[str, str, str]] = []
    seen_keys: set[tuple] = set()
    variants: dict[tuple, list[str]] = defaultdict(list)
    bare_parents: set[str] = set()

    for dep in pkg.optional_package_deps:
        # Skip excluded packages
        effective = _SUBPKG_PARENT.get(dep, dep)
        if effective in EXCLUDE_OPTIONAL_PACKAGES or dep in EXCLUDE_OPTIONAL_PACKAGES:
            continue

        spack_name, dep_variant = _pkg_dep_spec(dep)
        fn = _dep_call(dep)
        vname = _variant_name(dep)

        # We use the control variant vname as the 'when' condition
        key = (fn, spack_name, vname)
        if key not in seen_keys:
            seen_keys.add(key)
            order.append(key)

        # The dependency itself might require a specific variant (e.g. +tpetracore)
        if dep_variant and dep_variant not in variants[key]:
            variants[key].append(dep_variant)
            bare_parents.add(spack_name)

    # Handle cross-package synchronized variants (from SCALAR_SYNC_MAP)
    # This adds depends_on requirements to other packages based on variants enabled in this one.
    for variant, requirements in SCALAR_SYNC_MAP.items():
        # We only add these if the current package actually uses this variant (scraped or subpackage)
        has_variant = any(_cmake_var_to_spack_variant(var, pkg.name) == variant
                          for var in (scraped_options or {})) or \
                      any(_variant_name(sp) == variant for sp in pkg.subpackages)

        if has_variant:
            for req_type, target, req_val in requirements:
                if req_type == "external":
                    # This is a cross-package dependency: depend on the target package with the req_val variant
                    fn = "depends_on_trilinos_package" if target.startswith("trilinos-") else "depends_on"
                    spec = f"{target} +{req_val}"
                    key = (fn, target, f"+{variant}")
                    if key not in seen_keys:
                        seen_keys.add(key)
                        order.append(key)
                        variants[key] = []

    lines = ["    # Optional package dependencies"]
    for fn, spack_name, when in order:
        vparts = variants[(fn, spack_name, when)]
        spec = spack_name + ("".join(f" {v}" for v in vparts) if vparts else "")
        # If 'when' starts with '+', it's a scalar sync variant; otherwise it's a control variant.
        # We use + prefix regardless.
        when_prefix = "" if when.startswith("+") else "+"
        lines.append(f'    {fn}("{spec}", when="{when_prefix}{when}")')

    lines.append("")
    return lines


def _required_tpl_deps(pkg: TrilinosPackage) -> list[str]:
    """Render depends_on(...) lines for required TPL dependencies."""
    if not pkg.required_tpl_deps:
        return []

    lines = ["    # Required external (TPL) dependencies"]
    for tpl in pkg.required_tpl_deps:
        spack_name = _tpl_to_spack(tpl)
        if spack_name is None:
            continue
        lines.append(f'    depends_on("{spack_name}")')
    lines.append("")
    return lines


def _optional_tpl_deps(pkg: TrilinosPackage) -> list[str]:
    """Render depends_on lines for optional TPL dependencies.

    Each optional TPL has a with-<tpl> variant.  The depends_on is gated only
    on that variant — subpackage constraints are expressed via conflicts() instead.

        depends_on("mpi", when="+with-mpi")
    """
    if not pkg.optional_tpl_deps:
        return []

    lines = ["    # Optional external (TPL) dependencies"]
    for tpl in pkg.optional_tpl_deps:
        spack_name = _tpl_to_spack(tpl)
        if spack_name is None:
            continue
        tpl_vname = _tpl_variant_name(tpl)
        lines.append(f'    depends_on("{spack_name}", when="+{tpl_vname}")')

    lines.append("")
    return lines


def _manual_section() -> list[str]:
    """Render the manual section placeholder between dependencies and cmake_args.

    This section allows hand-editing of dependencies, variants, or other class members
    that survive regeneration.
    """
    return [
        f"    {MANUAL_SECTION_BEGIN}",
        "    # Add custom dependencies, variants, or class methods here",
        "    # Examples:",
        "    #   depends_on(\"llvm\")",
        "    #   variant(\"custom\", default=False, description=\"Custom feature\")",
        f"    {MANUAL_SECTION_END}",
        "",
    ]


def _conflicts(pkg: TrilinosPackage) -> list[str]:
    """Render conflicts() lines enforcing that optional TPLs cannot be disabled
    when a subpackage that requires them is enabled.

    For each optional TPL introduced by specific subpackages:
        conflicts("~mpi", when="+teuchoscore")

    If the TPL was introduced at the top level (not by any subpackage), no
    conflict is needed — the TPL variant alone controls it.
    """
    if not pkg.optional_tpl_deps:
        return []

    sp_variant_names: set[str] = {_variant_name(sp) for sp in pkg.subpackages}

    lines = ["    # TPL conflicts: subpackages that require an optional TPL"]
    any_written = False
    for tpl in pkg.optional_tpl_deps:
        if _tpl_to_spack(tpl) is None:
            continue

        tpl_vname = _tpl_variant_name(tpl)
        sources: list[str] = pkg.optional_tpl_sources.get(tpl, [])
        sp_sources = [sp for sp in sources if _variant_name(sp) in sp_variant_names]
        non_sp_sources = [sp for sp in sources if _variant_name(sp) not in sp_variant_names]

        if not sp_sources or non_sp_sources:
            continue

        for sp in sp_sources:
            sp_vname = _variant_name(sp)
            lines.append(f'    conflicts("~{tpl_vname}", when="+{sp_vname}")')
            any_written = True

    if not any_written:
        return []

    lines.append("")
    return lines


def _footer(pkg: TrilinosPackage, scraped_options: dict[str, tuple[str, bool]] = None) -> list[str]:
    """Render cmake_args.

    Self:         Trilinos_ENABLE_<ThisPackage>=ON      (always, unconditional)
    Every dep:    TPL_ENABLE_<Name>=ON
      - Required deps go in the args=[...] list (unconditional)
      - Optional deps are appended conditionally
      - Externals (Kokkos, STK, SEACAS) and their subpackages are skipped —
        they are not Trilinos cmake knobs
      - For subpackage deps the cmake name is the subpackage itself
        e.g. TeuchosKokkosComm → TPL_ENABLE_TeuchosKokkosComm
      - Optional Trilinos package deps are gated on the subpackage variant(s)
        that introduced them
      - Optional TPL deps are gated on their with-<tpl> variant AND the
        subpackage variant(s) that introduced them
    """
    sp_variant_names: set[str] = {_variant_name(sp) for sp in pkg.subpackages}
    seen: set[str] = set()   # cmake names already emitted, for dedup

    def _pkg_cmake_name(dep: str) -> str:
        """Return the CMake enable name for a Trilinos package dep.

        Subpackages resolve to themselves (Trilinos_ENABLE_TeuchosCore).
        Top-level packages resolve to themselves (Trilinos_ENABLE_Kokkos).
        """
        return dep

    lines: list[str] = [
        "    def cmake_args(self):",
        "        args = super().cmake_args()",
        f'        args.append(self.define("Trilinos_ENABLE_{pkg.name}", True))',
        "",
    ]

    # ---- Subpackage enables — conditional on each subpackage variant ---------
    for sp in pkg.subpackages:
        vname = _variant_name(sp)
        lines += [
            f'        if self.spec.satisfies("+{vname}"):',
            f'            args.append(self.define("Trilinos_ENABLE_{sp}", True))',
            '',
        ]

    # ---- Required package deps — TPL_ENABLE_ only (all deps are external) -
    for dep in pkg.required_package_deps:
        cmake_name = _pkg_cmake_name(dep)
        if cmake_name not in seen:
            seen.add(cmake_name)
            # All dependencies (whether external like Kokkos or already-built Trilinos packages)
            # are treated as TPLs - only the current package gets Trilinos_ENABLE_
            lines.append(f'        args.append(self.define("TPL_ENABLE_{cmake_name}", True))')

    # ---- Test-required external package deps — TPL_ENABLE_ to prevent internal build ----
    # When test dependencies are external packages (Kokkos, KokkosKernels), TriBITS
    # auto-enables them when their Config files are found, even with tests disabled.
    # We must set TPL_ENABLE to treat them as external.
    for dep in pkg.test_required_package_deps:
        effective = _SUBPKG_PARENT.get(dep, dep)
        if effective in EXTERNAL_PACKAGES:
            cmake_name = _pkg_cmake_name(dep)
            if cmake_name not in seen:
                seen.add(cmake_name)
                lines.append(f'        args.append(self.define("TPL_ENABLE_{cmake_name}", True))')

    # ---- Required TPL deps — unconditional TPL_ENABLE_ --------------
    for tpl in pkg.required_tpl_deps:
        if _tpl_to_spack(tpl) is None:
            continue
        if tpl not in seen:
            seen.add(tpl)
            lines.append(f'        args.append(self.define("TPL_ENABLE_{tpl}", True))')

    lines.append("")

    # ---- Optional package deps — keyed on control variant ----------------
    for dep in pkg.optional_package_deps:
        # Skip excluded packages
        effective = _SUBPKG_PARENT.get(dep, dep)
        if effective in EXCLUDE_OPTIONAL_PACKAGES or dep in EXCLUDE_OPTIONAL_PACKAGES:
            continue

        cmake_name = _pkg_cmake_name(dep)
        if cmake_name in seen:
            continue

        vname = _variant_name(dep)
        seen.add(cmake_name)
        lines.append(
            f'        args.append(self.define_from_variant("TPL_ENABLE_{cmake_name}", "{vname}"))'
        )

    # ---- Optional TPL deps — conditional TPL_ENABLE_ ----------------
    for tpl in pkg.optional_tpl_deps:
        if _tpl_to_spack(tpl) is None:
            continue
        if tpl in seen:
            continue

        tpl_vname = _tpl_variant_name(tpl)
        seen.add(tpl)
        lines += [
            f'        if self.spec.satisfies("+{tpl_vname}"):',
            f'            args.append(self.define("TPL_ENABLE_{tpl}", True))',
            '',
        ]

    # ---- Scraped CMake options ----------------
    if scraped_options:
        lines.append("        # Scraped CMake options")
        for var, (_, _) in scraped_options.items():
            vname = _cmake_var_to_spack_variant(var, pkg.name)
            lines.append(f'        args.append(self.define_from_variant("{var}", "{vname}"))')
        lines.append("")

    lines += [
        "",
        f"        {MANUAL_CMAKE_BEGIN}",
        "        # Add custom CMake arguments here",
        f"        {MANUAL_CMAKE_END}",
        "",
        "        return args",
        "",
    ]
    return lines


def generate_package_py(pkg: TrilinosPackage, existing_file_path: str = None) -> str:
    """Assemble a complete package.py for one top-level Trilinos package.

    If existing_file_path is provided, extracts and preserves manual sections
    from the existing file.
    """
    scraped_options = _scrape_cmake_options(pkg.name)
    lines: list[str] = []
    lines += _header(pkg, scraped_options=scraped_options)
    lines += _required_package_deps(pkg)
    lines += _optional_package_deps(pkg, scraped_options=scraped_options)
    lines += _required_tpl_deps(pkg)
    lines += _optional_tpl_deps(pkg)

    # Insert manual section (either from existing file or fresh)
    if existing_file_path:
        manual_content = _extract_manual_section(
            existing_file_path, MANUAL_SECTION_BEGIN, MANUAL_SECTION_END
        )
        # Split by lines and add to lines list
        lines.extend(manual_content.rstrip('\n').split('\n'))
        # Always add blank line after manual section
        lines.append('')
    else:
        lines += _manual_section()

    lines += _conflicts(pkg)

    # For cmake_args, we need to preserve the manual CMAKE args section
    # This is handled inside _footer, but we need to pass the file path
    footer_lines = _footer(pkg, scraped_options=scraped_options)
    if existing_file_path:
        # Extract manual CMAKE args from existing file
        manual_cmake = _extract_manual_section(
            existing_file_path, MANUAL_CMAKE_BEGIN, MANUAL_CMAKE_END
        )
        # Replace the default manual CMAKE section in footer with preserved content
        footer_str = '\n'.join(footer_lines)
        default_cmake_section = f"        {MANUAL_CMAKE_BEGIN}\n        # Add custom CMake arguments here\n        {MANUAL_CMAKE_END}"
        footer_str = footer_str.replace(default_cmake_section, manual_cmake.rstrip('\n'))
        footer_lines = footer_str.split('\n')

    lines += footer_lines
    return "\n".join(lines)


def _remove_cyclic_optional_deps(packages: list) -> list:
    """Remove optional package deps that would create a cycle.

    Builds a graph of required deps only, then checks each optional dep
    to see if adding it would create a cycle. If so, drops it and warns.
    Uses the Spack package name (trilinos-foo) as node identity.
    """
    # Map spack name -> TrilinosPackage for packages we generate
    by_spack: dict[str, object] = {_spack_pkg_name(p.name): p for p in packages}

    def spack_name_of(tribits_dep: str) -> str | None:
        """Resolve a TriBITS dep name to the spack name of its top-level package."""
        effective = _SUBPKG_PARENT.get(tribits_dep, tribits_dep)
        if effective in _EXTERNAL_NAMES:
            return None  # external, not in our graph
        return _spack_pkg_name(effective)

    # Build required-only adjacency: spack_name -> set of spack_names
    req_graph: dict[str, set[str]] = {_spack_pkg_name(p.name): set() for p in packages}
    for p in packages:
        src = _spack_pkg_name(p.name)
        for dep in p.required_package_deps:
            dst = spack_name_of(dep)
            if dst and dst in req_graph:
                req_graph[src].add(dst)

    def has_path(graph: dict, start: str, target: str) -> bool:
        """Return True if there is a directed path from start to target."""
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(graph.get(node, set()))
        return False

    # For each package, check optional deps — drop any that would cycle
    for p in packages:
        src = _spack_pkg_name(p.name)
        keep_opt: list[str] = []
        for dep in p.optional_package_deps:
            dst = spack_name_of(dep)
            if dst is None or dst not in req_graph:
                keep_opt.append(dep)
                continue
            # Would adding src->dst create a cycle? Yes if dst can already reach src.
            if has_path(req_graph, dst, src):
                print(f"  [cycle] dropping {src} -> {dst} (optional dep creates cycle)")
                # Also remove from sources dict
                p.optional_package_sources.pop(dep, None)
            else:
                keep_opt.append(dep)
                # Add to graph so subsequent checks see it
                req_graph[src].add(dst)
        p.optional_package_deps[:] = keep_opt

    return packages


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate Spack package.py files from TrilinosPackageDependencies.xml"
    )
    parser.add_argument("--xml", required=True, metavar="FILE",
                        help="Path to TrilinosPackageDependencies.xml")
    parser.add_argument("--outdir", default="spack_repo/trilinos/packages",
                        metavar="DIR", help="Root output directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print package names without writing files")
    args = parser.parse_args()

    print(f"[*] Parsing {args.xml} ...")
    try:
        packages, subpkg_parent = parse_xml(args.xml, extra_subpackages=EXTRA_SUBPACKAGES)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    # Populate the global subpackage→parent map used by dep rendering
    _SUBPKG_PARENT.update(subpkg_parent)
    _SUBPKG_PARENT.update(EXTRA_SUBPACKAGES)

    # Filter out external packages – they already exist in Spack
    packages = [p for p in packages if p.name not in _EXTERNAL_NAMES]
    print(f"    {len(packages)} top-level packages to generate.")
    print(f"    Externals (skipped): {', '.join(sorted(_EXTERNAL_NAMES))}")

    # Remove optional deps that would create cycles
    packages = _remove_cyclic_optional_deps(packages)

    if args.dry_run:
        for p in packages:
            print(f"  {_spack_pkg_name(p.name)}  →  {_dir_name(p.name)}/package.py")
        return

    os.makedirs(args.outdir, exist_ok=True)
    for pkg in packages:
        pkg_dir = os.path.join(args.outdir, _dir_name(pkg.name))
        os.makedirs(pkg_dir, exist_ok=True)
        pkg_path = os.path.join(pkg_dir, "package.py")
        # Generate content BEFORE opening file for writing (to preserve manual sections)
        content = generate_package_py(pkg, existing_file_path=pkg_path)
        with open(pkg_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"  → {pkg_path}")

    print(f"\n[✓] Generated {len(packages)} package.py files in {args.outdir}/")


if __name__ == "__main__":
    main()
