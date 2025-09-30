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

class TrilinosPercept(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional TPLs variants ###
    variant('opennurbs', default=True, description='Enable tpl')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-intrepid2)
    depends_on_trilinos_package(trilinos-seacasioss)
    depends_on_trilinos_package(trilinos-stkutil)
    depends_on_trilinos_package(trilinos-stkio)
    depends_on_trilinos_package(trilinos-stkmesh)
    depends_on_trilinos_package(trilinos-stkexpr-eval)
    depends_on_trilinos_package(trilinos-stksearch)
    depends_on_trilinos_package(trilinos-stktransfer)
    depends_on_trilinos_package(trilinos-zoltan)

    ### Optional TPLs automatically generated ###
    depends_on(opennurbs, when='+opennurbs')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        