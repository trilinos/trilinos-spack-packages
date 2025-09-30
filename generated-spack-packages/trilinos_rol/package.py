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

class TrilinosRol(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional TPLs variants ###
    variant('boost', default=True, description='Enable tpl')
    variant('arrayfirecpu', default=True, description='Enable tpl')
    variant('eigen', default=True, description='Enable tpl')
    variant('pebbl', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-belos', default=True, description='Enable Belos support')
    variant('trilinos-epetra', default=True, description='Enable Epetra support')
    variant('trilinos-tpetra', default=True, description='Enable Tpetra support')
    variant('trilinos-thyra', default=True, description='Enable Thyra support')
    variant('trilinos-sacado', default=True, description='Enable Sacado support')
    variant('trilinos-intrepid', default=True, description='Enable Intrepid support')
    variant('trilinos-mini-tensor', default=True, description='Enable MiniTensor support')
    variant('trilinos-shards', default=True, description='Enable Shards support')
    variant('trilinos-amesos', default=True, description='Enable Amesos support')
    variant('trilinos-amesos2', default=True, description='Enable Amesos2 support')
    variant('trilinos-ifpack2', default=True, description='Enable Ifpack2 support')
    variant('trilinos-mue-lu', default=True, description='Enable MueLu support')
    variant('trilinos-tempus', default=True, description='Enable Tempus support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-teuchos)

    ### Optional TPLs automatically generated ###
    depends_on(boost, when='+boost')
    depends_on(arrayfirecpu, when='+arrayfirecpu')
    depends_on(eigen, when='+eigen')
    depends_on(pebbl, when='+pebbl')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        