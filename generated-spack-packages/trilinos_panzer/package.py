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

class TrilinosPanzer(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Variants automatically generated from optional subpackages ###
    variant(dofmgr, default=True, description='Enable PanzerDofMgr')
    variant(discfe, default=True, description='Enable PanzerDiscFE')
    variant(adaptersstk, default=True, description='Enable PanzerAdaptersSTK')
    variant(miniem, default=True, description='Enable PanzerMiniEM')
    variant(expreval, default=True, description='Enable PanzerExprEval')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []
        generated_cmake_options.append(-DTrilinos_ENABLE_PanzerCore=ON)

        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_PanzerDofMgr', dofmgr))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_PanzerDiscFE', discfe))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_PanzerAdaptersSTK', adaptersstk))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_PanzerMiniEM', miniem))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_PanzerExprEval', expreval))

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        