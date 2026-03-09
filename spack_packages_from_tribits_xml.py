#!/usr/bin/env python3
"""
spack_packages_from_tribits_xml.py

Reads a TriBITS-generated TrilinosPackageDependencies.xml file and produces
one Spack package.py per *top-level* Trilinos package.  Sub-packages (e.g.
TeuchosCore, TeuchosNumerics, …) are surfaced as boolean variants inside their
parent package rather than as separate Spack packages.

Usage
-----
    python spack_packages_from_tribits_xml.py \
        --xml  xml_files/TrilinosPackageDependencies.xml \
        --outdir spack_repo/trilinos/packages

Each generated package ends up in:
    <outdir>/trilinos-<lowercase-package-name>/package.py

XML schema assumed (TriBITS standard output)
--------------------------------------------
<PackageDependencies project="Trilinos">
  <Package
      name="Teuchos"
      dir="packages/teuchos"
      type="PT"
      parentPackage="">          <!-- empty  → top-level package  -->

    <LIB_REQUIRED_DEP_PACKAGES value=""/>
    <LIB_OPTIONAL_DEP_PACKAGES value="Sacado"/>
    <LIB_REQUIRED_DEP_TPLS     value=""/>
    <LIB_OPTIONAL_DEP_TPLS     value="MPI Boost"/>

    <Subpackages>
      <Subpackage name="TeuchosCore"/>
      <Subpackage name="TeuchosParameterList"/>
      …
    </Subpackages>
  </Package>

  <!-- sub-packages also appear as their own <Package> elements  -->
  <Package name="TeuchosCore" parentPackage="Teuchos" …>
    …
  </Package>
  …
</PackageDependencies>

Logic
-----
* Sub-package detection uses a TWO-PASS strategy:
    Pass 1 – collect every name that appears inside any <Subpackage> element
             OR has a non-empty parentPackage attribute.
    Pass 2 – a package is top-level only if its name does NOT appear in that
             sub-package name set.
  This correctly handles cases where parentPackage="" even for sub-packages,
  which occurs in some TriBITS XML variants.

* Packages in SKIP_PACKAGES are excluded entirely (no package.py generated,
  and they are omitted from dependency lists).  SEACAS is treated as an
  external Spack package, so it belongs here.

* All generated Spack package names are prefixed with "trilinos-", e.g.
  Teuchos → trilinos-teuchos, Epetra → trilinos-epetra, etc.
  The Python class name remains un-prefixed CamelCase (e.g. class Teuchos).

* For each top-level package:
    - One variant per sub-package (default=True).
    - depends_on() for every required Trilinos dependency (unconditional).
    - depends_on() for every optional Trilinos dependency (when="+<dep>").
    - depends_on() for TPLs (required unconditional, optional when="+<tpl>")
      using a simple mapping of TriBITS TPL names → Spack package names.
    - Sub-package intra-deps are merged so that enabling a sub-package that
      needs another sub-package of the *same* parent forces the dependency.
"""

import argparse
import os
import re
import sys
import textwrap
from collections import defaultdict
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# Packages to skip entirely – not generated as Spack packages and removed
# from all dependency lists.  SEACAS is handled as an external Spack package.
# Add any other packages that should be treated as external here.
# ---------------------------------------------------------------------------
SKIP_PACKAGES: set[str] = {
    "SEACAS",
    "Seacas",
}

# ---------------------------------------------------------------------------
# TPL name mapping: TriBITS name → Spack package name
# Add / adjust entries as needed for your environment.
# ---------------------------------------------------------------------------
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
    "HYPRE":        "hypre",
    "Hypre":        "hypre",
    "MUMPS":        "mumps",
    "Scotch":       "scotch",
    "ParMETIS":     "parmetis",
    "TBB":          "intel-tbb",
    "CUDA":         "cuda",
    "OpenMP":       "llvm-openmp",   # virtual in most spack envs
    "Pthread":      None,            # handled by compiler / OS – skip
    "DLlib":        None,
    "X11":          "libx11",
    "Eigen":        "eigen",
    "GLM":          "glm",
    "Gtest":        "googletest",
    "CGNS":         "cgns",
    "Matio":        "matio",
    "SEACAS":       None,            # internal trilinos – skip as TPL
    "Kokkos":       "kokkos",        # can be external
    "KokkosKernels":"kokkos-kernels",
    "yaml-cpp":     "yaml-cpp",
    "Python":       "python",
    "PyTrilinos":   None,
}

# TPLs that map to virtual packages (Spack "virtual dependency" style)
TPL_VIRTUAL: set[str] = {"MPI", "BLAS", "LAPACK"}

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _split_value(value: str) -> list[str]:
    """Split a space/comma-separated XML attribute value into a clean list."""
    if not value:
        return []
    return [v.strip() for v in re.split(r"[\s,]+", value.strip()) if v.strip()]


def _to_spack_name(tribits_name: str) -> str:
    """Convert a CamelCase Trilinos package name to a 'trilinos-<lower>' spack name.

    E.g. "Teuchos" → "trilinos-teuchos", "EpetraExt" → "trilinos-epetraext".
    Packages in SKIP_PACKAGES should not be passed here; callers must filter first.
    """
    return f"trilinos-{tribits_name.lower()}"


def _spack_variant_name(pkg_name: str) -> str:
    """Return the variant name to use for a given package / subpackage."""
    return pkg_name.lower()


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class PackageInfo:
    """Parsed information for one TriBITS package (top-level or sub-package)."""

    def __init__(self):
        self.name: str = ""
        self.dir: str = ""
        self.pkg_type: str = "PT"       # PT / ST / EX
        self.parent: str = ""           # empty → top-level
        self.subpackages: list[str] = []

        # Intra-Trilinos deps
        self.lib_req_pkgs:  list[str] = []
        self.lib_opt_pkgs:  list[str] = []
        self.test_req_pkgs: list[str] = []
        self.test_opt_pkgs: list[str] = []

        # External TPL deps
        self.lib_req_tpls:  list[str] = []
        self.lib_opt_tpls:  list[str] = []
        self.test_req_tpls: list[str] = []
        self.test_opt_tpls: list[str] = []

    @property
    def is_subpackage(self) -> bool:
        # NOTE: authoritative sub-package detection is done in parse_xml()
        # via two-pass analysis.  This flag is set there.
        return bool(self.parent)

    @property
    def spack_name(self) -> str:
        return _to_spack_name(self.name)


# ---------------------------------------------------------------------------
# XML parser
# ---------------------------------------------------------------------------

def parse_xml(xml_path: str) -> dict[str, PackageInfo]:
    """Parse TrilinosPackageDependencies.xml → dict[name → PackageInfo].

    Uses a TWO-PASS strategy to robustly identify sub-packages:
      Pass 1 – collect every package name listed inside a <Subpackage> element
               OR that has a non-empty parentPackage attribute.
      Pass 2 – build PackageInfo objects; mark a package as a sub-package if
               its name appears in the set collected in Pass 1, regardless of
               whether its own parentPackage attribute is empty.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # ------------------------------------------------------------------
    # Pass 1: build the authoritative set of all sub-package names and
    # build a parentPackage map for those that declare it explicitly.
    # ------------------------------------------------------------------
    subpackage_names: set[str] = set()        # every known sub-pkg name
    explicit_parent: dict[str, str] = {}      # name → declared parentPackage

    for pkg_el in root.findall("Package"):
        pkg_name = pkg_el.get("name", "").strip()
        parent   = pkg_el.get("parentPackage", "").strip()

        if parent:
            subpackage_names.add(pkg_name)
            explicit_parent[pkg_name] = parent

        # Any name listed under <Subpackages><Subpackage name="…"/> is a sub-pkg
        subpkgs_el = pkg_el.find("Subpackages")
        if subpkgs_el is not None:
            for sp_el in subpkgs_el.findall("Subpackage"):
                sp_name = sp_el.get("name", "").strip()
                if sp_name:
                    subpackage_names.add(sp_name)
                    if sp_name not in explicit_parent:
                        explicit_parent[sp_name] = pkg_name

    # ------------------------------------------------------------------
    # Pass 2: build full PackageInfo objects.
    # ------------------------------------------------------------------
    packages: dict[str, PackageInfo] = {}

    for pkg_el in root.findall("Package"):
        info = PackageInfo()
        info.name     = pkg_el.get("name", "").strip()
        info.dir      = pkg_el.get("dir", "")
        info.pkg_type = pkg_el.get("type", "PT")

        # Use the authoritative parent map, not the raw attribute (which may be "")
        info.parent = explicit_parent.get(info.name, "")

        def _get_list(tag: str) -> list[str]:
            el = pkg_el.find(tag)
            if el is None:
                return []
            return _split_value(el.get("value", ""))

        info.lib_req_pkgs  = _get_list("LIB_REQUIRED_DEP_PACKAGES")
        info.lib_opt_pkgs  = _get_list("LIB_OPTIONAL_DEP_PACKAGES")
        info.test_req_pkgs = _get_list("TEST_REQUIRED_DEP_PACKAGES")
        info.test_opt_pkgs = _get_list("TEST_OPTIONAL_DEP_PACKAGES")

        info.lib_req_tpls  = _get_list("LIB_REQUIRED_DEP_TPLS")
        info.lib_opt_tpls  = _get_list("LIB_OPTIONAL_DEP_TPLS")
        info.test_req_tpls = _get_list("TEST_REQUIRED_DEP_TPLS")
        info.test_opt_tpls = _get_list("TEST_OPTIONAL_DEP_TPLS")

        # Subpackages listed inside <Subpackages>
        subpkgs_el = pkg_el.find("Subpackages")
        if subpkgs_el is not None:
            for sp_el in subpkgs_el.findall("Subpackage"):
                sp_name = sp_el.get("name", "").strip()
                if sp_name:
                    info.subpackages.append(sp_name)

        if info.name:
            packages[info.name] = info

    return packages


# ---------------------------------------------------------------------------
# Aggregation: build per-top-level-package view
# ---------------------------------------------------------------------------

class TopLevelPackage:
    """Aggregated view of a top-level Trilinos package for code generation."""

    def __init__(self, info: PackageInfo, all_packages: dict[str, PackageInfo]):
        self.info = info
        self.name = info.name
        self.spack_name = info.spack_name
        self.subpackages: list[PackageInfo] = []

        # Collect subpackage PackageInfo objects (in declaration order)
        for sp_name in info.subpackages:
            if sp_name in all_packages:
                self.subpackages.append(all_packages[sp_name])

        # Also pick up any sub-packages that list this as their parent
        # but weren't in the <Subpackages> list (defensive)
        listed = {sp.name for sp in self.subpackages}
        for pkg in all_packages.values():
            if pkg.parent == self.name and pkg.name not in listed:
                self.subpackages.append(pkg)

        self._all_packages = all_packages
        self._top_level_names = {
            p.name for p in all_packages.values() if not p.is_subpackage
        }

    # ------------------------------------------------------------------
    # Dependency aggregation helpers
    # ------------------------------------------------------------------

    def _resolve_top_level(self, pkg_name: str) -> str | None:
        """Return the top-level parent name for pkg_name (or itself if top-level)."""
        if pkg_name not in self._all_packages:
            return None
        info = self._all_packages[pkg_name]
        if not info.is_subpackage:
            return pkg_name
        # parent should be top-level; if not recurse (handles depth > 1)
        return self._resolve_top_level(info.parent)

    @property
    def _all_sub_info(self) -> list[PackageInfo]:
        """The top-level package itself plus all its subpackages."""
        return [self.info] + self.subpackages

    def _aggregate_pkgs(self, attr: str) -> list[str]:
        """Aggregate a dep-list attribute across the top-level + sub-packages,
        resolving to top-level names, deduplicating, excluding self and
        any packages in SKIP_PACKAGES."""
        seen: set[str] = set()
        result: list[str] = []
        for info in self._all_sub_info:
            for dep in getattr(info, attr):
                if dep in SKIP_PACKAGES:
                    continue
                top = self._resolve_top_level(dep)
                if top and top != self.name and top not in seen and top not in SKIP_PACKAGES:
                    seen.add(top)
                    result.append(top)
        return result

    def _aggregate_tpls(self, attr: str) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for info in self._all_sub_info:
            for tpl in getattr(info, attr):
                if tpl not in seen:
                    seen.add(tpl)
                    result.append(tpl)
        return result

    # Public aggregated dep lists (top-level Trilinos packages only)
    @property
    def required_trilinos_deps(self) -> list[str]:
        return self._aggregate_pkgs("lib_req_pkgs")

    @property
    def optional_trilinos_deps(self) -> list[str]:
        # Exclude anything already in required
        req = set(self.required_trilinos_deps)
        return [d for d in self._aggregate_pkgs("lib_opt_pkgs") if d not in req]

    @property
    def required_tpls(self) -> list[str]:
        return self._aggregate_tpls("lib_req_tpls")

    @property
    def optional_tpls(self) -> list[str]:
        req = set(self.required_tpls)
        return [t for t in self._aggregate_tpls("lib_opt_tpls") if t not in req]

    # Sub-package intra-deps: for each subpackage, which OTHER subpackages of
    # the SAME parent does it require?
    def subpkg_intra_deps(self) -> dict[str, list[str]]:
        """Map sub-package name → list of sibling sub-package names it needs."""
        sibling_names = {sp.name for sp in self.subpackages}
        result: dict[str, list[str]] = {}
        for sp in self.subpackages:
            deps = []
            for dep in sp.lib_req_pkgs + sp.lib_opt_pkgs:
                if dep in sibling_names and dep != sp.name:
                    deps.append(dep)
            result[sp.name] = deps
        return result


# ---------------------------------------------------------------------------
# Code generator
# ---------------------------------------------------------------------------

# Known Trilinos homepage URL pattern per package (best-effort)
TRILINOS_HOME = "https://trilinos.github.io"
TRILINOS_URL_TEMPLATE = (
    "https://github.com/trilinos/Trilinos/archive/trilinos-release-{version}.tar.gz"
)

# Representative versions – add more as needed
TRILINOS_VERSIONS = [
    ("16.4.0", "placeholder_sha256_16_4_0"),
    ("16.0.0", "placeholder_sha256_16_0_0"),
    ("15.1.1", "placeholder_sha256_15_1_1"),
    ("14.4.0", "placeholder_sha256_14_4_0"),
]


def _indent(text: str, spaces: int = 4) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in text.splitlines())


def _tpl_to_spack(tpl_name: str) -> str | None:
    """Map TriBITS TPL name to a Spack package name.  Returns None to skip."""
    return TPL_SPACK_MAP.get(tpl_name, tpl_name.lower())


def generate_package_py(top: TopLevelPackage) -> str:
    """Render a complete Spack package.py for a top-level Trilinos package."""
    pkg_class = top.name  # e.g. "Teuchos"
    pkg_spack = top.spack_name  # e.g. "teuchos"

    lines: list[str] = []

    # ------------------------------------------------------------------ header
    lines.append(f'# Copyright Spack Project Developers. See COPYRIGHT file for details.')
    lines.append(f'# Auto-generated by spack_packages_from_tribits_xml.py')
    lines.append(f'# Source: TrilinosPackageDependencies.xml')
    lines.append('')
    lines.append('from spack.package import *')
    lines.append('')
    lines.append('')
    lines.append(f'class {pkg_class}(CMakePackage):')
    lines.append(f'    """Trilinos {pkg_class} package.')
    lines.append('')
    lines.append(f'    Part of the Trilinos Project (https://trilinos.github.io).')
    lines.append(f'    See individual sub-packages for detailed descriptions.')
    lines.append(f'    """')
    lines.append('')
    lines.append(f'    homepage = "{TRILINOS_HOME}"')
    lines.append(f'    url = (')
    lines.append(f'        "https://github.com/trilinos/Trilinos/archive/"')
    lines.append(f'        "trilinos-release-{{0}}.tar.gz"')
    lines.append(f'    )')
    lines.append(f'    git = "https://github.com/trilinos/Trilinos.git"')
    lines.append('')

    # versions
    for ver, sha in TRILINOS_VERSIONS:
        dash_ver = ver.replace('.', '-')
        lines.append(
            f'    version("{ver}", sha256="{sha}",'
            f' url="https://github.com/trilinos/Trilinos/archive/'
            f'trilinos-release-{dash_ver}.tar.gz")'
        )
    lines.append('    version("develop", branch="develop")')
    lines.append('')

    # ---------------------------------------------------------------- variants
    # Sub-package variants
    if top.subpackages:
        lines.append('    # --- Sub-package variants ---')
        intra = top.subpkg_intra_deps()
        for sp in top.subpackages:
            vname = _spack_variant_name(sp.name)
            lines.append(
                f'    variant("{vname}", default=True,'
                f' description="Enable the {sp.name} sub-package")'
            )
        lines.append('')

    # Optional Trilinos-package variants (so downstream can condition on them)
    opt_deps = top.optional_trilinos_deps
    if opt_deps:
        lines.append('    # --- Optional intra-Trilinos feature variants ---')
        for dep in opt_deps:
            vname = _spack_variant_name(dep)
            lines.append(
                f'    variant("{vname}", default=False,'
                f' description="Enable optional {dep} support")'
            )
        lines.append('')

    # Optional TPL variants
    opt_tpls = top.optional_tpls
    if opt_tpls:
        lines.append('    # --- Optional TPL variants ---')
        for tpl in opt_tpls:
            spack_tpl = _tpl_to_spack(tpl)
            if spack_tpl is None:
                continue
            vname = _spack_variant_name(tpl)
            lines.append(
                f'    variant("{vname}", default=False,'
                f' description="Enable {tpl} support")'
            )
        lines.append('')

    # ---------------------------------------------------------------- depends_on
    lines.append('    # --- Trilinos as the build source (meta-package pattern) ---')
    lines.append('    depends_on("trilinos@develop", when="@develop")')
    for ver, _ in TRILINOS_VERSIONS:
        lines.append(f'    depends_on("trilinos@{ver}", when="@{ver}")')
    lines.append('')

    # Required intra-Trilinos deps
    req_deps = top.required_trilinos_deps
    if req_deps:
        lines.append('    # --- Required Trilinos package dependencies ---')
        for dep in req_deps:
            lines.append(f'    depends_on_trilinos_package("{_to_spack_name(dep)}")')
        lines.append('')

    # Optional intra-Trilinos deps
    if opt_deps:
        lines.append('    # --- Optional Trilinos package dependencies ---')
        for dep in opt_deps:
            vname = _spack_variant_name(dep)
            lines.append(
                f'    depends_on_trilinos_package("{_to_spack_name(dep)}", when="+{vname}")'
            )
        lines.append('')

    # Required TPL deps
    req_tpls = top.required_tpls
    if req_tpls:
        lines.append('    # --- Required external (TPL) dependencies ---')
        for tpl in req_tpls:
            spack_tpl = _tpl_to_spack(tpl)
            if spack_tpl is None:
                continue
            if tpl in TPL_VIRTUAL:
                lines.append(f'    depends_on("{spack_tpl}")')
            else:
                lines.append(f'    depends_on("{spack_tpl}")')
        lines.append('')

    # Optional TPL deps
    if opt_tpls:
        lines.append('    # --- Optional external (TPL) dependencies ---')
        for tpl in opt_tpls:
            spack_tpl = _tpl_to_spack(tpl)
            if spack_tpl is None:
                continue
            vname = _spack_variant_name(tpl)
            lines.append(
                f'    depends_on("{spack_tpl}", when="+{vname}")'
            )
        lines.append('')

    # Sub-package intra-deps: conflicts / conditional variant enables
    intra = top.subpkg_intra_deps()
    intra_lines = []
    for sp_name, sibling_deps in intra.items():
        for sdep in sibling_deps:
            vname_sp   = _spack_variant_name(sp_name)
            vname_sdep = _spack_variant_name(sdep)
            intra_lines.append(
                f'    # {sp_name} requires sibling {sdep}'
            )
            intra_lines.append(
                f'    conflicts("+{vname_sp}", when="~{vname_sdep}",'
                f' msg="{sp_name} requires {sdep}")'
            )
    if intra_lines:
        lines.append('    # --- Sub-package intra-dependency constraints ---')
        lines.extend(intra_lines)
        lines.append('')

    # ---------------------------------------------------------------- cmake args
    lines.append('    def cmake_args(self):')
    lines.append('        spec = self.spec')
    lines.append('        args = [')
    lines.append(f'            self.define("Trilinos_ENABLE_{top.name}", True),')

    # Enable / disable sub-packages based on variants
    if top.subpackages:
        lines.append('')
        lines.append('            # Sub-package enables')
        for sp in top.subpackages:
            vname = _spack_variant_name(sp.name)
            lines.append(
                f'            self.define_from_variant("Trilinos_ENABLE_{sp.name}", "{vname}"),'
            )

    # Optional Trilinos deps
    if opt_deps:
        lines.append('')
        lines.append('            # Optional intra-Trilinos package enables')
        for dep in opt_deps:
            vname = _spack_variant_name(dep)
            lines.append(
                f'            self.define_from_variant("Trilinos_ENABLE_{dep}", "{vname}"),'
            )

    # TPL enables
    all_tpls = [(t, True) for t in req_tpls] + [(t, False) for t in opt_tpls]
    if all_tpls:
        lines.append('')
        lines.append('            # TPL enables')
        for tpl, required in all_tpls:
            spack_tpl = _tpl_to_spack(tpl)
            if spack_tpl is None:
                continue
            if required:
                lines.append(
                    f'            self.define("TPL_ENABLE_{tpl}", True),'
                )
            else:
                vname = _spack_variant_name(tpl)
                lines.append(
                    f'            self.define_from_variant("TPL_ENABLE_{tpl}", "{vname}"),'
                )

    lines.append('        ]')
    lines.append('        return args')
    lines.append('')

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate Spack package.py files from TrilinosPackageDependencies.xml"
    )
    parser.add_argument(
        "--xml",
        required=True,
        metavar="FILE",
        help="Path to TrilinosPackageDependencies.xml (TriBITS-generated)",
    )
    parser.add_argument(
        "--outdir",
        default="spack_repo/trilinos/packages",
        metavar="DIR",
        help="Root output directory (default: spack_repo/trilinos/packages)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print package names that would be generated without writing files",
    )
    args = parser.parse_args()

    # Parse XML
    print(f"[*] Parsing {args.xml} …")
    try:
        all_packages = parse_xml(args.xml)
    except Exception as exc:
        print(f"[ERROR] Failed to parse XML: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"    Found {len(all_packages)} package entries total.")

    # Separate top-level from sub-packages; exclude SKIP_PACKAGES entirely
    top_level = {
        name: info
        for name, info in all_packages.items()
        if not info.is_subpackage and name not in SKIP_PACKAGES
    }
    skipped = [name for name in all_packages if name in SKIP_PACKAGES]
    sub_count = len(all_packages) - len(top_level) - len(skipped)
    print(f"    {len(top_level)} top-level packages, {sub_count} sub-packages.")
    if skipped:
        print(f"    Skipped (external): {', '.join(sorted(skipped))}")

    if args.dry_run:
        print("\n[DRY RUN] Would generate packages:")
        for name in sorted(top_level):
            print(f"  {name}")
        return

    # Generate output
    os.makedirs(args.outdir, exist_ok=True)
    generated = 0
    for name in sorted(top_level):
        info = top_level[name]
        top = TopLevelPackage(info, all_packages)

        pkg_dir = os.path.join(args.outdir, top.spack_name.replace("-", "_"))  # e.g. trilinos_teuchos
        os.makedirs(pkg_dir, exist_ok=True)

        pkg_path = os.path.join(pkg_dir, "package.py")
        content = generate_package_py(top)

        with open(pkg_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        sub_names = [sp.name for sp in top.subpackages]
        sub_str = f" ({len(sub_names)} sub-pkgs: {', '.join(sub_names[:3])}{'…' if len(sub_names) > 3 else ''})" if sub_names else ""
        print(f"  → {pkg_path}{sub_str}")
        generated += 1

    print(f"\n[✓] Generated {generated} package.py files in {args.outdir}/")


if __name__ == "__main__":
    main()
