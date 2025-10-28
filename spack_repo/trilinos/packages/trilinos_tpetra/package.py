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

class TrilinosTpetra(TrilinosBaseClass):
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
    
    ### Required subpackage TpetraCore ###

    ### Required tpls of Tpetra from subpackage requirements###
    depends_on('cuda')
    depends_on('kokkos')
    depends_on('mpi')
    depends_on('qd')
    depends_on('mpi_advance')
    depends_on('quadmath')
    depends_on_trilinos_package('trilinos-epetra')

    ### Optional subpackage TpetraTSQR ###
    variant('tsqr', default=True, description='Enable TpetraTSQR')
    with when('+tsqr'):
        depends_on('cublas')
        depends_on('cusolver')
        depends_on('kokkos')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required subpackage TpetraCore ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_TpetraCore=ON')

        ### Required tpls of Tpetra from subpackage requirements###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_CUDA=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Kokkos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_MPI=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_QD=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_mpi_advance=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_quadmath=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Epetra=ON')

        ### Optional subpackage TpetraTSQR ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_TpetraTSQR', 'tsqr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUBLAS', 'tsqr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSOLVER', 'tsqr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'tsqr'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        