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

class TrilinosPanzer(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Variants automatically generated from optional subpackages of Panzer ###
    variant('miniem', default=True, description='Enable PanzerMiniEM')
    variant('dofmgr', default=True, description='Enable PanzerDofMgr')
    variant('discfe', default=True, description='Enable PanzerDiscFE')
    variant('adaptersstk', default=True, description='Enable PanzerAdaptersSTK')
    variant('expreval', default=True, description='Enable PanzerExprEval')

