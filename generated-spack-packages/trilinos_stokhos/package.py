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
    variant('foruqtk', default=True, description='Enable tpl')
    variant('cuda', default=True, description='Enable tpl')
    variant('thrust', default=True, description='Enable tpl')
    variant('cusp', default=True, description='Enable tpl')
    variant('cusparse', default=True, description='Enable tpl')
    variant('clp', default=True, description='Enable tpl')
    variant('glpk', default=True, description='Enable tpl')
    variant('qpoases', default=True, description='Enable tpl')
    variant('boost', default=True, description='Enable tpl')
    variant('matlablib', default=True, description='Enable tpl')
    variant('mkl', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-kokkos-kernels', default=True, description='Enable KokkosKernels support')
    variant('trilinos-epetra-ext', default=True, description='Enable EpetraExt support')
    variant('trilinos-ifpack', default=True, description='Enable Ifpack support')
    variant('trilinos-ml', default=True, description='Enable ML support')
    variant('trilinos-anasazi', default=True, description='Enable Anasazi support')
    variant('trilinos-sacado', default=True, description='Enable Sacado support')
    variant('trilinos-nox', default=True, description='Enable NOX support')
    variant('trilinos-isorropia', default=True, description='Enable Isorropia support')
    variant('trilinos-kokkos-kernels', default=True, description='Enable KokkosKernels support')
    variant('trilinos-teuchos-kokkos-comm', default=True, description='Enable TeuchosKokkosComm support')
    variant('trilinos-tpetra', default=True, description='Enable Tpetra support')
    variant('trilinos-ifpack2', default=True, description='Enable Ifpack2 support')
    variant('trilinos-mue-lu', default=True, description='Enable MueLu support')
    variant('trilinos-belos', default=True, description='Enable Belos support')
    variant('trilinos-amesos2', default=True, description='Enable Amesos2 support')
    variant('trilinos-thyra', default=True, description='Enable Thyra support')
    variant('trilinos-xpetra', default=True, description='Enable Xpetra support')

    ### Required Trilinos packages ###
    depends_on_trilinos_package(trilinos-teuchos)
    depends_on_trilinos_package(trilinos-kokkos)

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
        