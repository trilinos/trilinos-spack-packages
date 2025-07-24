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

    maintainers("keitat", "kuberry", "jfrye", "jwillenbring", "psakievich")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    # ###################### Variants ##########################
    variant("adapters-stk", default=False, description="Enable Adapters STK")
    variant("disc-fe", default=False, description="Enable Disc FE")
    variant("dof-mgr", default=False, description="Enable DOF MGR")
    variant("expr-eval", default=False, description="Enable Expr Eval")
    variant("mini-em", default=False, description="Enable AMini EM")

    # ######################### Conflicts #############################
    conflicts("~mpi", when="+mini-em", msg="mpi must be enabled for mini EM to build")
    
    # ######################### TPLs #############################
    depends_on_trilinos_package("trilinos-teuchos")
    depends_on_trilinos_package("trilinos-tpetra")
    depends_on("kokkos-kernels")
    depends_on("trilinos-teuchos+mpi", when="+mpi")
    depends_on("trilinos-tpetra+mpi", when="+mpi")

    def trilinos_package_cmake_args(self):
        args = [
        "-DTrilinos_ENABLE_Panzer=ON",
        "-DTPL_ENABLE_KokkosKernels=ON",
        "-DTPL_ENABLE_Teuchos=ON",
        "-DTPL_ENABLE_Tpetra=ON",
        ]
        
        args.append(self.define_from_variant("Trilinos_ENABLE_PanzerAdaptersSTK", "adapters-stk"))
        args.append(self.define_from_variant("Trilinos_ENABLE_PanzerDiscFE", "disc-fe"))
        args.append(self.define_from_variant("Trilinos_ENABLE_PanzerDofMgr", "dof-mgr"))
        args.append(self.define_from_variant("Trilinos_ENABLE_PanzerExprEval", "expr-eval"))
        args.append(self.define_from_variant("Trilinos_ENABLE_PanzerMiniEM", "mini-em"))

        return args

    def cmake_args(self):
        args = []
        args.extend(self.trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args


    
