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

class TrilinosPanzer(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass

    # List of automatically generated cmake arguments
    trilinos_package_auto_cmake_args=[]
    
    ### Required subpackage PanzerCore ###

    ### Required tpls of Panzer from subpackage requirements###

    ### Optional subpackage PanzerAdaptersSTK ###
    variant('adaptersstk', default=True, description='Enable PanzerAdaptersSTK')
    with when('+adaptersstk'):
        depends_on_trilinos_package('trilinos-ifpack2')
        depends_on_trilinos_package('trilinos-mue-lu')
        depends_on_trilinos_package('trilinos-nox')
        depends_on_trilinos_package('trilinos-percept')
        depends_on_trilinos_package('trilinos-piro')
        depends_on_trilinos_package('trilinos-stratimikos')
        depends_on_trilinos_package('trilinos-teko')
        depends_on_trilinos_package('trilinos-tempus')
        depends_on_trilinos_package('trilinos-zoltan')

    ### Optional subpackage PanzerDiscFE ###
    variant('discfe', default=True, description='Enable PanzerDiscFE')
    with when('+discfe'):
        depends_on('camal')
        depends_on('kokkos')
        depends_on('mpi')
        depends_on('papi')
        depends_on_trilinos_package('trilinos-epetra')
        depends_on_trilinos_package('trilinos-epetra-ext')

    ### Optional subpackage PanzerDofMgr ###
    variant('dofmgr', default=True, description='Enable PanzerDofMgr')
    with when('+dofmgr'):
        depends_on('mpi')
        depends_on_trilinos_package('trilinos-epetra')
        depends_on_trilinos_package('trilinos-intrepid2')
        depends_on_trilinos_package('trilinos-phalanx')
        depends_on_trilinos_package('trilinos-shards')
        depends_on_trilinos_package('trilinos-tpetra')

    ### Optional subpackage PanzerExprEval ###
    variant('expreval', default=True, description='Enable PanzerExprEval')
    with when('+expreval'):
        depends_on('kokkos')

    ### Optional subpackage PanzerMiniEM ###
    variant('miniem', default=True, description='Enable PanzerMiniEM')
    with when('+miniem'):
        depends_on('camal')
        depends_on('mpi')
        depends_on('papi')
        depends_on_trilinos_package('trilinos-belos')
        depends_on_trilinos_package('trilinos-ml')
        depends_on_trilinos_package('trilinos-mue-lu')
        depends_on_trilinos_package('trilinos-phalanx')
        depends_on_trilinos_package('trilinos-teko')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required subpackage PanzerCore ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_PanzerCore=ON')

        ### Required tpls of Panzer from subpackage requirements###

        ### Optional subpackage PanzerAdaptersSTK ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerAdaptersSTK', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Ifpack2', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MueLu', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_NOX', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Percept', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Piro', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Stratimikos', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Teko', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Tempus', 'adaptersstk'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Zoltan', 'adaptersstk'))

        ### Optional subpackage PanzerDiscFE ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerDiscFE', 'discfe'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CAMAL', 'discfe'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'discfe'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'discfe'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PAPI', 'discfe'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Epetra', 'discfe'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_EpetraExt', 'discfe'))

        ### Optional subpackage PanzerDofMgr ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerDofMgr', 'dofmgr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'dofmgr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Epetra', 'dofmgr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Intrepid2', 'dofmgr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Phalanx', 'dofmgr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Shards', 'dofmgr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Tpetra', 'dofmgr'))

        ### Optional subpackage PanzerExprEval ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerExprEval', 'expreval'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'expreval'))

        ### Optional subpackage PanzerMiniEM ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerMiniEM', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CAMAL', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PAPI', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Belos', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ML', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MueLu', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Phalanx', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Teko', 'miniem'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        