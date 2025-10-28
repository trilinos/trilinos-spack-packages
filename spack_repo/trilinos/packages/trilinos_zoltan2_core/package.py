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

class TrilinosZoltan2Core(TrilinosBaseClass):
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
    
    ###Optional tpl dependencies of Zoltan2Core ###
    variant('amd', default=True, description='Enable AMD')
    depends_on('amd', when='+amd')

    variant('metis', default=True, description='Enable METIS')
    depends_on('metis', when='+metis')

    variant('ovis', default=True, description='Enable OVIS')
    depends_on('ovis', when='+ovis')

    variant('patoh', default=True, description='Enable PaToH')
    depends_on('patoh', when='+patoh')

    variant('parmetis', default=True, description='Enable ParMETIS')
    depends_on('parmetis', when='+parmetis')

    variant('pulp', default=True, description='Enable PuLP')
    depends_on('pulp', when='+pulp')

    variant('sarma', default=True, description='Enable SARMA')
    depends_on('sarma', when='+sarma')

    variant('scotch', default=True, description='Enable Scotch')
    depends_on('scotch', when='+scotch')

    variant('topomanager', default=True, description='Enable TopoManager')
    depends_on('topomanager', when='+topomanager')

    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ###Optional tpl dependencies of Zoltan2Core ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_AMD', 'amd'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_METIS', 'metis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_OVIS', 'ovis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PaToH', 'patoh'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ParMETIS', 'parmetis'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_PuLP', 'pulp'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_SARMA', 'sarma'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Scotch', 'scotch'))

        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_TopoManager', 'topomanager'))

        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        