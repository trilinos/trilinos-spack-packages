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

class TrilinosPytrilinos2(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("keitat", "kuberry", "jfrye", "jwillenbring", "psakievich")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    # ###################### Variants ##########################

    
    # ######################### Conflicts #############################

    
    # ######################### TPLs #############################
    depends_on_trilinos_package("trilinos-stratimikos")
    depends_on_trilinos_package("trilinos-tpetra")
    depends_on_trilinos_package("trilinos-teuchos")
    depends_on_trilinos_package("trilinos-thyra")
    depends_on_trilinos_package("trilinos-muelu")
    depends_on("binder")
    depends_on("python")
    depends_on("py-pybind11")
    depends_on("py-numpy")
    depends_on("py-mpi4py")

    def trilinos_package_cmake_args(self):
        args = [
        "-DTrilinos_ENABLE_PyTrilinos2=ON",
        "-DTPL_ENABLE_Stratimikos=ON",
        "-DTPL_ENABLE_Tpetra=ON",
        "-DTPL_ENABLE_Tuechos=ON",
        "-DTPL_ENABLE_Thyra=ON",
        "-DTPL_ENABLE_MueLu=ON",
        ]

        return args

    def cmake_args(self):
        args = []
        args.extend(self.trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
