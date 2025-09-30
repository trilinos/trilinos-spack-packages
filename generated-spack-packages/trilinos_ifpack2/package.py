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

class TrilinosIfpack2(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Optional TPLs variants ###
    variant('hypre', default=True, description='Enable tpl')
    variant('cholmod', default=True, description='Enable tpl')
    variant('lemon', default=True, description='Enable tpl')
    variant('metis', default=True, description='Enable tpl')
    variant('mpi', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-xpetra', default=True, description='Enable Xpetra support')
    variant('trilinos-zoltan2-core', default=True, description='Enable Zoltan2Core support')
    variant('trilinos-thyra-tpetra-adapters', default=True, description='Enable ThyraTpetraAdapters support')
    variant('trilinos-amesos2', default=True, description='Enable Amesos2 support')
    variant('trilinos-shylu_-node-basker', default=True, description='Enable ShyLU_NodeBasker support')
    variant('trilinos-shylu_-node-hts', default=True, description='Enable ShyLU_NodeHTS support')
    variant('trilinos-shylu_-node-fast-ilu', default=True, description='Enable ShyLU_NodeFastILU support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-belos)
    depends_on_trilinos_package(trilinos-teuchos)
    depends_on_trilinos_package(trilinos-tpetra)
    depends_on_trilinos_package(trilinos-kokkos-kernels)

    ### Optional TPLs automatically generated ###
    depends_on(hypre, when='+hypre')
    depends_on(cholmod, when='+cholmod')
    depends_on(lemon, when='+lemon')
    depends_on(metis, when='+metis')
    depends_on(mpi, when='+mpi')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        