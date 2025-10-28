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

class TrilinosThyra(TrilinosBaseClass):
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
    
    ### Required subpackage ThyraCore ###

    ### Required tpls of Thyra from subpackage requirements###
    depends_on_trilinos_package('trilinos-rtop')

    ### Optional subpackage ThyraEpetraAdapters ###
    variant('epetraadapters', default=True, description='Enable ThyraEpetraAdapters')
    with when('+epetraadapters'):
        depends_on_trilinos_package('trilinos-epetra')

    ### Optional subpackage ThyraEpetraExtAdapters ###
    variant('epetraextadapters', default=True, description='Enable ThyraEpetraExtAdapters')
    with when('+epetraextadapters'):
        depends_on_trilinos_package('trilinos-epetra')
        depends_on_trilinos_package('trilinos-epetra-ext')

    ### Optional subpackage ThyraTpetraAdapters ###
    variant('tpetraadapters', default=True, description='Enable ThyraTpetraAdapters')
    with when('+tpetraadapters'):
        depends_on_trilinos_package('trilinos-tpetra')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required subpackage ThyraCore ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_ThyraCore=ON')

        ### Required tpls of Thyra from subpackage requirements###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_RTOp=ON')

        ### Optional subpackage ThyraEpetraAdapters ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ThyraEpetraAdapters', 'epetraadapters'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Epetra', 'epetraadapters'))

        ### Optional subpackage ThyraEpetraExtAdapters ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ThyraEpetraExtAdapters', 'epetraextadapters'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Epetra', 'epetraextadapters'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_EpetraExt', 'epetraextadapters'))

        ### Optional subpackage ThyraTpetraAdapters ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ThyraTpetraAdapters', 'tpetraadapters'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Tpetra', 'tpetraadapters'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        