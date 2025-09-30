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
    
    ### Variants automatically generated from optional trilinos subpackages ###
    variant('thyratpetraadapters', default=True, description='Enable ThyraTpetraAdapters')

    ### Optional TPLs variants ###
    variant('cusparse', default=True, description='Enable tpl')
    variant('boost', default=True, description='Enable tpl')
    variant('avatar', default=True, description='Enable tpl')
    variant('mkl', default=True, description='Enable tpl')
    variant('magmasparse', default=True, description='Enable tpl')
    variant('viennacl', default=True, description='Enable tpl')
    variant('amgx', default=True, description='Enable tpl')
    variant('mlpack', default=True, description='Enable tpl')
    variant('matlab', default=True, description='Enable tpl')

    ### Optional Trilinos dependencies variants ###
    variant('trilinos-epetra-ext', default=True, description='Enable EpetraExt support')
    variant('trilinos-ifpack2', default=True, description='Enable Ifpack2 support')
    variant('trilinos-epetra', default=True, description='Enable Epetra support')
    variant('trilinos-belos', default=True, description='Enable Belos support')
    variant('trilinos-amesos', default=True, description='Enable Amesos support')
    variant('trilinos-amesos2', default=True, description='Enable Amesos2 support')
    variant('trilinos-intrepid2', default=True, description='Enable Intrepid2 support')
    variant('trilinos-ml', default=True, description='Enable ML support')
    variant('trilinos-zoltan', default=True, description='Enable Zoltan support')
    variant('trilinos-ifpack', default=True, description='Enable Ifpack support')
    variant('trilinos-isorropia', default=True, description='Enable Isorropia support')
    variant('trilinos-thyra', default=True, description='Enable Thyra support')
    variant('trilinos-zoltan2-core', default=True, description='Enable Zoltan2Core support')
    variant('trilinos-stratimikos', default=True, description='Enable Stratimikos support')
    variant('trilinos-teko', default=True, description='Enable Teko support')

