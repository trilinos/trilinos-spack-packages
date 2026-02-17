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
    variant('ifpack2', default=True, description='Enable Ifpack2')
    depends_on_trilinos_package('trilinos-ifpack2')
    #conflicts('+adaptersstk~ifpack2')
    variant('muelu', default=True, description='Enable MueLu')
    depends_on_trilinos_package('trilinos-mue-lu')
    #conflicts('+adaptersstk~muelu')
    variant('nox', default=True, description='Enable NOX')
    depends_on_trilinos_package('trilinos-nox')
    #conflicts('+adaptersstk~nox')
    variant('percept', default=True, description='Enable Percept')
    depends_on_trilinos_package('trilinos-percept')
    #conflicts('+adaptersstk~percept')
    variant('piro', default=True, description='Enable Piro')
    depends_on_trilinos_package('trilinos-piro')
    #conflicts('+adaptersstk~piro')
    variant('stratimikos', default=True, description='Enable Stratimikos')
    depends_on_trilinos_package('trilinos-stratimikos')
    #conflicts('+adaptersstk~stratimikos')
    variant('teko', default=True, description='Enable Teko')
    depends_on_trilinos_package('trilinos-teko')
    #conflicts('+adaptersstk~teko')
    variant('tempus', default=True, description='Enable Tempus')
    depends_on_trilinos_package('trilinos-tempus')
    #conflicts('+adaptersstk~tempus')
    variant('zoltan', default=True, description='Enable Zoltan')
    depends_on_trilinos_package('trilinos-zoltan')
    #conflicts('+adaptersstk~zoltan')

    ### Optional subpackage PanzerDiscFE ###
    variant('discfe', default=True, description='Enable PanzerDiscFE')
    variant('camal', default=True, description='Enable TPL CAMAL')
    depends_on('camal', when='+camal')
    #conflicts('+discfe~camal')
    variant('kokkos', default=True, description='Enable TPL Kokkos')
    depends_on('kokkos', when='+kokkos')
    #conflicts('+discfe~kokkos')
    variant('mpi', default=True, description='Enable TPL MPI')
    depends_on('mpi', when='+mpi')
    #conflicts('+discfe~mpi')
    variant('papi', default=True, description='Enable TPL PAPI')
    depends_on('papi', when='+papi')
    #conflicts('+discfe~papi')

    ### Optional subpackage PanzerDofMgr ###
    variant('dofmgr', default=True, description='Enable PanzerDofMgr')
    variant('mpi', default=True, description='Enable TPL MPI')
    depends_on('mpi', when='+mpi')
    #conflicts('+dofmgr~mpi')
    variant('intrepid2', default=True, description='Enable Intrepid2')
    depends_on_trilinos_package('trilinos-intrepid2')
    #conflicts('+dofmgr~intrepid2')
    variant('phalanx', default=True, description='Enable Phalanx')
    depends_on_trilinos_package('trilinos-phalanx')
    #conflicts('+dofmgr~phalanx')
    variant('shards', default=True, description='Enable Shards')
    depends_on_trilinos_package('trilinos-shards')
    #conflicts('+dofmgr~shards')
    variant('tpetra', default=True, description='Enable Tpetra')
    depends_on_trilinos_package('trilinos-tpetra')
    #conflicts('+dofmgr~tpetra')

    ### Optional subpackage PanzerExprEval ###
    variant('expreval', default=True, description='Enable PanzerExprEval')
    variant('kokkos', default=True, description='Enable TPL Kokkos')
    depends_on('kokkos', when='+kokkos')
    #conflicts('+expreval~kokkos')

    ### Optional subpackage PanzerMiniEM ###
    variant('miniem', default=True, description='Enable PanzerMiniEM')
    variant('camal', default=True, description='Enable TPL CAMAL')
    depends_on('camal', when='+camal')
    #conflicts('+miniem~camal')
    variant('mpi', default=True, description='Enable TPL MPI')
    depends_on('mpi', when='+mpi')
    #conflicts('+miniem~mpi')
    variant('papi', default=True, description='Enable TPL PAPI')
    depends_on('papi', when='+papi')
    #conflicts('+miniem~papi')
    variant('belos', default=True, description='Enable Belos')
    depends_on_trilinos_package('trilinos-belos')
    #conflicts('+miniem~belos')
    variant('muelu', default=True, description='Enable MueLu')
    depends_on_trilinos_package('trilinos-mue-lu')
    #conflicts('+miniem~muelu')
    variant('phalanx', default=True, description='Enable Phalanx')
    depends_on_trilinos_package('trilinos-phalanx')
    #conflicts('+miniem~phalanx')
    variant('teko', default=True, description='Enable Teko')
    depends_on_trilinos_package('trilinos-teko')
    #conflicts('+miniem~teko')


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

        ### Optional subpackage PanzerDofMgr ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_PanzerDofMgr', 'dofmgr'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'dofmgr'))
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
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MueLu', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Phalanx', 'miniem'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Teko', 'miniem'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        