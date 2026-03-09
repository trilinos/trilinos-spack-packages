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

def get_trilinos_packages():
    """Get a list of trilinos packages from spack."""
    result = run_spack_command("list trilinos-")
    print(result)
    if result.returncode == 0:
        return result.stdout.splitlines()  # Return the list of packages
    else:
        return []

### Tests ###
    
def test_spack_version():
    """Test the 'spack version' command."""
    result = run_spack_command('--version')
    assert result.returncode == 0

def test_spack_list():
    """Test the 'spack list' command."""
    result = run_spack_command('list')
    assert result.returncode == 0
    assert len(result.stdout) > 0  # Check that the output is not empty

def test_spack_find():
    """Test the 'spack find' command."""
    result = run_spack_command('find')
    assert result.returncode == 0

# Get the list of trilinos packages for parameterization
trilinos_packages = get_trilinos_packages()

@pytest.mark.parametrize("packageName", trilinos_packages, ids=trilinos_packages)
def test_spack_info(packageName):
    """Test spack info works on the packages."""
    result = run_spack_command(f"info {packageName}")
    assert result.returncode == 0

# Add more tests as needed
