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

class TrilinosEpetraExt(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional TPLs variants ###
    variant('hdf5', default=True, description='Enable tpl')
    variant('umfpack', default=True, description='Enable tpl')
    variant('amd', default=True, description='Enable tpl')
    variant('petsc', default=True, description='Enable tpl')
    variant('hypre', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-triutils', default=True, description='Enable Triutils support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-teuchos)
    depends_on_trilinos_package(trilinos-epetra)

    ### Optional TPLs automatically generated ###
    depends_on(hdf5, when='+hdf5')
    depends_on(umfpack, when='+umfpack')
    depends_on(amd, when='+amd')
    depends_on(petsc, when='+petsc')
    depends_on(hypre, when='+hypre')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        