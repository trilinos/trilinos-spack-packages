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

class TrilinosKokkosKernels(TrilinosBaseClass):
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
    
    ### Required tpl dependencies of KokkosKernels ###
    depends_on('kokkos')

    ###Optional tpl dependencies of KokkosKernels ###
    variant('blas', default=True, description='Enable BLAS')
    depends_on('blas', when='+blas')

    variant('cublas', default=True, description='Enable CUBLAS')
    depends_on('cublas', when='+cublas')

    variant('cusolver', default=True, description='Enable CUSOLVER')
    depends_on('cusolver', when='+cusolver')

    variant('cusparse', default=True, description='Enable CUSPARSE')
    depends_on('cusparse', when='+cusparse')

    variant('cholmod', default=True, description='Enable Cholmod')
    depends_on('cholmod', when='+cholmod')

    variant('lapack', default=True, description='Enable LAPACK')
    depends_on('lapack', when='+lapack')

    variant('metis', default=True, description='Enable METIS')
    depends_on('metis', when='+metis')

    variant('mkl', default=True, description='Enable MKL')
    depends_on('mkl', when='+mkl')

    variant('rocblas', default=True, description='Enable ROCBLAS')
    depends_on('rocblas', when='+rocblas')

    variant('rocsolver', default=True, description='Enable ROCSOLVER')
    depends_on('rocsolver', when='+rocsolver')

    variant('rocsparse', default=True, description='Enable ROCSPARSE')
    depends_on('rocsparse', when='+rocsparse')

    variant('superlu', default=True, description='Enable SuperLU')
    depends_on('superlu', when='+superlu')

    variant('quadmath', default=True, description='Enable quadmath')
    depends_on('quadmath', when='+quadmath')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required tpl dependencies of KokkosKernels ###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Kokkos=ON')

        ###Optional tpl dependencies of KokkosKernels ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_BLAS', 'blas'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUBLAS', 'cublas'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSOLVER', 'cusolver'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSPARSE', 'cusparse'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Cholmod', 'cholmod'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_LAPACK', 'lapack'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_METIS', 'metis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MKL', 'mkl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ROCBLAS', 'rocblas'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ROCSOLVER', 'rocsolver'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ROCSPARSE', 'rocsparse'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SuperLU', 'superlu'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_quadmath', 'quadmath'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        