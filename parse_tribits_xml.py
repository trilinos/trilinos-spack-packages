#!/usr/bin/env python3
"""
parse_tribits_xml.py

Parses a TriBITS TrilinosPackageDependencies.xml file and builds a list of
TrilinosPackage objects representing only top-level packages.

Each TrilinosPackage contains:
  - name                   : str
  - required_tpl_deps      : list[str]   external TPLs this package requires
  - optional_tpl_deps      : list[str]   external TPLs this package can use
  - required_package_deps  : list[str]   other top-level Trilinos packages required
  - optional_package_deps  : list[str]   other top-level Trilinos packages optional
  - subpackages            : list[str]   sub-package names (variants, not separate packages)

Sub-package detection uses two passes so that sub-packages whose
parentPackage attribute is incorrectly empty are still caught via
the <Subpackages> lists on their parent.

All dependencies that are sub-packages are resolved to their top-level
parent before being stored.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET
import re


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class TrilinosPackage:
    name: str
    subpackages:              list[str] = field(default_factory=list)
    required_tpl_deps:        list[str] = field(default_factory=list)
    optional_tpl_deps:        list[str] = field(default_factory=list)
    # Maps optional TPL name → list of subpackage names that introduced it.
    optional_tpl_sources:     dict[str, list[str]] = field(default_factory=dict)
    required_package_deps:    list[str] = field(default_factory=list)
    optional_package_deps:    list[str] = field(default_factory=list)
    # Maps optional package dep name → list of subpackage names that introduced it.
    optional_package_sources: dict[str, list[str]] = field(default_factory=dict)

    def __repr__(self) -> str:
        lines = [f"TrilinosPackage({self.name!r})"]
        if self.subpackages:
            lines.append(f"  subpackages:              {self.subpackages}")
        if self.required_package_deps:
            lines.append(f"  required_package_deps:    {self.required_package_deps}")
        if self.optional_package_deps:
            lines.append(f"  optional_package_deps:    {self.optional_package_deps}")
        if self.optional_package_sources:
            lines.append(f"  optional_package_sources: {self.optional_package_sources}")
        if self.required_tpl_deps:
            lines.append(f"  required_tpl_deps:        {self.required_tpl_deps}")
        if self.optional_tpl_deps:
            lines.append(f"  optional_tpl_deps:        {self.optional_tpl_deps}")
        if self.optional_tpl_sources:
            lines.append(f"  optional_tpl_sources:     {self.optional_tpl_sources}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split(value: str) -> list[str]:
    """Split a space/comma-separated XML attribute value into a clean list."""
    if not value:
        return []
    return [v for v in re.split(r"[\s,]+", value.strip()) if v]


# ---------------------------------------------------------------------------
# Raw intermediate structure (one per XML <Package> element)
# ---------------------------------------------------------------------------

@dataclass
class _RawPackage:
    name: str
    parent: str                        # empty string if top-level (or unknown)
    subpackage_names: list[str]        # names declared in <Subpackages>
    lib_req_pkgs:  list[str]
    lib_opt_pkgs:  list[str]
    lib_req_tpls:  list[str]
    lib_opt_tpls:  list[str]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_xml(xml_path: str, extra_subpackages: dict | None = None) -> tuple:
    """
    Parse TrilinosPackageDependencies.xml and return a list of TrilinosPackage
    objects, one per top-level Trilinos package.

    extra_subpackages: optional {subpkg_name: parent_name} for relationships
    not declared in the XML via ParentPackage (e.g. Zoltan2Core -> Zoltan2).
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # ------------------------------------------------------------------
    # Pass 1: read every <Package> element into a _RawPackage.
    #         Simultaneously build the authoritative sub-package name set
    #         from <Subpackage> elements (more reliable than parentPackage="").
    # ------------------------------------------------------------------
    raw: dict[str, _RawPackage] = {}
    all_subpackage_names: set[str] = set()   # every name that is a sub-pkg
    parent_of: dict[str, str] = {}           # subpkg name -> parent name

    for el in root.findall("Package"):
        name = el.get("name", "").strip()
        if not name:
            continue

        # ParentPackage may be an XML attribute OR a child element <ParentPackage value="..."/>
        parent = el.get("parentPackage", "").strip()
        parent_el = el.find("ParentPackage")
        if parent_el is not None:
            parent = parent_el.get("value", "").strip()

        # Collect sub-package names declared on this element (older XML schema)
        subpkg_names: list[str] = []
        subpkgs_el = el.find("Subpackages")
        if subpkgs_el is not None:
            for sp in subpkgs_el.findall("Subpackage"):
                sp_name = sp.get("name", "").strip()
                if sp_name:
                    subpkg_names.append(sp_name)
                    all_subpackage_names.add(sp_name)
                    parent_of[sp_name] = name

        # If this element itself declares a parent, record it
        if parent:
            all_subpackage_names.add(name)
            if name not in parent_of:
                parent_of[name] = parent

        def _get(tag: str) -> list[str]:
            child = el.find(tag)
            return _split(child.get("value", "")) if child is not None else []

        raw[name] = _RawPackage(
            name=name,
            parent=parent,
            subpackage_names=subpkg_names,
            lib_req_pkgs=_get("LIB_REQUIRED_DEP_PACKAGES"),
            lib_opt_pkgs=_get("LIB_OPTIONAL_DEP_PACKAGES"),
            lib_req_tpls=_get("LIB_REQUIRED_DEP_TPLS"),
            lib_opt_tpls=_get("LIB_OPTIONAL_DEP_TPLS"),
        )

    # Inject any extra subpackage relationships not present in the XML
    if extra_subpackages:
        for sp_name, par_name in extra_subpackages.items():
            all_subpackage_names.add(sp_name)
            parent_of[sp_name] = par_name

    # ------------------------------------------------------------------
    # Pass 2: determine which packages are top-level.
    #         A package is top-level if its name is NOT in all_subpackage_names.
    # ------------------------------------------------------------------
    top_level_names: set[str] = {
        name for name in raw if name not in all_subpackage_names
    }

    def resolve_to_top_level(pkg_name: str) -> str | None:
        """Walk up parent_of until we reach a top-level package."""
        visited = set()
        current = pkg_name
        while current in all_subpackage_names:
            if current in visited:
                return None   # cycle guard
            visited.add(current)
            current = parent_of.get(current, "")
            if not current:
                return None
        return current if current in top_level_names else None

    # ------------------------------------------------------------------
    # Pass 3: build TrilinosPackage objects for each top-level package.
    #         Aggregate deps from the top-level element + all its sub-packages.
    # ------------------------------------------------------------------
    packages: list[TrilinosPackage] = []

    for name in sorted(top_level_names):
        r = raw[name]

        # Collect all _RawPackage entries that belong to this top-level pkg.
        # Use parent_of (built from <ParentPackage> child elements) as the
        # authoritative source — the real Trilinos XML has no <Subpackages>
        # list on the parent, only <ParentPackage> declarations on each child.
        subpackage_names_ordered: list[str] = [
            sp for sp in raw if parent_of.get(sp) == name
        ]
        members: list[_RawPackage] = [r] + [
            raw[sp] for sp in subpackage_names_ordered if sp in raw
        ]

        # Aggregate TPL deps across all members.
        # Collect required first across ALL members, then optional (excluding any already required).
        req_tpls: list[str] = []
        opt_tpls: list[str] = []
        seen_req_tpl: set[str] = set()
        # Maps optional TPL → list of subpackage names (or parent name) that introduced it
        opt_tpl_sources: dict[str, list[str]] = {}

        for m in members:
            for t in m.lib_req_tpls:
                if t not in seen_req_tpl:
                    seen_req_tpl.add(t)
                    req_tpls.append(t)

        seen_opt_tpl: set[str] = set()
        for m in members:
            for t in m.lib_opt_tpls:
                if t not in seen_req_tpl:
                    if t not in seen_opt_tpl:
                        seen_opt_tpl.add(t)
                        opt_tpls.append(t)
                        opt_tpl_sources[t] = []
                    # Record which member (subpackage or parent) introduced this TPL
                    opt_tpl_sources[t].append(m.name)

        # Aggregate intra-Trilinos package deps across all members.
        # If a dep is a sub-package, we record BOTH the sub-package name AND
        # its top-level parent (e.g. TeuchosCore → [TeuchosCore, Teuchos]).
        # Required always wins over optional for dedup.
        req_pkgs: list[str] = []
        opt_pkgs: list[str] = []
        seen_req_pkg: set[str] = set()
        seen_opt_pkg: set[str] = set()

        def _dep_names(dep: str) -> list[str]:
            """Return the dep itself plus its top-level parent (if it's a sub-pkg),
            filtering out anything that belongs to the package being built."""
            names = []
            # Skip deps that are sub-packages of this same top-level package
            if dep in all_subpackage_names and parent_of.get(dep) == name:
                return names
            names.append(dep)
            if dep in all_subpackage_names:
                top = resolve_to_top_level(dep)
                if top and top != dep and top != name:
                    names.append(top)
            return names

        # Collect all required first across all members so required wins dedup
        for m in members:
            for dep in m.lib_req_pkgs:
                for n in _dep_names(dep):
                    if n != name and n not in seen_req_pkg:
                        seen_req_pkg.add(n)
                        req_pkgs.append(n)

        # Maps optional package dep → list of subpackage names that introduced it
        opt_pkg_sources: dict[str, list[str]] = {}

        for m in members:
            for dep in m.lib_opt_pkgs:
                for n in _dep_names(dep):
                    if n != name and n not in seen_req_pkg:
                        if n not in seen_opt_pkg:
                            seen_opt_pkg.add(n)
                            opt_pkgs.append(n)
                            opt_pkg_sources[n] = []
                        opt_pkg_sources[n].append(m.name)

        packages.append(TrilinosPackage(
            name=name,
            subpackages=subpackage_names_ordered,
            required_tpl_deps=req_tpls,
            optional_tpl_deps=opt_tpls,
            optional_tpl_sources=opt_tpl_sources,
            required_package_deps=req_pkgs,
            optional_package_deps=opt_pkgs,
            optional_package_sources=opt_pkg_sources,
        ))

    return packages, dict(parent_of)


# ---------------------------------------------------------------------------
# Main (for quick inspection / debugging)
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Parse TrilinosPackageDependencies.xml into package objects"
    )
    parser.add_argument("--xml", required=True, help="Path to XML file")
    args = parser.parse_args()

    try:
        packages, subpkg_parent = parse_xml(args.xml)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed {len(packages)} top-level packages:\n")
    for pkg in packages:
        print(pkg)
        print()


if __name__ == "__main__":
    main()
