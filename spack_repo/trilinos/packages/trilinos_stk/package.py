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

    # List of automatically generated cmake arguments
    trilinos_package_auto_cmake_args=[]
    
    ###Optional tpl dependencies of STK ###
    variant('mpi', default=True, description='Enable MPI')
    depends_on('mpi', when='+mpi')

    ### Optional subpackage STKBalance ###
    variant('balance', default=True, description='Enable STKBalance')
    with when('+balance'):
        depends_on('blas')
        depends_on('lapack')
        depends_on_trilinos_package('trilinos-zoltan2-core')

    ### Optional subpackage STKCoupling ###
    variant('coupling', default=True, description='Enable STKCoupling')
    with when('+coupling'):
        depends_on('mpi')

    ### Optional subpackage STKDoc_tests ###
    variant('doc_tests', default=True, description='Enable STKDoc_tests')

    ### Optional subpackage STKEmend ###
    variant('emend', default=True, description='Enable STKEmend')
    with when('+emend'):
        depends_on('mpi')

    ### Optional subpackage STKExprEval ###
    variant('expreval', default=True, description='Enable STKExprEval')
    with when('+expreval'):
        depends_on('kokkos')

    ### Optional subpackage STKIO ###
    variant('io', default=True, description='Enable STKIO')

    ### Optional subpackage STKIntegration_tests ###
    variant('integration_tests', default=True, description='Enable STKIntegration_tests')

    ### Optional subpackage STKMath ###
    variant('math', default=True, description='Enable STKMath')
    with when('+math'):
        depends_on('kokkos')

    ### Optional subpackage STKMesh ###
    variant('mesh', default=True, description='Enable STKMesh')
    with when('+mesh'):
        depends_on('blas')
        depends_on('kokkos')
        depends_on('mpi')

    ### Optional subpackage STKMiddle_mesh ###
    variant('middle_mesh', default=True, description='Enable STKMiddle_mesh')
    with when('+middle_mesh'):
        depends_on('cdt')

    ### Optional subpackage STKMiddle_mesh_util ###
    variant('middle_mesh_util', default=True, description='Enable STKMiddle_mesh_util')
    with when('+middle_mesh_util'):
        depends_on('cdt')

    ### Optional subpackage STKNGP_TEST ###
    variant('ngp_test', default=True, description='Enable STKNGP_TEST')
    with when('+ngp_test'):
        depends_on('kokkos')

    ### Optional subpackage STKPerformance_tests ###
    variant('performance_tests', default=True, description='Enable STKPerformance_tests')

    ### Optional subpackage STKSearch ###
    variant('search', default=True, description='Enable STKSearch')
    with when('+search'):
        depends_on('kokkos')
        depends_on('mpi')

    ### Optional subpackage STKSearchUtil ###
    variant('searchutil', default=True, description='Enable STKSearchUtil')
    with when('+searchutil'):
        depends_on_trilinos_package('trilinos-intrepid2')

    ### Optional subpackage STKSimd ###
    variant('simd', default=True, description='Enable STKSimd')
    with when('+simd'):
        depends_on('kokkos')

    ### Optional subpackage STKTools ###
    variant('tools', default=True, description='Enable STKTools')

    ### Optional subpackage STKTopology ###
    variant('topology', default=True, description='Enable STKTopology')

    ### Optional subpackage STKTransfer ###
    variant('transfer', default=True, description='Enable STKTransfer')

    ### Optional subpackage STKTransferUtil ###
    variant('transferutil', default=True, description='Enable STKTransferUtil')
    with when('+transferutil'):
        depends_on('mpi')

    ### Optional subpackage STKUnit_test_utils ###
    variant('unit_test_utils', default=True, description='Enable STKUnit_test_utils')
    with when('+unit_test_utils'):
        depends_on('mpi')

    ### Optional subpackage STKUnit_tests ###
    variant('unit_tests', default=True, description='Enable STKUnit_tests')

    ### Optional subpackage STKUtil ###
    variant('util', default=True, description='Enable STKUtil')
    with when('+util'):
        depends_on('boost')
        depends_on('kokkos')
        depends_on('mpi')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ###Optional tpl dependencies of STK ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'mpi'))

        ### Optional subpackage STKBalance ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKBalance', 'balance'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_BLAS', 'balance'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_LAPACK', 'balance'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Zoltan2Core', 'balance'))

        ### Optional subpackage STKCoupling ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKCoupling', 'coupling'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'coupling'))

        ### Optional subpackage STKDoc_tests ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKDoc_tests', 'doc_tests'))

        ### Optional subpackage STKEmend ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKEmend', 'emend'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'emend'))

        ### Optional subpackage STKExprEval ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKExprEval', 'expreval'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'expreval'))

        ### Optional subpackage STKIO ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKIO', 'io'))

        ### Optional subpackage STKIntegration_tests ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKIntegration_tests', 'integration_tests'))

        ### Optional subpackage STKMath ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKMath', 'math'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'math'))

        ### Optional subpackage STKMesh ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKMesh', 'mesh'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_BLAS', 'mesh'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'mesh'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'mesh'))

        ### Optional subpackage STKMiddle_mesh ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKMiddle_mesh', 'middle_mesh'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CDT', 'middle_mesh'))

        ### Optional subpackage STKMiddle_mesh_util ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKMiddle_mesh_util', 'middle_mesh_util'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CDT', 'middle_mesh_util'))

        ### Optional subpackage STKNGP_TEST ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKNGP_TEST', 'ngp_test'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'ngp_test'))

        ### Optional subpackage STKPerformance_tests ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKPerformance_tests', 'performance_tests'))

        ### Optional subpackage STKSearch ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKSearch', 'search'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'search'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'search'))

        ### Optional subpackage STKSearchUtil ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKSearchUtil', 'searchutil'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Intrepid2', 'searchutil'))

        ### Optional subpackage STKSimd ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKSimd', 'simd'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'simd'))

        ### Optional subpackage STKTools ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKTools', 'tools'))

        ### Optional subpackage STKTopology ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKTopology', 'topology'))

        ### Optional subpackage STKTransfer ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKTransfer', 'transfer'))

        ### Optional subpackage STKTransferUtil ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKTransferUtil', 'transferutil'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'transferutil'))

        ### Optional subpackage STKUnit_test_utils ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKUnit_test_utils', 'unit_test_utils'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'unit_test_utils'))

        ### Optional subpackage STKUnit_tests ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKUnit_tests', 'unit_tests'))

        ### Optional subpackage STKUtil ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_STKUtil', 'util'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Boost', 'util'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'util'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'util'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        