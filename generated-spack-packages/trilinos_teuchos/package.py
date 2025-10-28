#
# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
import pathlib
import re
import sys

from spack.package import *
from ..trilinos_base_class.package import TrilinosBaseClass
from ..trilinos_base_class.package import depends_on_trilinos_package
from ..trilinos_base_class.package import trilinos_variant
from ..trilinos_base_class.package import list_of_trilinos_variants

class TrilinosTeuchos(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass

    # List of automatically generated cmake arguments
    trilinos_package_auto_cmake_args=[]
    
    ### Required subpackages of Teuchos ###
    trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosComm=ON')
    trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosCore=ON')
    trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosNumerics=ON')
    trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosParameterList=ON')
    trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosParser=ON')
    trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosRemainder=ON')

    ### Required tpls of Teuchos from subpackage requirements###
    depends_on('arprec')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_ARPREC=ON')
    depends_on('binutils')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_BinUtils=ON')
    depends_on('boost')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Boost=ON')
    depends_on('mpi')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_MPI=ON')
    depends_on('pthread')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Pthread=ON')
    depends_on('qd')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_QD=ON')
    depends_on('qt')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_QT=ON')
    depends_on('valgrind')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Valgrind=ON')
    depends_on('quadmath')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_quadmath=ON')
    depends_on('kokkos')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Kokkos=ON')
    depends_on('blas')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_BLAS=ON')
    depends_on('eigen')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Eigen=ON')
    depends_on('lapack')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_LAPACK=ON')
    depends_on('yamlcpp')
    trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_yamlcpp=ON')

    ### Optional subpackages of Teuchos ###
    variant('kokkoscomm', default=True, description='Enable TeuchosKokkosComm')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_TeuchosKokkosComm', 'kokkoscomm'))
    depends_on('kokkos', when='+kokkoscomm')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'kokkoscomm'))
    depends_on('mpi', when='+kokkoscomm')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'kokkoscomm'))


    variant('kokkoscompat', default=True, description='Enable TeuchosKokkosCompat')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_TeuchosKokkosCompat', 'kokkoscompat'))
    depends_on('kokkos', when='+kokkoscompat')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'kokkoscompat'))




    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        