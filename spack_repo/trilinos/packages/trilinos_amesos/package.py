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

class TrilinosAmesos(TrilinosBaseClass):
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
    
    ###Optional tpl dependencies of Amesos ###
    variant('blacs', default=True, description='Enable BLACS')
    ##depends_on('blacs', when='+blacs')

    variant('css_mkl', default=True, description='Enable CSS_MKL')
    ##depends_on('css_mkl', when='+css_mkl')

    variant('csparse', default=True, description='Enable CSparse')
    ##depends_on('csparse', when='+csparse')

    variant('mumps', default=True, description='Enable MUMPS')
    ##depends_on('mumps', when='+mumps')

    variant('pardiso', default=True, description='Enable PARDISO')
    ##depends_on('pardiso', when='+pardiso')

    variant('pardiso_mkl', default=True, description='Enable PARDISO_MKL')
    ##depends_on('pardiso_mkl', when='+pardiso_mkl')

    variant('parmetis', default=True, description='Enable ParMETIS')
    ##depends_on('parmetis', when='+parmetis')

    variant('scalapack', default=True, description='Enable SCALAPACK')
    ##depends_on('scalapack', when='+scalapack')

    variant('superlu', default=True, description='Enable SuperLU')
    ##depends_on('superlu', when='+superlu')

    variant('superludist', default=True, description='Enable SuperLUDist')
    ##depends_on('superludist', when='+superludist')

    variant('taucs', default=True, description='Enable TAUCS')
    ##depends_on('taucs', when='+taucs')

    variant('umfpack', default=True, description='Enable UMFPACK')
    ##depends_on('umfpack', when='+umfpack')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ###Optional tpl dependencies of Amesos ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_BLACS', 'blacs'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CSS_MKL', 'css_mkl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CSparse', 'csparse'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MUMPS', 'mumps'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PARDISO', 'pardiso'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PARDISO_MKL', 'pardiso_mkl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ParMETIS', 'parmetis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SCALAPACK', 'scalapack'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SuperLU', 'superlu'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SuperLUDist', 'superludist'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_TAUCS', 'taucs'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_UMFPACK', 'umfpack'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        