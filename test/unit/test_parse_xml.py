import pytest
import os
from xml.etree import ElementTree as ET
from parse_tribits_xml import parse_xml, TrilinosPackage

def create_test_xml(path, content):
    with open(path, "w") as f:
        f.write(content)

@pytest.fixture
def simple_xml(tmp_path):
    xml_path = tmp_path / "test_deps.xml"
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <TrilinosPackageDependencies>
        <Package name="Teuchos">
            <LIB_REQUIRED_DEP_TPLS value="MPI, Zlib"/>
            <LIB_OPTIONAL_DEP_TPLS value="Boost"/>
            <Subpackages>
                <Subpackage name="TeuchosCore"/>
            </Subpackages>
        </Package>
        <Package name="TeuchosCore" parentPackage="Teuchos">
            <LIB_REQUIRED_DEP_TPLS value="MPI"/>
            <LIB_OPTIONAL_DEP_TPLS value="HDF5"/>
        </Package>
        <Package name="Belos">
            <LIB_REQUIRED_DEP_PACKAGES value="TeuchosCore"/>
            <LIB_OPTIONAL_DEP_PACKAGES value="Teuchos"/>
            <TEST_REQUIRED_DEP_TPLS value="Gtest"/>
        </Package>
    </TrilinosPackageDependencies>
    """
    create_test_xml(str(xml_path), content)
    return str(xml_path)

def test_parse_xml_basic(simple_xml):
    packages, parent_map = parse_xml(simple_xml)

    # Should have Teuchos and Belos as top-level
    pkg_names = [p.name for p in packages]
    assert "Teuchos" in pkg_names
    assert "Belos" in pkg_names
    assert "TeuchosCore" not in pkg_names

    # Teuchos aggregation
    teuchos = next(p for p in packages if p.name == "Teuchos")
    assert "MPI" in teuchos.required_tpl_deps
    assert "Zlib" in teuchos.required_tpl_deps
    assert "Boost" in teuchos.optional_tpl_deps
    assert "HDF5" in teuchos.optional_tpl_deps # aggregated from TeuchosCore
    assert "TeuchosCore" in teuchos.subpackages

    # Belos resolution
    belos = next(p for p in packages if p.name == "Belos")
    # TeuchosCore is a subpackage of Teuchos, so it should resolve to Teuchos
    assert "Teuchos" in belos.required_package_deps
    assert "Gtest" in belos.test_required_tpl_deps

def test_extra_subpackages(tmp_path):
    xml_path = tmp_path / "extra.xml"
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <TrilinosPackageDependencies>
        <Package name="Zoltan2"/>
        <Package name="Zoltan2Core"/>
    </TrilinosPackageDependencies>
    """
    create_test_xml(str(xml_path), content)

    # Inject Zoltan2Core -> Zoltan2
    packages, parent_map = parse_xml(str(xml_path), extra_subpackages={"Zoltan2Core": "Zoltan2"})

    pkg_names = [p.name for p in packages]
    assert "Zoltan2" in pkg_names
    assert "Zoltan2Core" not in pkg_names
    assert parent_map["Zoltan2Core"] == "Zoltan2"

def test_complex_resolution(tmp_path):
    xml_path = tmp_path / "complex.xml"
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <TrilinosPackageDependencies>
        <Package name="A"/>
        <Package name="A1" parentPackage="A"/>
        <Package name="B">
            <LIB_REQUIRED_DEP_PACKAGES value="A1"/>
        </Package>
    </TrilinosPackageDependencies>
    """
    create_test_xml(str(xml_path), content)
    packages, _ = parse_xml(str(xml_path))

    b_pkg = next(p for p in packages if p.name == "B")
    # B depends on A1, which is a subpackage of A. Result should be A.
    assert "A" in b_pkg.required_package_deps
