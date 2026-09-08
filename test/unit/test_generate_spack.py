import pytest
from unittest.mock import MagicMock, patch
import os
from generate_spack_packages import (
    _spack_pkg_name, _variant_name, _tpl_variant_name,
    _cmake_var_to_spack_variant, _tpl_to_spack,
    _remove_cyclic_optional_deps
)
from parse_tribits_xml import TrilinosPackage

def test_naming_helpers():
    assert _spack_pkg_name("Teuchos") == "trilinos-teuchos"
    assert _spack_pkg_name("ShyLU_Node") == "trilinos-shylu-node"
    assert _variant_name("TeuchosCore") == "teuchoscore"
    assert _variant_name("ShyLU_Node") == "shylu-node"
    assert _tpl_variant_name("MPI") == "mpi"
    assert _tpl_variant_name("yaml-cpp") == "yaml-cpp"

def test_cmake_variant_conversion():
    # Test omission of package prefix (must be at start)
    assert _cmake_var_to_spack_variant("Teuchos_something", "Teuchos") == "something"
    # Test omission of "use" prefix
    assert _cmake_var_to_spack_variant("USE_MPI", "Something") == "mpi"
    # Test alphanumeric cleaning (TPL_ENABLE is not explicitly stripped)
    assert _cmake_var_to_spack_variant("TPL_ENABLE_Something_Complex", "Something") == "tplenablesomethingcomplex"
    # Test simple case
    assert _cmake_var_to_spack_variant("ENABLE_Foo", "Bar") == "enablefoo"

def test_cycle_detection():
    # Create 3 packages: A, B, C
    # A depends on B (required)
    # B depends on C (required)
    # C depends on A (optional) -> should be dropped

    pkg_a = TrilinosPackage(name="A", required_package_deps=["B"])
    pkg_b = TrilinosPackage(name="B", required_package_deps=["C"])
    pkg_c = TrilinosPackage(name="C", optional_package_deps=["A"])

    packages = [pkg_a, pkg_b, pkg_c]

    # Need to mock _spack_pkg_name as it is used inside _remove_cyclic_optional_deps
    # But it's actually just a helper.

    result = _remove_cyclic_optional_deps(packages)

    # Package C's optional dependency on A should be removed
    assert pkg_c.optional_package_deps == []
    # A and B should remain unchanged
    assert pkg_a.required_package_deps == ["B"]
    assert pkg_b.required_package_deps == ["C"]

def test_cycle_detection_no_cycle():
    # A -> B -> C
    pkg_a = TrilinosPackage(name="A", required_package_deps=["B"])
    pkg_b = TrilinosPackage(name="B", required_package_deps=["C"])
    pkg_c = TrilinosPackage(name="C")

    packages = [pkg_a, pkg_b, pkg_c]
    result = _remove_cyclic_optional_deps(packages)

    assert pkg_a.required_package_deps == ["B"]
    assert pkg_b.required_package_deps == ["C"]
    assert pkg_c.optional_package_deps == []
