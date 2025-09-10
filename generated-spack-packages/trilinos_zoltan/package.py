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

class TrilinosZoltan(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional TPLs variants ###
    variant(mpi, default=True, description='Enable tpl')
    variant(metis, default=True, description='Enable tpl')
    variant(parmetis, default=True, description='Enable tpl')
    variant(patoh, default=True, description='Enable tpl')
    variant(scotch, default=True, description='Enable tpl')
    variant(zlib, default=True, description='Enable tpl')
    variant(ovis, default=True, description='Enable tpl')

    ### Optional TPLs automatically generated ###
    depends_on(mpi, when='+mpi')
    depends_on(metis, when='+metis')
    depends_on(parmetis, when='+parmetis')
    depends_on(patoh, when='+patoh')
    depends_on(scotch, when='+scotch')
    depends_on(zlib, when='+zlib')
    depends_on(ovis, when='+ovis')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        