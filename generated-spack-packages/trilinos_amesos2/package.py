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

class TrilinosAmesos2(TrilinosBaseClass):
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
    variant('superlu', default=True, description='Enable tpl')
    variant('superlumt', default=True, description='Enable tpl')
    variant('superludist', default=True, description='Enable tpl')
    variant('lapack', default=True, description='Enable tpl')
    variant('umfpack', default=True, description='Enable tpl')
    variant('pardiso_mkl', default=True, description='Enable tpl')
    variant('css_mkl', default=True, description='Enable tpl')
    variant('parmetis', default=True, description='Enable tpl')
    variant('metis', default=True, description='Enable tpl')
    variant('cholmod', default=True, description='Enable tpl')
    variant('mumps', default=True, description='Enable tpl')
    variant('strumpack', default=True, description='Enable tpl')
    variant('cusparse', default=True, description='Enable tpl')
    variant('cusolver', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-epetra', default=True, description='Enable Epetra support')
    variant('trilinos-epetra-ext', default=True, description='Enable EpetraExt support')
    variant('trilinos-shylu_-node-basker', default=True, description='Enable ShyLU_NodeBasker support')
    variant('trilinos-shylu_-node-tacho', default=True, description='Enable ShyLU_NodeTacho support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-teuchos)
    depends_on_trilinos_package(trilinos-tpetra)
    depends_on_trilinos_package(trilinos-trilinos-ss)
    depends_on_trilinos_package(trilinos-kokkos)

    ### Optional TPLs automatically generated ###
    depends_on(mpi, when='+mpi')
    depends_on(superlu, when='+superlu')
    depends_on(superlumt, when='+superlumt')
    depends_on(superludist, when='+superludist')
    depends_on(lapack, when='+lapack')
    depends_on(umfpack, when='+umfpack')
    depends_on(pardiso_mkl, when='+pardiso_mkl')
    depends_on(css_mkl, when='+css_mkl')
    depends_on(parmetis, when='+parmetis')
    depends_on(metis, when='+metis')
    depends_on(cholmod, when='+cholmod')
    depends_on(mumps, when='+mumps')
    depends_on(strumpack, when='+strumpack')
    depends_on(cusparse, when='+cusparse')
    depends_on(cusolver, when='+cusolver')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        