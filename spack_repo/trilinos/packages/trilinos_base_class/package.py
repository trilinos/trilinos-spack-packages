import os

from datetime import datetime

from spack.package import *
from os.path import join as join_path

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

import spack.store

list_of_trilinos_variants=[]
trilinos_versions=[]

def trilinos_variant(variant_name, default, description):
    variant(variant_name, default=default, description=description)
    list_of_trilinos_variants.append(variant_name)
    
def depends_on_trilinos_package(trilinos_package_spec, when=None):
    depends_on(trilinos_package_spec, when=when)

    pkg_name = trilinos_package_spec.split()[0]

    for tril_ver in trilinos_versions:
        depends_on(f"{pkg_name}@{tril_ver}", when=f"@{tril_ver}")

    for t_variant in list_of_trilinos_variants:
        depends_on(f"{pkg_name}")
        conflicts(f"^{pkg_name}+{t_variant}", when=f"~{t_variant}")
        conflicts(f"^{pkg_name}~{t_variant}", when=f"+{t_variant}")
    
class TrilinosBaseClass(CMakePackage):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages."""

    homepage = "https://trilinos.org/"
    url = "https://github.com/trilinos/Trilinos/archive/refs/tags/trilinos-release-12-12-1.tar.gz"
    git = "https://github.com/fryeguy52/Trilinos.git"

    maintainers("keitat", "kuberry", "jwillenbring", "psakievich", "jfrye")

    # ###################### Versions ##########################
    version("jfrye-spack-changes", branch="changes-for-spack")
    trilinos_versions.append("jfrye-spack-changes")
    version("develop", branch="develop")
    trilinos_versions.append("develop")
    #version("master", branch="master")
    #trilinos_versions.append("master")
    #version("develop", branch="develop")
    #trilinos_versions.append("develop")
    #version("16.0.0", sha256="46bfc40419ed2aa2db38c144fb8e61d4aa8170eaa654a88d833ba6b92903f309")
    #trilinos_versions.append("16.0.0")

    # ###################### Variants ##########################
    variant("tests", default=False, description="Enable build of package's test executables")

    variant(
        "cxxstd",
        values=("20", "23"),
        default="20",
        multi=False,
        description="C++ standard to use when building",
    )

    #Trilinos_ENABLE_ALL_FORWARD_DEP_PACKAGES:BOOL=OFF
    #Trilinos_ENABLE_ALL_OPTIONAL_PACKAGES:BOOL=ON
    #Trilinos_ENABLE_ALL_PACKAGES:BOOL=OFF

    #Trilinos_ENABLE_COMPLEX:BOOL=OFF
    #Trilinos_ENABLE_COMPLEX_DOUBLE:BOOL=OFF
    #Trilinos_ENABLE_COMPLEX_FLOAT:BOOL=OFF
    #Trilinos_ENABLE_FLOAT:BOOL=OFF
    #Trilinos_ENABLE_LONG_DOUBLE:BOOL=OFF


    #Trilinos_ENABLE_INSTALLATION_TESTING:STRING=OFF
    #Trilinos_ENABLE_SECONDARY_TESTED_CODE:BOOL=OFF

    #Trilinos_ENABLE_INSTALL_CMAKE_CONFIG_FILES:BOOL=ON

    #Trilinos_ENABLE_THREAD_SAFE:BOOL=OFF
    
    # List of variants we want to be the same between all packages built together
    trilinos_variant("mpi", default=True, description="Enable mpi")
    trilinos_variant("cuda", default=False, description="Enable cuda")
    trilinos_variant("fortran", default=True, description="Enable fortran")
    trilinos_variant("wrapper", default=False, description="use kokkos-nvcc-wrapper")
    trilinos_variant("openmp", default=False, description="use openmp")
    trilinos_variant("explicit-instantiation", default=True, description="use explicit instantiation")
    #trilinos_variant("all-optional-packages", default=True, description="Enable all optional packages")

    # ###################### Dependencies ##########################
    kokkos_version="5.2.0"
    openmpi_version="4.1.6"
    superlu_version="5.3.0"

    with when ("^kokkos"):
        depends_on(f"kokkos@{kokkos_version}")

    with when ("^kokkos" and "+cuda"):
        depends_on(f"kokkos@{kokkos_version} +cuda")

    with when ("^openmpi"):
        depends_on(f"openmpi@{openmpi_version}")

    with when ("^superlu"):
        depends_on(f"superlu@{superlu_version}")

    depends_on("blas")
    depends_on("lapack")
    
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    depends_on("fortran", type="build", when="+fortran")
    depends_on("kokkos-nvcc-wrapper", when="+wrapper")

    
    git_sparse_paths = []
        

    def generated_trilinos_base_cmake_args(self):
        args = []

        # Depricated Packages
        args.append("-DTrilinos_ENABLE_AztecOO=OFF")
        args.append("-DTrilinos_ENABLE_Isorropia=OFF")
        args.append("-DTrilinos_ENABLE_Amesos=OFF")
        args.append("-DTrilinos_ENABLE_Pliris=OFF")
        args.append("-DTrilinos_ENABLE_EpetraExt=OFF")
        args.append("-DTrilinos_ENABLE_Epetra=OFF")
        args.append("-DTrilinos_ENABLE_Ifpack=OFF")
        args.append("-DTrilinos_ENABLE_Amesos=OFF")
        args.append("-DTrilinos_ENABLE_Triutils=OFF")
        args.append("-DTrilinos_ENABLE_PyTrilinos=OFF")
        args.append("-DTrilinos_ENABLE_Intrepid=OFF")
        args.append("-DTrilinos_ENABLE_ML=OFF")

        # Definitions from variants
        args.append(self.define_from_variant("Trilinos_ENABLE_TESTS", "tests"))
        args.append(self.define_from_variant("Trilinos_ENABLE_INSTALLATION_TESTING", "tests"))
        args.append(self.define_from_variant("Trilinos_ENABLE_Gtest", "tests"))
        args.append(self.define_from_variant("CMAKE_CXX_STANDARD", "cxxstd"))
        args.append(self.define_from_variant("Trilinos_ENABLE_OpenMP", "openmp"))
        args.append(self.define_from_variant("Trilinos_ENABLE_EXPLICIT_INSTANTIATION", "explicit-instantiation"))

        # Disable auto-enabling of optional packages - we explicitly enable what we need
        args.append("-DTrilinos_ENABLE_ALL_OPTIONAL_PACKAGES=OFF")

        # Disable gtest TPL when tests are disabled, unless package explicitly depends on it
        if "~tests" in self.spec and "^googletest" not in self.spec:
            args.append("-DTPL_ENABLE_gtest=OFF")

        if "^mpi" in self.spec:
            args.append(self.define_from_variant("TPL_ENABLE_MPI", "mpi"))

        # ==============================================================================
        # Create a CMake include file for Spack-specific workarounds
        # ==============================================================================
        # This file is included right after project() initialization via CMAKE_PROJECT_INCLUDE.
        # It contains workarounds for issues that arise when building Trilinos packages
        # separately (as individual Spack packages) rather than as a monolithic build.
        # These are Spack-specific fixes and do not modify Trilinos source code.
        #
        # Background: In a monolithic Trilinos build, all packages are built together in
        # a single CMake configuration. When we split Trilinos into separate Spack packages,
        # previously-built Trilinos packages (like STK, Teuchos) become "external TPLs" to
        # later packages (like Panzer). This creates issues that don't occur in monolithic builds.
        # ==============================================================================

        needs_include_file = False
        include_file = join_path(self.stage.path, "spack_project_config.cmake")

        if "blas" in self.spec or "lapack" in self.spec:
            needs_include_file = True

        # Check if we depend on external Teuchos with MPI
        if "^trilinos-teuchos" in self.spec and "+mpi" in self.spec:
            needs_include_file = True

        if needs_include_file:
            with open(include_file, "w") as f:
                f.write("# =============================================================================\n")
                f.write("# Spack-specific CMake configuration for split Trilinos packages\n")
                f.write("# Generated by trilinos_base_class package.py\n")
                f.write("# =============================================================================\n\n")

                # ----------------------------------------------------------------------
                # Workaround #1: Manually create BLAS::BLAS and LAPACK::LAPACK targets
                # ----------------------------------------------------------------------
                # Problem: When Trilinos packages (like STK) are built separately and later
                # used as external TPLs by other packages (like Panzer), the STK CMake config
                # files reference BLAS::BLAS and LAPACK::LAPACK targets. However:
                #
                # 1. Trilinos uses a custom TriBITS TPL system that doesn't call the standard
                #    CMake FindBLAS/FindLAPACK modules, so these targets don't get created.
                # 2. We can't use find_package(BLAS/LAPACK) because that requires compilers
                #    to be detected, which hasn't happened yet when this file runs.
                #
                # Solution: Manually create INTERFACE IMPORTED GLOBAL targets with the actual
                # library paths from Spack. The GLOBAL scope ensures they're visible when
                # external package configs (like STKConfig.cmake) are loaded later.
                # This is provider-agnostic - works with OpenBLAS, Intel MKL, netlib-lapack, etc.
                # ----------------------------------------------------------------------
                if "blas" in self.spec:
                    # Get the actual BLAS library files from Spack (provider-agnostic)
                    blas_libs = self.spec["blas"].libs
                    f.write("# Create BLAS::BLAS imported target\n")
                    f.write("# Required because external Trilinos package configs reference this target\n")
                    f.write("if(NOT TARGET BLAS::BLAS)\n")
                    f.write("  add_library(BLAS::BLAS INTERFACE IMPORTED GLOBAL)\n")
                    f.write("  set_target_properties(BLAS::BLAS PROPERTIES\n")
                    f.write(f"    INTERFACE_LINK_LIBRARIES \"{';'.join(blas_libs)}\")\n")
                    f.write("endif()\n\n")

                if "lapack" in self.spec:
                    # Get the actual LAPACK library files from Spack (provider-agnostic)
                    lapack_libs = self.spec["lapack"].libs
                    f.write("# Create LAPACK::LAPACK imported target\n")
                    f.write("# Required because external Trilinos package configs reference this target\n")
                    f.write("if(NOT TARGET LAPACK::LAPACK)\n")
                    f.write("  add_library(LAPACK::LAPACK INTERFACE IMPORTED GLOBAL)\n")
                    f.write("  set_target_properties(LAPACK::LAPACK PROPERTIES\n")
                    f.write(f"    INTERFACE_LINK_LIBRARIES \"{';'.join(lapack_libs)}\")\n")
                    f.write("endif()\n\n")

                # ----------------------------------------------------------------------
                # Workaround #2: Define HAVE_TEUCHOS_MPI for external Teuchos with MPI
                # ----------------------------------------------------------------------
                # Problem: When using an external Teuchos package built with MPI support,
                # downstream packages (like Panzer) fail to compile with errors like:
                #   "error: 'MpiComm' in namespace 'Teuchos' does not name a template type"
                #
                # Root cause: The Teuchos::MpiComm class is guarded by #ifdef HAVE_TEUCHOS_MPI
                # in the Teuchos headers. While this define exists in the installed
                # Teuchos_config.h, when TriBITS processes Teuchos as an external TPL,
                # it doesn't properly propagate this preprocessor define to dependent packages.
                #
                # In a monolithic build, all packages share the same config and defines.
                # In separate builds, TriBITS generates new config files that may not
                # include all the defines from external package configs.
                #
                # Solution: Explicitly add HAVE_TEUCHOS_MPI as a compile definition when
                # building packages that depend on external Teuchos with MPI. This ensures
                # the preprocessor define is set globally for all compilation units.
                # ----------------------------------------------------------------------
                if "^trilinos-teuchos" in self.spec and "+mpi" in self.spec:
                    f.write("# Define HAVE_TEUCHOS_MPI when using external Teuchos with MPI\n")
                    f.write("# Required because TriBITS doesn't propagate this define from external Teuchos config\n")
                    f.write("# Without this, Teuchos::MpiComm class is not visible in dependent packages\n")
                    f.write("add_compile_definitions(HAVE_TEUCHOS_MPI)\n\n")

            args.append(f"-DCMAKE_PROJECT_INCLUDE={include_file}")

        return args
    
    def cmake_args(self):
        return self.generated_trilinos_base_cmake_args()

