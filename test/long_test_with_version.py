import subprocess
import pytest
import os

## Helper Functions ###
def run_spack_command(command):
    """Helper function to run a spack command and return the output."""
    result = subprocess.run(['spack'] + command.split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
    return result

def get_trilinos_version():
    """Get Trilinos version from environment variable, default to 'develop'."""
    return os.environ.get('TRILINOS_VERSION', 'develop')

def format_package_spec(package_name, version=None):
    """Format a package spec with optional version constraint."""
    if version is None:
        version = get_trilinos_version()
    return f"{package_name}@{version}"

## Fixtures ###
@pytest.fixture(scope="session")
def trilinos_packages():
    """Get a list of trilinos packages from spack. Cached for the entire test session."""
    result = run_spack_command("list trilinos-")
    print(result)
    if result.returncode == 0:
        return result.stdout.splitlines()
    else:
        return []

@pytest.fixture(scope="session")
def trilinos_version():
    """Get the Trilinos version being tested."""
    return get_trilinos_version()

### Tests ###

@pytest.mark.quick
def test_spack_version():
    """Test the 'spack version' command."""
    result = run_spack_command('--version')
    assert result.returncode == 0

@pytest.mark.quick
def test_spack_list():
    """Test the 'spack list' command."""
    result = run_spack_command('list')
    assert result.returncode == 0
    assert len(result.stdout) > 0

@pytest.mark.quick
def test_spack_find():
    """Test the 'spack find' command."""
    result = run_spack_command('find')
    assert result.returncode == 0

def test_spack_info(packageName, trilinos_packages, trilinos_version):
    """Test spack info works on the packages."""
    spec = format_package_spec(packageName, trilinos_version)
    result = run_spack_command(f"info {spec}")
    print(f"Testing: {spec}")
    assert result.returncode == 0

def test_spack_spec(packageName, trilinos_packages, trilinos_version):
    """Test spack spec works on the packages."""
    spec = format_package_spec(packageName, trilinos_version)
    result = run_spack_command(f"-dd spec {spec}")
    print(f"Testing spec for: {spec}")
    print(result.stdout)
    assert result.returncode == 0

@pytest.mark.slow
@pytest.mark.install
def test_spack_install(packageName, trilinos_packages, trilinos_version):
    """Test spack install works on the packages - REAL COMPILATION."""
    # This actually compiles each package (takes hours)
    # --reuse: reuse installed dependencies (OpenMPI, BLAS, Boost, etc.)
    # Set SPACK_OVERWRITE=1 env var to force reinstall, otherwise reuse existing
    spec = format_package_spec(packageName, trilinos_version)
    overwrite_flag = "--overwrite" if os.environ.get("SPACK_OVERWRITE") else ""

    print(f"Installing: {spec}")
    result = run_spack_command(f"install -j4 --reuse {overwrite_flag} -y {spec}")
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0

def pytest_generate_tests(metafunc):
    """Dynamically generate test parameters from the trilinos_packages fixture."""
    if "packageName" in metafunc.fixturenames:
        packages = metafunc.config.cache.get("trilinos_packages", None)
        if packages is None:
            result = run_spack_command("list trilinos-")
            packages = result.stdout.splitlines() if result.returncode == 0 else []
            metafunc.config.cache.set("trilinos_packages", packages)
        metafunc.parametrize("packageName", packages, ids=packages)
