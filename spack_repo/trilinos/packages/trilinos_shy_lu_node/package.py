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

class TrilinosShyLuNode(TrilinosBaseClass):
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
    
    ### Optional subpackage ShyLU_NodeBasker ###
    variant('basker', default=True, description='Enable ShyLU_NodeBasker')
    with when('+basker'):
        depends_on('kokkos')
        depends_on('metis')
        depends_on('mkl')
        depends_on('scotch')
        depends_on('vtune')

    ### Optional subpackage ShyLU_NodeFastILU ###
    variant('fastilu', default=True, description='Enable ShyLU_NodeFastILU')
    with when('+fastilu'):
        depends_on('kokkos')

    ### Optional subpackage ShyLU_NodeHTS ###
    variant('hts', default=True, description='Enable ShyLU_NodeHTS')
    with when('+hts'):
        depends_on('blas')
        depends_on('mkl')
        depends_on_trilinos_package('trilinos-kokkos-kernels')

    ### Optional subpackage ShyLU_NodeTacho ###
    variant('tacho', default=True, description='Enable ShyLU_NodeTacho')
    with when('+tacho'):
        depends_on('blas')
        depends_on('cublas')
        depends_on('cuda')
        depends_on('cusolver')
        depends_on('cusparse')
        depends_on('kokkos')
        depends_on('lapack')
        depends_on('metis')
        depends_on('mkl')
        depends_on('pthread')
        depends_on('qthread')
        depends_on('rocblas')
        depends_on('rocsolver')
        depends_on('rocsparse')
        depends_on('vtune')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Optional subpackage ShyLU_NodeBasker ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ShyLU_NodeBasker', 'basker'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'basker'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_METIS', 'basker'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MKL', 'basker'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Scotch', 'basker'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_VTune', 'basker'))

        ### Optional subpackage ShyLU_NodeFastILU ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ShyLU_NodeFastILU', 'fastilu'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'fastilu'))

        ### Optional subpackage ShyLU_NodeHTS ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ShyLU_NodeHTS', 'hts'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_BLAS', 'hts'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MKL', 'hts'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_KokkosKernels', 'hts'))

        ### Optional subpackage ShyLU_NodeTacho ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_ShyLU_NodeTacho', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_BLAS', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUBLAS', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUDA', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSOLVER', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSPARSE', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_LAPACK', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_METIS', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MKL', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Pthread', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_QTHREAD', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ROCBLAS', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ROCSOLVER', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ROCSPARSE', 'tacho'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_VTune', 'tacho'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        