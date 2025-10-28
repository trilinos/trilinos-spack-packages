import os
7
from datetime import datetime

from spack.package import *

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.cuda import CudaPackage
from spack_repo.builtin.build_systems.rocm import ROCmPackage

import llnl.util.filesystem as fs
import spack.store

list_of_trilinos_variants=[]
trilinos_versions=[]

def trilinos_variant(variant_name, default, description):
    variant(variant_name, default=default, description=description)
    list_of_trilinos_variants.append(variant_name)
    
def depends_on_trilinos_package(trilinos_package_name):
    for tril_ver in trilinos_versions:
        depends_on(trilinos_package_name+"@"+tril_ver, when="@"+tril_ver)
    for t_variant in list_of_trilinos_variants:
        depends_on(trilinos_package_name+"+"+t_variant, when="+"+t_variant)
        depends_on(trilinos_package_name+"~"+t_variant, when="~"+t_variant)
    
class TrilinosBaseClass(CMakePackage, CudaPackage, ROCmPackage):
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
    #version("master", branch="master")
    #version("develop", branch="develop")
    #version("16.0.0", sha256="46bfc40419ed2aa2db38c144fb8e61d4aa8170eaa654a88d833ba6b92903f309")
    # List of possible trilinos versions.  used to enforce that depends_on_trilinos_package()
    # all have the same version
    trilinos_versions.append("master")
    trilinos_versions.append("develop")

    # ###################### Variants ##########################
    variant("tests", default=False, description="Enable build of package's test executables")

    variant(
        "cxxstd",
        values=("17", "20"),
        default="17",
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
    #trilinos_variant("mpi", default=True, description="Enable mpi")
    #trilinos_variant("fortran", default=False, description="Enable fortran")
    #trilinos_variant("wrapper", default=False, description="use kokkos-nvcc-wrapper")
    #trilinos_variant("openmp", default=False, description="use openmp")
    #trilinos_variant("explicit-instantiation", default=True, description="use explicit instantiation")
    #trilinos_variant("all-optional-packages", default=True, description="Enable all optional packages")

    # ###################### Dependencies ##########################
    kokkos_version="4.6.02"
    with when ("^kokkos"):
        depends_on(f"kokkos@{kokkos_version}")
    #depends_on("blas")
    #depends_on("lapack")
    #depends_on("kokkos@4.6.02")
    #depends_on("kokkos-kernels")
    
    depends_on("c", type="build")
    depends_on("cxx", type="build")
    #depends_on("fortran", type="build", when="+fortran")
    #depends_on("mpi", when="+mpi")
    #depends_on("kokkos-nvcc-wrapper", when="+wrapper")

    
    git_sparse_paths = []
        

    def trilinos_base_cmake_args(self):
        args = []
        args.append("-DTPL_ENABLE_Kokkos=ON")
        args.append("-DTPL_ENABLE_KokkosKernels=ON")

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
        args.append(self.define_from_variant("Trilinos_ENABLE_ALL_OPTIONAL_PACKAGES", "all-optional-packages"))
        #args.append(self.define_from_variant("TPL_ENABLE_MPI", "mpi"))
        
        if "^openblas" in self.spec:
            args.append(f"-DBLAS_LIBRARY_NAMES=openblas")
            args.append(f"-DLAPACK_LIBRARY_NAMES=openblas")

        return args
    
    def cmake_args(self):
        return []

