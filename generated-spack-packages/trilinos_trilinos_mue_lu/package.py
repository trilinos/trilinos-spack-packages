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
    
    ### Optional TPLs variants ###
    variant(boost, default=True, description='Enable tpl')
    variant(matlab, default=True, description='Enable tpl')
    variant(amgx, default=True, description='Enable tpl')
    variant(viennacl, default=True, description='Enable tpl')
    variant(mkl, default=True, description='Enable tpl')
    variant(avatar, default=True, description='Enable tpl')
    variant(cusparse, default=True, description='Enable tpl')
    variant(magmasparse, default=True, description='Enable tpl')
    variant(mlpack, default=True, description='Enable tpl')

    ### Required TPLs automatically generated ###
    depends_on(blas)
    depends_on(lapack)

    ### Optional TPLs automatically generated ###
    depends_on(boost, when='+boost')
    depends_on(matlab, when='+matlab')
    depends_on(amgx, when='+amgx')
    depends_on(viennacl, when='+viennacl')
    depends_on(mkl, when='+mkl')
    depends_on(avatar, when='+avatar')
    depends_on(cusparse, when='+cusparse')
    depends_on(magmasparse, when='+magmasparse')
    depends_on(mlpack, when='+mlpack')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        