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
    variant('kokkos', default=True, description='Enable TPL Kokkos')
    depends_on('kokkos', when='+kokkos')
    #conflicts('+basker~kokkos')
    variant('metis', default=True, description='Enable TPL METIS')
    depends_on('metis', when='+metis')
    #conflicts('+basker~metis')
    variant('mkl', default=True, description='Enable TPL MKL')
    depends_on('mkl', when='+mkl')
    #conflicts('+basker~mkl')
    variant('scotch', default=True, description='Enable TPL Scotch')
    depends_on('scotch', when='+scotch')
    #conflicts('+basker~scotch')
    variant('vtune', default=True, description='Enable TPL VTune')
    depends_on('vtune', when='+vtune')
    #conflicts('+basker~vtune')

    ### Optional subpackage ShyLU_NodeFastILU ###
    variant('fastilu', default=True, description='Enable ShyLU_NodeFastILU')
    variant('kokkos', default=True, description='Enable TPL Kokkos')
    depends_on('kokkos', when='+kokkos')
    #conflicts('+fastilu~kokkos')

    ### Optional subpackage ShyLU_NodeHTS ###
    variant('hts', default=True, description='Enable ShyLU_NodeHTS')
    variant('blas', default=True, description='Enable TPL BLAS')
    depends_on('blas', when='+blas')
    #conflicts('+hts~blas')
    variant('mkl', default=True, description='Enable TPL MKL')
    depends_on('mkl', when='+mkl')
    #conflicts('+hts~mkl')
    variant('kokkoskernels', default=True, description='Enable KokkosKernels')
    depends_on_trilinos_package('trilinos-kokkos-kernels')
    #conflicts('+hts~kokkoskernels')

    ### Optional subpackage ShyLU_NodeTacho ###
    variant('tacho', default=True, description='Enable ShyLU_NodeTacho')
    variant('blas', default=True, description='Enable TPL BLAS')
    depends_on('blas', when='+blas')
    #conflicts('+tacho~blas')
    variant('cublas', default=True, description='Enable TPL CUBLAS')
    depends_on('cublas', when='+cublas')
    #conflicts('+tacho~cublas')
    variant('cuda', default=True, description='Enable TPL CUDA')
    depends_on('cuda', when='+cuda')
    #conflicts('+tacho~cuda')
    variant('cusolver', default=True, description='Enable TPL CUSOLVER')
    depends_on('cusolver', when='+cusolver')
    #conflicts('+tacho~cusolver')
    variant('cusparse', default=True, description='Enable TPL CUSPARSE')
    depends_on('cusparse', when='+cusparse')
    #conflicts('+tacho~cusparse')
    variant('kokkos', default=True, description='Enable TPL Kokkos')
    depends_on('kokkos', when='+kokkos')
    #conflicts('+tacho~kokkos')
    variant('lapack', default=True, description='Enable TPL LAPACK')
    depends_on('lapack', when='+lapack')
    #conflicts('+tacho~lapack')
    variant('metis', default=True, description='Enable TPL METIS')
    depends_on('metis', when='+metis')
    #conflicts('+tacho~metis')
    variant('mkl', default=True, description='Enable TPL MKL')
    depends_on('mkl', when='+mkl')
    #conflicts('+tacho~mkl')
    variant('pthread', default=True, description='Enable TPL Pthread')
    depends_on('pthread', when='+pthread')
    #conflicts('+tacho~pthread')
    variant('qthread', default=True, description='Enable TPL QTHREAD')
    depends_on('qthread', when='+qthread')
    #conflicts('+tacho~qthread')
    variant('rocblas', default=True, description='Enable TPL ROCBLAS')
    depends_on('rocblas', when='+rocblas')
    #conflicts('+tacho~rocblas')
    variant('rocsolver', default=True, description='Enable TPL ROCSOLVER')
    depends_on('rocsolver', when='+rocsolver')
    #conflicts('+tacho~rocsolver')
    variant('rocsparse', default=True, description='Enable TPL ROCSPARSE')
    depends_on('rocsparse', when='+rocsparse')
    #conflicts('+tacho~rocsparse')
    variant('vtune', default=True, description='Enable TPL VTune')
    depends_on('vtune', when='+vtune')
    #conflicts('+tacho~vtune')


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
        