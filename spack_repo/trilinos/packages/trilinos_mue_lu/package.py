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

class TrilinosMueLu(TrilinosBaseClass):
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
    
    ### Required tpl dependencies of MueLu ###
    depends_on('blas')

    depends_on('kokkos')

    depends_on('lapack')

    ###Optional tpl dependencies of MueLu ###
    variant('amgx', default=True, description='Enable AmgX')
    depends_on('amgx', when='+amgx')

    variant('avatar', default=True, description='Enable Avatar')
    depends_on('avatar', when='+avatar')

    variant('boost', default=True, description='Enable Boost')
    depends_on('boost', when='+boost')

    variant('cusparse', default=True, description='Enable CUSPARSE')
    depends_on('cusparse', when='+cusparse')

    variant('magmasparse', default=True, description='Enable MAGMASparse')
    depends_on('magmasparse', when='+magmasparse')

    variant('matlab', default=True, description='Enable MATLAB')
    depends_on('matlab', when='+matlab')

    variant('mkl', default=True, description='Enable MKL')
    depends_on('mkl', when='+mkl')

    variant('viennacl', default=True, description='Enable ViennaCL')
    depends_on('viennacl', when='+viennacl')

    variant('mlpack', default=True, description='Enable mlpack')
    depends_on('mlpack', when='+mlpack')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required tpl dependencies of MueLu ###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_BLAS=ON')

        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Kokkos=ON')

        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_LAPACK=ON')

        ###Optional tpl dependencies of MueLu ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_AmgX', 'amgx'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Avatar', 'avatar'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Boost', 'boost'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSPARSE', 'cusparse'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MAGMASparse', 'magmasparse'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MATLAB', 'matlab'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MKL', 'mkl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ViennaCL', 'viennacl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_mlpack', 'mlpack'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        