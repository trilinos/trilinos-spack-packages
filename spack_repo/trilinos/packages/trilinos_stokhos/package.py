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

class TrilinosStokhos(TrilinosBaseClass):
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
    
    ### Required tpl dependencies of Stokhos ###
    #depends_on('kokkos')

    ###Optional tpl dependencies of Stokhos ###
    variant('boost', default=True, description='Enable Boost')
    ##depends_on('boost', when='+boost')

    variant('cuda', default=True, description='Enable CUDA')
    ##depends_on('cuda', when='+cuda')

    variant('cusparse', default=True, description='Enable CUSPARSE')
    ##depends_on('cusparse', when='+cusparse')

    variant('clp', default=True, description='Enable Clp')
    ##depends_on('clp', when='+clp')

    variant('cusp', default=True, description='Enable Cusp')
    ##depends_on('cusp', when='+cusp')

    variant('foruqtk', default=True, description='Enable ForUQTK')
    ##depends_on('foruqtk', when='+foruqtk')

    variant('glpk', default=True, description='Enable GLPK')
    ##depends_on('glpk', when='+glpk')

    variant('matlablib', default=True, description='Enable MATLABLib')
    ##depends_on('matlablib', when='+matlablib')

    variant('mkl', default=True, description='Enable MKL')
    ##depends_on('mkl', when='+mkl')

    variant('thrust', default=True, description='Enable Thrust')
    ##depends_on('thrust', when='+thrust')

    variant('qpoases', default=True, description='Enable qpOASES')
    ##depends_on('qpoases', when='+qpoases')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ### Required tpl dependencies of Stokhos ###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Kokkos=ON')

        ###Optional tpl dependencies of Stokhos ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Boost', 'boost'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUDA', 'cuda'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CUSPARSE', 'cusparse'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Clp', 'clp'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Cusp', 'cusp'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ForUQTK', 'foruqtk'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_GLPK', 'glpk'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MATLABLib', 'matlablib'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MKL', 'mkl'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Thrust', 'thrust'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_qpOASES', 'qpoases'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        