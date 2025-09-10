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
    
    ### Optional TPLs variants ###
    variant(foruqtk, default=True, description='Enable tpl')
    variant(cuda, default=True, description='Enable tpl')
    variant(thrust, default=True, description='Enable tpl')
    variant(cusp, default=True, description='Enable tpl')
    variant(cusparse, default=True, description='Enable tpl')
    variant(clp, default=True, description='Enable tpl')
    variant(glpk, default=True, description='Enable tpl')
    variant(qpoases, default=True, description='Enable tpl')
    variant(boost, default=True, description='Enable tpl')
    variant(matlablib, default=True, description='Enable tpl')
    variant(mkl, default=True, description='Enable tpl')

    ### Optional TPLs automatically generated ###
    depends_on(foruqtk, when='+foruqtk')
    depends_on(cuda, when='+cuda')
    depends_on(thrust, when='+thrust')
    depends_on(cusp, when='+cusp')
    depends_on(cusparse, when='+cusparse')
    depends_on(clp, when='+clp')
    depends_on(glpk, when='+glpk')
    depends_on(qpoases, when='+qpoases')
    depends_on(boost, when='+boost')
    depends_on(matlablib, when='+matlablib')
    depends_on(mkl, when='+mkl')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        