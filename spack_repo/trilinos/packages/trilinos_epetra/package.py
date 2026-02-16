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

class TrilinosEpetra(TrilinosBaseClass):
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
    
    ### Required tpl dependencies of Epetra ###
    #depends_on('blas')

    #depends_on('lapack')

    ###Optional tpl dependencies of Epetra ###
    variant('cask', default=True, description='Enable CASK')
    ##depends_on('cask', when='+cask')

    variant('mpi', default=True, description='Enable MPI')
    ##depends_on('mpi', when='+mpi')

    variant('oski', default=True, description='Enable Oski')
    ##depends_on('oski', when='+oski')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required tpl dependencies of Epetra ###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_BLAS=ON')

        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_LAPACK=ON')

        ###Optional tpl dependencies of Epetra ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CASK', 'cask'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'mpi'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Oski', 'oski'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        