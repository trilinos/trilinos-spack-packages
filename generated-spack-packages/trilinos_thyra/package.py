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

class TrilinosThyra(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Variants automatically generated from optional subpackages ###
    variant(epetraadapters, default=True, description='Enable ThyraEpetraAdapters')
    variant(epetraextadapters, default=True, description='Enable ThyraEpetraExtAdapters')
    variant(tpetraadapters, default=True, description='Enable ThyraTpetraAdapters')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []
        generated_cmake_options.append(-DTrilinos_ENABLE_ThyraCore=ON)

        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_ThyraEpetraAdapters', epetraadapters))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_ThyraEpetraExtAdapters', epetraextadapters))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_ThyraTpetraAdapters', tpetraadapters))

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        