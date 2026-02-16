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

    # List of automatically generated cmake arguments
    trilinos_package_auto_cmake_args=[]
    
    ### Required tpl dependencies of Amesos2 ###
    #depends_on('kokkos')

    ###Optional tpl dependencies of Amesos2 ###
    variant('css_mkl', default=True, description='Enable CSS_MKL')
    ##depends_on('css_mkl', when='+css_mkl')

    variant('cusolver', default=True, description='Enable CUSOLVER')
    ##depends_on('cusolver', when='+cusolver')

    variant('cusparse', default=True, description='Enable CUSPARSE')
    ##depends_on('cusparse', when='+cusparse')

    variant('cholmod', default=True, description='Enable Cholmod')
    ##depends_on('cholmod', when='+cholmod')

    variant('lapack', default=True, description='Enable LAPACK')
    ##depends_on('lapack', when='+lapack')

    variant('metis', default=True, description='Enable METIS')
    ##depends_on('metis', when='+metis')

    variant('mpi', default=True, description='Enable MPI')
    ##depends_on('mpi', when='+mpi')

    variant('mumps', default=True, description='Enable MUMPS')
    ##depends_on('mumps', when='+mumps')

    variant('pardiso_mkl', default=True, description='Enable PARDISO_MKL')
    ##depends_on('pardiso_mkl', when='+pardiso_mkl')

    variant('parmetis', default=True, description='Enable ParMETIS')
    ##depends_on('parmetis', when='+parmetis')

    variant('strumpack', default=True, description='Enable STRUMPACK')
    ##depends_on('strumpack', when='+strumpack')

    variant('superlu', default=True, description='Enable SuperLU')
    ##depends_on('superlu', when='+superlu')

    variant('superludist', default=True, description='Enable SuperLUDist')
    ##depends_on('superludist', when='+superludist')

    variant('superlumt', default=True, description='Enable SuperLUMT')
    ##depends_on('superlumt', when='+superlumt')

    variant('umfpack', default=True, description='Enable UMFPACK')
    ##depends_on('umfpack', when='+umfpack')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required tpl dependencies of Amesos2 ###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Kokkos=ON')

        ###Optional tpl dependencies of Amesos2 ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CSS_MKL', 'css_mkl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSOLVER', 'cusolver'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSPARSE', 'cusparse'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Cholmod', 'cholmod'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_LAPACK', 'lapack'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_METIS', 'metis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'mpi'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MUMPS', 'mumps'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PARDISO_MKL', 'pardiso_mkl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ParMETIS', 'parmetis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_STRUMPACK', 'strumpack'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SuperLU', 'superlu'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SuperLUDist', 'superludist'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SuperLUMT', 'superlumt'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_UMFPACK', 'umfpack'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        