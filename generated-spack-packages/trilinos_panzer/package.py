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
    
    ### Required subpackages of Panzer ###
    trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_PanzerCore=ON')

    ### Required tpls of Panzer from subpackage requirements###

    ### Optional subpackages of Panzer ###
    variant('adaptersstk', default=True, description='Enable PanzerAdaptersSTK')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerAdaptersSTK', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-ifpack2', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Ifpack2', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-mue-lu', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MueLu', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-nox', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_NOX', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-percept', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Percept', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-piro', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Piro', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-stratimikos', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Stratimikos', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-teko', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Teko', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-tempus', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Tempus', 'adaptersstk'))
    depends_on_trilinos_package('trilinos-zoltan', when='+adaptersstk')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Zoltan', 'adaptersstk'))


    variant('discfe', default=True, description='Enable PanzerDiscFE')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerDiscFE', 'discfe'))
    depends_on('camal', when='+discfe')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CAMAL', 'discfe'))
    depends_on('kokkos', when='+discfe')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'discfe'))
    depends_on('mpi', when='+discfe')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'discfe'))
    depends_on('papi', when='+discfe')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PAPI', 'discfe'))
    depends_on_trilinos_package('trilinos-epetra', when='+discfe')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Epetra', 'discfe'))
    depends_on_trilinos_package('trilinos-epetra-ext', when='+discfe')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_EpetraExt', 'discfe'))


    variant('dofmgr', default=True, description='Enable PanzerDofMgr')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerDofMgr', 'dofmgr'))
    depends_on('mpi', when='+dofmgr')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'dofmgr'))
    depends_on_trilinos_package('trilinos-epetra', when='+dofmgr')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Epetra', 'dofmgr'))
    depends_on_trilinos_package('trilinos-intrepid2', when='+dofmgr')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Intrepid2', 'dofmgr'))
    depends_on_trilinos_package('trilinos-phalanx', when='+dofmgr')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Phalanx', 'dofmgr'))
    depends_on_trilinos_package('trilinos-shards', when='+dofmgr')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Shards', 'dofmgr'))
    depends_on_trilinos_package('trilinos-tpetra', when='+dofmgr')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Tpetra', 'dofmgr'))


    variant('expreval', default=True, description='Enable PanzerExprEval')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerExprEval', 'expreval'))
    depends_on('kokkos', when='+expreval')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'expreval'))


    variant('miniem', default=True, description='Enable PanzerMiniEM')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerMiniEM', 'miniem'))
    depends_on('camal', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CAMAL', 'miniem'))
    depends_on('mpi', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'miniem'))
    depends_on('papi', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PAPI', 'miniem'))
    depends_on_trilinos_package('trilinos-belos', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Belos', 'miniem'))
    depends_on_trilinos_package('trilinos-ml', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ML', 'miniem'))
    depends_on_trilinos_package('trilinos-mue-lu', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MueLu', 'miniem'))
    depends_on_trilinos_package('trilinos-phalanx', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Phalanx', 'miniem'))
    depends_on_trilinos_package('trilinos-teko', when='+miniem')
    trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Teko', 'miniem'))




    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        