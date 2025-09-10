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
    
    ### Optional TPLs variants ###
    variant(quadmath, default=True, description='Enable tpl')
    variant(mkl, default=True, description='Enable tpl')
    variant(blas, default=True, description='Enable tpl')
    variant(lapack, default=True, description='Enable tpl')
    variant(metis, default=True, description='Enable tpl')
    variant(superlu, default=True, description='Enable tpl')
    variant(cholmod, default=True, description='Enable tpl')
    variant(cublas, default=True, description='Enable tpl')
    variant(cusparse, default=True, description='Enable tpl')
    variant(cusolver, default=True, description='Enable tpl')
    variant(rocblas, default=True, description='Enable tpl')
    variant(rocsparse, default=True, description='Enable tpl')
    variant(rocsolver, default=True, description='Enable tpl')

    ### Optional TPLs automatically generated ###
    depends_on(quadmath, when='+quadmath')
    depends_on(mkl, when='+mkl')
    depends_on(blas, when='+blas')
    depends_on(lapack, when='+lapack')
    depends_on(metis, when='+metis')
    depends_on(superlu, when='+superlu')
    depends_on(cholmod, when='+cholmod')
    depends_on(cublas, when='+cublas')
    depends_on(cusparse, when='+cusparse')
    depends_on(cusolver, when='+cusolver')
    depends_on(rocblas, when='+rocblas')
    depends_on(rocsparse, when='+rocsparse')
    depends_on(rocsolver, when='+rocsolver')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        