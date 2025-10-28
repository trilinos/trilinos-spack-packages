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

class TrilinosShyLuDd(TrilinosBaseClass):
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
    
    ### Required subpackage ShyLU_DDCore ###
    ### Required subpackage ShyLU_DDFROSch ###

    ### Required tpls of ShyLU_DD from subpackage requirements###
    depends_on('mpi')
    depends_on_trilinos_package('trilinos-amesos')
    depends_on_trilinos_package('trilinos-amesos2')
    depends_on_trilinos_package('trilinos-aztec-oo')
    depends_on_trilinos_package('trilinos-belos')
    depends_on_trilinos_package('trilinos-epetra')
    depends_on_trilinos_package('trilinos-ifpack')
    depends_on_trilinos_package('trilinos-isorropia')
    depends_on_trilinos_package('trilinos-teuchos')
    depends_on_trilinos_package('trilinos-tpetra')
    depends_on_trilinos_package('trilinos-zoltan2-core')
    depends_on('mpi')
    depends_on_trilinos_package('trilinos-amesos')
    depends_on_trilinos_package('trilinos-amesos2')
    depends_on_trilinos_package('trilinos-belos')
    depends_on_trilinos_package('trilinos-epetra')
    depends_on_trilinos_package('trilinos-epetra-ext')
    depends_on_trilinos_package('trilinos-ifpack2')
    depends_on_trilinos_package('trilinos-mue-lu')
    depends_on_trilinos_package('trilinos-stratimikos')
    depends_on_trilinos_package('trilinos-teuchos')
    depends_on_trilinos_package('trilinos-thyra')
    depends_on_trilinos_package('trilinos-tpetra')
    depends_on_trilinos_package('trilinos-xpetra')
    depends_on_trilinos_package('trilinos-zoltan2')

    ### Optional subpackage ShyLU_DDCommon ###
    variant('common', default=True, description='Enable ShyLU_DDCommon')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required subpackage ShyLU_DDCore ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_ShyLU_DDCore=ON')
        ### Required subpackage ShyLU_DDFROSch ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_ShyLU_DDFROSch=ON')

        ### Required tpls of ShyLU_DD from subpackage requirements###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_MPI=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Amesos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Amesos2=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_AztecOO=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Belos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Epetra=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Ifpack=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Isorropia=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Teuchos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Tpetra=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Zoltan2Core=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_MPI=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Amesos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Amesos2=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Belos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Epetra=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_EpetraExt=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Ifpack2=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_MueLu=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Stratimikos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Teuchos=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Thyra=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Tpetra=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Xpetra=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Zoltan2=ON')

        ### Optional subpackage ShyLU_DDCommon ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ShyLU_DDCommon', 'common'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        