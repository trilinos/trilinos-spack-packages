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

class TrilinosIfpack2(TrilinosBaseClass):
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
    
    ###Optional tpl dependencies of Ifpack2 ###
    variant('cholmod', default=True, description='Enable Cholmod')
    depends_on('cholmod', when='+cholmod')

    variant('hypre', default=True, description='Enable HYPRE')
    depends_on('hypre', when='+hypre')

    variant('lemon', default=True, description='Enable Lemon')
    depends_on('lemon', when='+lemon')

    variant('metis', default=True, description='Enable METIS')
    depends_on('metis', when='+metis')

    variant('mpi', default=True, description='Enable MPI')
    depends_on('mpi', when='+mpi')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ###Optional tpl dependencies of Ifpack2 ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Cholmod', 'cholmod'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_HYPRE', 'hypre'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Lemon', 'lemon'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_METIS', 'metis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'mpi'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        