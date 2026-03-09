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
    "STK":           "stk",
    "SEACAS":        "seacas",
}

# Convenience set for fast membership tests
_EXTERNAL_NAMES: set[str] = set(EXTERNAL_PACKAGES.keys())

# Subpackage relationships that the XML doesn't declare via ParentPackage.
# Key   = subpackage TriBITS name
# Value = parent TriBITS package name
# These are injected into _SUBPKG_PARENT at startup alongside the XML-derived ones.
EXTRA_SUBPACKAGES: dict[str, str] = {
    "Zoltan2Core":   "Zoltan2",
    "Zoltan2Sphynx": "Zoltan2",
}

# TPLs to skip entirely – no depends_on generated, no variants, nothing.
# Add any TPL here that has no Spack equivalent or should be ignored.
SKIP_TPLS: set[str] = {
    "QD",
    "ARPREC",
    "QT",
    "quadmath",
    "BinUtils",
    "Valgrind",
    "HWLOC",
    "Pthread",
    "DLlib",
    "PyTrilinos",
}

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
}

# TriBITS TPL name → Spack package name.
TPL_SPACK_MAP: dict[str, str] = {
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
    "SuperLUMT":    "superlu-mt",
    "HYPRE":        "hypre",
    "Hypre":        "hypre",
    "MUMPS":        "mumps",
    "Scotch":       "scotch",
    "TBB":          "intel-tbb",
    "CUDA":         "cuda",
    "CUBLAS":       "cuda",
    "CUSOLVER":     "cuda",
    "CUSPARSE":     "cuda",
    "ROCBLAS":      "rocblas",
    "ROCSOLVER":    "rocsolver",
    "ROCSPARSE":    "rocsparse",
    "Thrust":       "thrust",
    "OpenMP":       "llvm-openmp",
    "X11":          "libx11",
    "Eigen":        "eigen",
    "GLM":          "glm",
    "Gtest":        "googletest",
    "gtest":        "googletest",
    "CGNS":         "cgns",
    "Matio":        "matio",
    "Kokkos":       "kokkos",
    "KokkosKernels":"kokkos-kernels",
    "yaml-cpp":     "yaml-cpp",
    "yamlcpp":      "yaml-cpp",
    "Python":       "python",
    "PAPI":         "papi",
    "CAMAL":        "camal",
    "ADIOS2":       "adios2",
    "AmgX":         "amgx",
    "ArrayFireCPU": "arrayfire",
    "AWSSDK":       "aws-sdk-cpp",
    "Catalyst2":    "catalyst",
    "Cereal":       "cereal",
    "Cholmod":      "suite-sparse",
    "AMD":          "suite-sparse",
    "UMFPACK":      "suite-sparse",
    "Clp":          "clp",
    "DataWarp":     "datawarp",
    "ExodusII":     "exodusii",
    "Faodel":       "faodel",
    "GLPK":         "glpk",
    "Lemon":        "lemon",
    "MKL":          "intel-oneapi-mkl",
    "CSS_MKL":      "intel-oneapi-mkl",
    "PARDISO_MKL":  "intel-oneapi-mkl",
    "mlpack":       "mlpack",
    "mpi_advance":  "mpi-advance",
    "OpenNURBS":    "opennurbs",
    "PaToH":        "patoh",
    "PETSC":        "petsc",
    "Pnetcdf":      "parallel-netcdf",
    "PuLP":         "py-pulp",
    "QTHREAD":      "qthread",
    "STRUMPACK":    "strumpack",
    "ViennaCL":     "viennacl",
    "VTune":        "intel-oneapi-vtune",
    # No known Spack package
    "Avatar":       "none",
    "CDT":          "none",
    "Cusp":         "none",
    "ForUQTK":      "none",
    "MAGMASparse":  "none",   # magma exists but MAGMASparse is a distinct lib
    "MATLAB":       "none",
    "MATLABLib":    "none",
    "MF":           "none",
    "Nemesis":      "none",   # bundled in SEACAS/ExodusII
    "OVIS":         "none",
    "pebbl":        "none",
    "qpOASES":      "none",
    "SARMA":        "none",
    "TopoManager":  "none",
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

    Returns None if the TPL is in SKIP_TPLS, unmapped, or mapped to 'none'.
    """
    if tpl_name in SKIP_TPLS:
        return None
    spack_name = TPL_SPACK_MAP.get(tpl_name)
    if spack_name == "none":
        return None
    return spack_name


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


def _tpl_variant_name(tpl_name: str) -> str:
    """Convert a TriBITS TPL name to a Spack variant name for that TPL.

    e.g. 'MPI' -> 'mpi', 'yaml-cpp' -> 'yaml-cpp', 'CUBLAS' -> 'cublas'
    """
    return tpl_name.lower().replace("_", "-")


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def _header(pkg: TrilinosPackage) -> list[str]:
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
        if tpl not in SKIP_TPLS
        and _tpl_to_spack(tpl) is not None
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
    """
    if not pkg.required_package_deps:
        return []

    # Group variants by (fn, spack_name), preserving first-seen order
    from collections import defaultdict
    order: list[tuple[str, str]] = []           # ordered (fn, spack_name)
    seen_keys: set[tuple[str, str]] = set()
    variants: dict[tuple[str,str], list[str]] = defaultdict(list)
    bare_parents: set[str] = set()

    for dep in pkg.required_package_deps:
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


def _optional_package_deps(pkg: TrilinosPackage) -> list[str]:
    """Render depends_on lines for optional package dependencies, grouping
    multiple subpackage variants for the same parent+when into one line.

        TeuchosCore when=+tpetracore → depends_on_trilinos_package("trilinos-teuchos +teuchoscore", when="+tpetracore")
    """
    if not pkg.optional_package_deps:
        return []

    from collections import defaultdict
    sp_variant_names: set[str] = {_variant_name(sp) for sp in pkg.subpackages}

    # Group by (fn, spack_name, when_variant) → [variant, ...]
    order: list[tuple[str, str, str | None]] = []
    seen_keys: set[tuple] = set()
    variants: dict[tuple, list[str]] = defaultdict(list)
    bare_parents: set[str] = set()

    for dep in pkg.optional_package_deps:
        spack_name, variant = _pkg_dep_spec(dep)
        fn = _dep_call(dep)
        if variant:
            bare_parents.add(spack_name)

        sources: list[str] = pkg.optional_package_sources.get(dep, [])
        sp_sources = [sp for sp in sources if _variant_name(sp) in sp_variant_names]
        non_sp_sources = [sp for sp in sources if _variant_name(sp) not in sp_variant_names]

        whens: list[str | None] = (
            [None] if (not sp_sources or non_sp_sources)
            else [_variant_name(sp) for sp in sp_sources]
        )

        for when in whens:
            key = (fn, spack_name, when)
            if key not in seen_keys:
                seen_keys.add(key)
                order.append(key)
            if variant and variant not in variants[key]:
                variants[key].append(variant)

    lines = ["    # Optional package dependencies"]
    for fn, spack_name, when in order:
        if not variants[(fn, spack_name, when)] and spack_name in bare_parents:
            continue
        vparts = variants[(fn, spack_name, when)]
        spec = spack_name + ("".join(f" {v}" for v in vparts) if vparts else "")
        if when:
            lines.append(f'    {fn}("{spec}", when="+{when}")')
        else:
            lines.append(f'    {fn}("{spec}")')

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


def _conflicts(pkg: TrilinosPackage) -> list[str]:
    """Render conflicts() lines enforcing that optional TPLs cannot be disabled
    when a subpackage that requires them is enabled.

    For each optional TPL introduced by specific subpackages:
        conflicts("~with-mpi", when="+teuchoscore")
        conflicts("~with-mpi", when="+teuchoskokkoscomm")

    If the TPL was introduced at the top level (not by any subpackage), no
    conflict is needed — the TPL variant alone controls it.
    """
    if not pkg.optional_tpl_deps:
        return []

    sp_variant_names: set[str] = {_variant_name(sp) for sp in pkg.subpackages}

    lines = ["    # TPL conflicts: subpackages that require an optional TPL"]
    any_written = False
    for tpl in pkg.optional_tpl_deps:
        if tpl in SKIP_TPLS or _tpl_to_spack(tpl) is None:
            continue

        tpl_vname = _tpl_variant_name(tpl)
        sources: list[str] = pkg.optional_tpl_sources.get(tpl, [])
        sp_sources = [sp for sp in sources if _variant_name(sp) in sp_variant_names]
        non_sp_sources = [sp for sp in sources if _variant_name(sp) not in sp_variant_names]

        if not sp_sources or non_sp_sources:
            # Top-level dep — no subpackage conflict needed
            continue

        for sp in sp_sources:
            sp_vname = _variant_name(sp)
            lines.append(f'    conflicts("~{tpl_vname}", when="+{sp_vname}")')
            any_written = True

    if not any_written:
        return []

    lines.append("")
    return lines


def _footer(pkg: TrilinosPackage) -> list[str]:
    """Render cmake_args.

    Self:         Trilinos_ENABLE_<ThisPackage>=ON      (always, unconditional)
    Every dep:    TRILINOS_TPL_ENABLE_<Name>=ON
      - Required deps go in the args=[...] list (unconditional)
      - Optional deps are appended conditionally
      - Externals (Kokkos, STK, SEACAS) and their subpackages are skipped —
        they are not Trilinos cmake knobs
      - For subpackage deps the cmake name is the subpackage itself
        e.g. TeuchosKokkosComm → TRILINOS_TPL_ENABLE_TeuchosKokkosComm
      - Optional Trilinos package deps are gated on the subpackage variant(s)
        that introduced them
      - Optional TPL deps are gated on their with-<tpl> variant AND the
        subpackage variant(s) that introduced them
    """
    sp_variant_names: set[str] = {_variant_name(sp) for sp in pkg.subpackages}
    seen: set[str] = set()   # cmake names already emitted, for dedup

    def _is_external(dep: str) -> bool:
        """True if dep is an external package or a subpackage of one."""
        if dep in EXTERNAL_PACKAGES:
            return True
        parent = _SUBPKG_PARENT.get(dep)
        return parent in EXTERNAL_PACKAGES if parent else False

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

    # ---- Required package deps — unconditional TRILINOS_TPL_ENABLE_ ----------
    for dep in pkg.required_package_deps:
        if _is_external(dep):
            continue
        if dep not in seen:
            seen.add(dep)
            lines.append(f'        args.append(self.define("TRILINOS_TPL_ENABLE_{dep}", True))')

    # ---- Required TPL deps — unconditional TRILINOS_TPL_ENABLE_ --------------
    for tpl in pkg.required_tpl_deps:
        if tpl in SKIP_TPLS:
            continue
        if tpl not in seen:
            seen.add(tpl)
            lines.append(f'        args.append(self.define("TRILINOS_TPL_ENABLE_{tpl}", True))')

    lines.append("")

    # ---- Optional package deps — conditional TRILINOS_TPL_ENABLE_ ------------
    for dep in pkg.optional_package_deps:
        if _is_external(dep):
            continue
        if dep in seen:
            continue

        sources: list[str] = pkg.optional_package_sources.get(dep, [])
        sp_sources = [sp for sp in sources if _variant_name(sp) in sp_variant_names]
        non_sp_sources = [sp for sp in sources if _variant_name(sp) not in sp_variant_names]

        seen.add(dep)
        if not sp_sources or non_sp_sources:
            lines += [
                f'        args.append(self.define("TRILINOS_TPL_ENABLE_{dep}", True))',
                '',
            ]
        else:
            condition = " or ".join(
                f'self.spec.satisfies("+{_variant_name(sp)}")'
                for sp in sp_sources
            )
            lines += [
                f'        if {condition}:',
                f'            args.append(self.define("TRILINOS_TPL_ENABLE_{dep}", True))',
                '',
            ]

    # ---- Optional TPL deps — conditional TRILINOS_TPL_ENABLE_ ----------------
    for tpl in pkg.optional_tpl_deps:
        if tpl in SKIP_TPLS:
            continue
        if _tpl_to_spack(tpl) is None:
            continue
        if tpl in seen:
            continue

        tpl_vname = _tpl_variant_name(tpl)
        seen.add(tpl)
        lines += [
            f'        if self.spec.satisfies("+{tpl_vname}"):',
            f'            args.append(self.define("TRILINOS_TPL_ENABLE_{tpl}", True))',
            '',
        ]

    lines += [
        "        return args",
        "",
    ]
    return lines


def generate_package_py(pkg: TrilinosPackage) -> str:
    """Assemble a complete package.py for one top-level Trilinos package."""
    lines: list[str] = []
    lines += _header(pkg)
    lines += _required_package_deps(pkg)
    lines += _optional_package_deps(pkg)
    lines += _required_tpl_deps(pkg)
    lines += _optional_tpl_deps(pkg)
    lines += _conflicts(pkg)
    lines += _footer(pkg)
    return "\n".join(lines)


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

    if args.dry_run:
        for p in packages:
            print(f"  {_spack_pkg_name(p.name)}  →  {_dir_name(p.name)}/package.py")
        return

    os.makedirs(args.outdir, exist_ok=True)
    for pkg in packages:
        pkg_dir = os.path.join(args.outdir, _dir_name(pkg.name))
        os.makedirs(pkg_dir, exist_ok=True)
        pkg_path = os.path.join(pkg_dir, "package.py")
        with open(pkg_path, "w", encoding="utf-8") as fh:
            fh.write(generate_package_py(pkg))
        print(f"  → {pkg_path}")

    print(f"\n[✓] Generated {len(packages)} package.py files in {args.outdir}/")


if __name__ == "__main__":
    main()
