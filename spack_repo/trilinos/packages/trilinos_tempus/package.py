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

class TrilinosTempus(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("keitat", "kuberry", "jfrye", "jwillenbring", "psakievich")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    # ###################### Variants ##########################

    # ######################### TPLs #############################
    depends_on_trilinos_package("trilinos-nox")
    depends_on_trilinos_package("trilinos-thyra")
    depends_on_trilinos_package("trilinos-teuchos")
    
    def trilinos_package_cmake_args(self):
        args = [
        "-DTrilinos_ENABLE_Tempus=ON",
        "-DTPL_ENABLE_NOX=ON",
        "-DTPL_ENABLE_Teuchos=ON",
        "-DTPL_ENABLE_Thyra=ON",
        ]

        return args

    def cmake_args(self):
        args = []
        args.extend(self.trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args


    
