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

class TrilinosStk(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Variants automatically generated from optional subpackages ###
    variant(util, default=True, description='Enable STKUtil')
    variant(emend, default=True, description='Enable STKEmend')
    variant(coupling, default=True, description='Enable STKCoupling')
    variant(math, default=True, description='Enable STKMath')
    variant(simd, default=True, description='Enable STKSimd')
    variant(ngp_test, default=True, description='Enable STKNGP_TEST')
    variant(expreval, default=True, description='Enable STKExprEval')
    variant(topology, default=True, description='Enable STKTopology')
    variant(search, default=True, description='Enable STKSearch')
    variant(middle_mesh, default=True, description='Enable STKMiddle_mesh')
    variant(transfer, default=True, description='Enable STKTransfer')
    variant(mesh, default=True, description='Enable STKMesh')
    variant(io, default=True, description='Enable STKIO')
    variant(searchutil, default=True, description='Enable STKSearchUtil')
    variant(transferutil, default=True, description='Enable STKTransferUtil')
    variant(middle_mesh_util, default=True, description='Enable STKMiddle_mesh_util')
    variant(tools, default=True, description='Enable STKTools')
    variant(balance, default=True, description='Enable STKBalance')
    variant(unit_test_utils, default=True, description='Enable STKUnit_test_utils')
    variant(unit_tests, default=True, description='Enable STKUnit_tests')
    variant(doc_tests, default=True, description='Enable STKDoc_tests')
    variant(integration_tests, default=True, description='Enable STKIntegration_tests')
    variant(performance_tests, default=True, description='Enable STKPerformance_tests')

    ### Optional TPLs variants ###
    variant(mpi, default=True, description='Enable tpl')

    ### Optional TPLs automatically generated ###
    depends_on(mpi, when='+mpi')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKUtil', util))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKEmend', emend))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKCoupling', coupling))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKMath', math))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKSimd', simd))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKNGP_TEST', ngp_test))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKExprEval', expreval))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKTopology', topology))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKSearch', search))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKMiddle_mesh', middle_mesh))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKTransfer', transfer))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKMesh', mesh))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKIO', io))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKSearchUtil', searchutil))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKTransferUtil', transferutil))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKMiddle_mesh_util', middle_mesh_util))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKTools', tools))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKBalance', balance))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKUnit_test_utils', unit_test_utils))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKUnit_tests', unit_tests))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKDoc_tests', doc_tests))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKIntegration_tests', integration_tests))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_STKPerformance_tests', performance_tests))

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        