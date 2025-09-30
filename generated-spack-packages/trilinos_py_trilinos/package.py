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

class TrilinosPyTrilinos(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional Trilinos dependencies variants ###
    variant('trilinos-epetra', default=True, description='Enable Epetra support')
    variant('trilinos-triutils', default=True, description='Enable Triutils support')
    variant('trilinos-tpetra', default=True, description='Enable Tpetra support')
    variant('trilinos-epetra-ext', default=True, description='Enable EpetraExt support')
    variant('trilinos-isorropia', default=True, description='Enable Isorropia support')
    variant('trilinos-aztec-oo', default=True, description='Enable AztecOO support')
    variant('trilinos-galeri', default=True, description='Enable Galeri support')
    variant('trilinos-amesos', default=True, description='Enable Amesos support')
    variant('trilinos-ifpack', default=True, description='Enable Ifpack support')
    variant('trilinos-anasazi', default=True, description='Enable Anasazi support')
    variant('trilinos-pliris', default=True, description='Enable Pliris support')
    variant('trilinos-ml', default=True, description='Enable ML support')
    variant('trilinos-nox', default=True, description='Enable NOX support')
    variant('trilinos-stk', default=True, description='Enable STK support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-teuchos)

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        