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
    
    ### Variants automatically generated from optional trilinos subpackages ###
    variant('thyratpetraadapters', default=True, description='Enable ThyraTpetraAdapters')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-amesos', default=True, description='Enable Amesos support')
    variant('trilinos-amesos2', default=True, description='Enable Amesos2 support')
    variant('trilinos-belos', default=True, description='Enable Belos support')
    variant('trilinos-epetra', default=True, description='Enable Epetra support')
    variant('trilinos-epetra-ext', default=True, description='Enable EpetraExt support')
    variant('trilinos-ifpack', default=True, description='Enable Ifpack support')
    variant('trilinos-ifpack2', default=True, description='Enable Ifpack2 support')
    variant('trilinos-intrepid2', default=True, description='Enable Intrepid2 support')
    variant('trilinos-isorropia', default=True, description='Enable Isorropia support')
    variant('trilinos-ml', default=True, description='Enable ML support')
    variant('trilinos-stratimikos', default=True, description='Enable Stratimikos support')
    variant('trilinos-teko', default=True, description='Enable Teko support')
    variant('trilinos-thyra', default=True, description='Enable Thyra support')
    variant('trilinos-zoltan', default=True, description='Enable Zoltan support')
    variant('trilinos-zoltan2-core', default=True, description='Enable Zoltan2Core support')

    ### Optional TPLs variants ###
    variant('amgx', default=True, description='Enable AmgX')
    variant('avatar', default=True, description='Enable Avatar')
    variant('boost', default=True, description='Enable Boost')
    variant('cusparse', default=True, description='Enable CUSPARSE')
    variant('magmasparse', default=True, description='Enable MAGMASparse')
    variant('matlab', default=True, description='Enable MATLAB')
    variant('mkl', default=True, description='Enable MKL')
    variant('viennacl', default=True, description='Enable ViennaCL')
    variant('mlpack', default=True, description='Enable mlpack')

    ### Required Trilinos packages ###
    depends_on_trilinos_package('trilinos-kokkos-kernels')
    depends_on_trilinos_package('trilinos-teuchos')
    depends_on_trilinos_package('trilinos-tpetra')
    depends_on_trilinos_package('trilinos-xpetra')

    ### Optional Trilinos packages ###
    depends_on_trilinos_package('trilinos-amesos', when='+trilinos-amesos')
    depends_on_trilinos_package('trilinos-amesos2', when='+trilinos-amesos2')
    depends_on_trilinos_package('trilinos-belos', when='+trilinos-belos')
    depends_on_trilinos_package('trilinos-epetra', when='+trilinos-epetra')
    depends_on_trilinos_package('trilinos-epetra-ext', when='+trilinos-epetra-ext')
    depends_on_trilinos_package('trilinos-ifpack', when='+trilinos-ifpack')
    depends_on_trilinos_package('trilinos-ifpack2', when='+trilinos-ifpack2')
    depends_on_trilinos_package('trilinos-intrepid2', when='+trilinos-intrepid2')
    depends_on_trilinos_package('trilinos-isorropia', when='+trilinos-isorropia')
    depends_on_trilinos_package('trilinos-ml', when='+trilinos-ml')
    depends_on_trilinos_package('trilinos-stratimikos', when='+trilinos-stratimikos')
    depends_on_trilinos_package('trilinos-teko', when='+trilinos-teko')
    depends_on_trilinos_package('trilinos-thyra', when='+trilinos-thyra')
    depends_on_trilinos_package('trilinos-zoltan', when='+trilinos-zoltan')
    depends_on_trilinos_package('trilinos-zoltan2-core', when='+trilinos-zoltan2-core')

    ### Required TPLs automatically generated ###
    depends_on(blas)
    depends_on(lapack)

    ### Optional TPLs automatically generated ###
    depends_on(amgx, when='+amgx')
    depends_on(avatar, when='+avatar')
    depends_on(boost, when='+boost')
    depends_on(cusparse, when='+cusparse')
    depends_on(magmasparse, when='+magmasparse')
    depends_on(matlab, when='+matlab')
    depends_on(mkl, when='+mkl')
    depends_on(viennacl, when='+viennacl')
    depends_on(mlpack, when='+mlpack')


    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        