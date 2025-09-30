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

class TrilinosMl(TrilinosBaseClass):
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
    variant('metis', default=True, description='Enable tpl')
    variant('parmetis', default=True, description='Enable tpl')
    variant('petsc', default=True, description='Enable tpl')
    variant('superlu', default=True, description='Enable tpl')
    variant('matlab', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-teuchos', default=True, description='Enable Teuchos support')
    variant('trilinos-epetra', default=True, description='Enable Epetra support')
    variant('trilinos-zoltan', default=True, description='Enable Zoltan support')
    variant('trilinos-galeri', default=True, description='Enable Galeri support')
    variant('trilinos-amesos', default=True, description='Enable Amesos support')
    variant('trilinos-ifpack', default=True, description='Enable Ifpack support')
    variant('trilinos-aztec-oo', default=True, description='Enable AztecOO support')
    variant('trilinos-epetra-ext', default=True, description='Enable EpetraExt support')
    variant('trilinos-isorropia', default=True, description='Enable Isorropia support')

    ### Required TPLs automatically generated ###
    depends_on(blas)
    depends_on(lapack)

    ### Optional TPLs automatically generated ###
    depends_on(mpi, when='+mpi')
    depends_on(metis, when='+metis')
    depends_on(parmetis, when='+parmetis')
    depends_on(petsc, when='+petsc')
    depends_on(superlu, when='+superlu')
    depends_on(matlab, when='+matlab')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        