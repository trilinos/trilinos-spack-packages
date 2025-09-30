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

class TrilinosAnasazi(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional TPLs variants ###
    variant('mpi', default=True, description='Enable tpl')
    variant('tbb', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-tpetra', default=True, description='Enable Tpetra support')
    variant('trilinos-epetra', default=True, description='Enable Epetra support')
    variant('trilinos-epetra-ext', default=True, description='Enable EpetraExt support')
    variant('trilinos-thyra-core', default=True, description='Enable ThyraCore support')
    variant('trilinos-thyra-epetra-adapters', default=True, description='Enable ThyraEpetraAdapters support')
    variant('trilinos-belos', default=True, description='Enable Belos support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-teuchos)

    ### Optional TPLs automatically generated ###
    depends_on(mpi, when='+mpi')
    depends_on(tbb, when='+tbb')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        