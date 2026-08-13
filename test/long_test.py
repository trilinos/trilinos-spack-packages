import subprocess
import pytest

## Helper Functions ###
def run_spack_command(command):
    """Helper function to run a spack command and return the output."""
    result = subprocess.run(['spack'] + command.split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
    return result

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

def test_spack_info(packageName, trilinos_packages):
    """Test spack info works on the packages."""
    result = run_spack_command(f"info {packageName}")
    assert result.returncode == 0

def test_spack_spec(packageName, trilinos_packages):
    """Test spack spec works on the packages."""
    result = run_spack_command(f"-dd spec {packageName}")
    print(result)
    assert result.returncode == 0

@pytest.mark.slow
@pytest.mark.install
def test_spack_install(packageName, trilinos_packages):
    """Test spack install works on the packages."""
    result = run_spack_command(f"install -k -j4 --overwrite -y {packageName}")
    print(result)
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
