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
    
    ### Required subpackage TeuchosComm ###
    ### Required subpackage TeuchosCore ###
    ### Required subpackage TeuchosNumerics ###
    ### Required subpackage TeuchosParameterList ###
    ### Required subpackage TeuchosParser ###
    ### Required subpackage TeuchosRemainder ###

    ### Required tpls of Teuchos from subpackage requirements###
    depends_on('arprec')
    depends_on('binutils')
    depends_on('boost')
    depends_on('mpi')
    depends_on('pthread')
    depends_on('qd')
    depends_on('qt')
    depends_on('valgrind')
    depends_on('quadmath')
    depends_on('kokkos')
    depends_on('blas')
    depends_on('eigen')
    depends_on('lapack')
    depends_on('yamlcpp')

    ### Optional subpackage TeuchosKokkosComm ###
    variant('kokkoscomm', default=True, description='Enable TeuchosKokkosComm')
    with when('+kokkoscomm'):
        depends_on('kokkos')
        depends_on('mpi')

    ### Optional subpackage TeuchosKokkosCompat ###
    variant('kokkoscompat', default=True, description='Enable TeuchosKokkosCompat')
    with when('+kokkoscompat'):
        depends_on('kokkos')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required subpackage TeuchosComm ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosComm=ON')
        ### Required subpackage TeuchosCore ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosCore=ON')
        ### Required subpackage TeuchosNumerics ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosNumerics=ON')
        ### Required subpackage TeuchosParameterList ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosParameterList=ON')
        ### Required subpackage TeuchosParser ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosParser=ON')
        ### Required subpackage TeuchosRemainder ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TeuchosRemainder=ON')

        ### Required tpls of Teuchos from subpackage requirements###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_ARPREC=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_BinUtils=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Boost=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_MPI=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Pthread=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_QD=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_QT=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Valgrind=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_quadmath=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Kokkos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_BLAS=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Eigen=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_LAPACK=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_yamlcpp=ON')

        ### Optional subpackage TeuchosKokkosComm ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_TeuchosKokkosComm', 'kokkoscomm'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'kokkoscomm'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'kokkoscomm'))

        ### Optional subpackage TeuchosKokkosCompat ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_TeuchosKokkosCompat', 'kokkoscompat'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'kokkoscompat'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        