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
    
    ### Optional TPLs variants ###
    variant(superludist, default=True, description='Enable tpl')
    variant(parmetis, default=True, description='Enable tpl')
    variant(umfpack, default=True, description='Enable tpl')
    variant(superlu, default=True, description='Enable tpl')
    variant(blacs, default=True, description='Enable tpl')
    variant(scalapack, default=True, description='Enable tpl')
    variant(mumps, default=True, description='Enable tpl')
    variant(taucs, default=True, description='Enable tpl')
    variant(css_mkl, default=True, description='Enable tpl')
    variant(pardiso_mkl, default=True, description='Enable tpl')
    variant(pardiso, default=True, description='Enable tpl')
    variant(csparse, default=True, description='Enable tpl')

    ### Optional TPLs automatically generated ###
    depends_on(superludist, when='+superludist')
    depends_on(parmetis, when='+parmetis')
    depends_on(umfpack, when='+umfpack')
    depends_on(superlu, when='+superlu')
    depends_on(blacs, when='+blacs')
    depends_on(scalapack, when='+scalapack')
    depends_on(mumps, when='+mumps')
    depends_on(taucs, when='+taucs')
    depends_on(css_mkl, when='+css_mkl')
    depends_on(pardiso_mkl, when='+pardiso_mkl')
    depends_on(pardiso, when='+pardiso')
    depends_on(csparse, when='+csparse')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        