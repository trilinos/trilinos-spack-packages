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

class TrilinosZoltan2Core(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional TPLs variants ###
    variant('metis', default=True, description='Enable tpl')
    variant('patoh', default=True, description='Enable tpl')
    variant('parmetis', default=True, description='Enable tpl')
    variant('pulp', default=True, description='Enable tpl')
    variant('scotch', default=True, description='Enable tpl')
    variant('sarma', default=True, description='Enable tpl')
    variant('amd', default=True, description='Enable tpl')
    variant('ovis', default=True, description='Enable tpl')
    variant('topomanager', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-epetra', default=True, description='Enable Epetra support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-tpetra)
    depends_on_trilinos_package(trilinos-teuchos-core)
    depends_on_trilinos_package(trilinos-teuchos-comm)
    depends_on_trilinos_package(trilinos-teuchos-parameter-list)
    depends_on_trilinos_package(trilinos-xpetra)
    depends_on_trilinos_package(trilinos-zoltan)

    ### Optional TPLs automatically generated ###
    depends_on(metis, when='+metis')
    depends_on(patoh, when='+patoh')
    depends_on(parmetis, when='+parmetis')
    depends_on(pulp, when='+pulp')
    depends_on(scotch, when='+scotch')
    depends_on(sarma, when='+sarma')
    depends_on(amd, when='+amd')
    depends_on(ovis, when='+ovis')
    depends_on(topomanager, when='+topomanager')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        