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

class TrilinosAztecOo(TrilinosBaseClass):
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
    
    ###Optional tpl dependencies of AztecOO ###
    variant('y12m', default=True, description='Enable y12m')
    depends_on('y12m', when='+y12m')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ###Optional tpl dependencies of AztecOO ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_y12m', 'y12m'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        