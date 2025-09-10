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

class TrilinosSeacas(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    
    ### Variants automatically generated from optional subpackages ###
    variant(exodus_for, default=True, description='Enable SEACASExodus_for')
    variant(exoiiv2for32, default=True, description='Enable SEACASExoIIv2for32')
    variant(nemesis, default=True, description='Enable SEACASNemesis')
    variant(ioss, default=True, description='Enable SEACASIoss')
    variant(chaco, default=True, description='Enable SEACASChaco')
    variant(aprepro_lib, default=True, description='Enable SEACASAprepro_lib')
    variant(supes, default=True, description='Enable SEACASSupes')
    variant(suplib, default=True, description='Enable SEACASSuplib')
    variant(suplibc, default=True, description='Enable SEACASSuplibC')
    variant(suplibcpp, default=True, description='Enable SEACASSuplibCpp')
    variant(svdi, default=True, description='Enable SEACASSVDI')
    variant(plt, default=True, description='Enable SEACASPLT')
    variant(algebra, default=True, description='Enable SEACASAlgebra')
    variant(aprepro, default=True, description='Enable SEACASAprepro')
    variant(blot, default=True, description='Enable SEACASBlot')
    variant(conjoin, default=True, description='Enable SEACASConjoin')
    variant(ejoin, default=True, description='Enable SEACASEjoin')
    variant(epu, default=True, description='Enable SEACASEpu')
    variant(cpup, default=True, description='Enable SEACASCpup')
    variant(exo2mat, default=True, description='Enable SEACASExo2mat')
    variant(exodiff, default=True, description='Enable SEACASExodiff')
    variant(exomatlab, default=True, description='Enable SEACASExomatlab')
    variant(exotxt, default=True, description='Enable SEACASExotxt')
    variant(exo_format, default=True, description='Enable SEACASExo_format')
    variant(ex1ex2v2, default=True, description='Enable SEACASEx1ex2v2')
    variant(exotec2, default=True, description='Enable SEACASExotec2')
    variant(fastq, default=True, description='Enable SEACASFastq')
    variant(gjoin, default=True, description='Enable SEACASGjoin')
    variant(gen3d, default=True, description='Enable SEACASGen3D')
    variant(genshell, default=True, description='Enable SEACASGenshell')
    variant(grepos, default=True, description='Enable SEACASGrepos')
    variant(explore, default=True, description='Enable SEACASExplore')
    variant(mapvarlib, default=True, description='Enable SEACASMapvarlib')
    variant(mapvar, default=True, description='Enable SEACASMapvar')
    variant(mapvar-kd, default=True, description='Enable SEACASMapvar-kd')
    variant(mat2exo, default=True, description='Enable SEACASMat2exo')
    variant(nas2exo, default=True, description='Enable SEACASNas2exo')
    variant(zellij, default=True, description='Enable SEACASZellij')
    variant(nemslice, default=True, description='Enable SEACASNemslice')
    variant(nemspread, default=True, description='Enable SEACASNemspread')
    variant(numbers, default=True, description='Enable SEACASNumbers')
    variant(slice, default=True, description='Enable SEACASSlice')
    variant(txtexo, default=True, description='Enable SEACASTxtexo')
    variant(ex2ex1v2, default=True, description='Enable SEACASEx2ex1v2')

    ### Optional TPLs variants ###
    variant(mpi, default=True, description='Enable tpl')

    ### Optional TPLs automatically generated ###
    depends_on(mpi, when='+mpi')

    def generated_trilinos_package_cmake_args(self):
        # auto generated cmake arguments
        generated_cmake_options = []
        generated_cmake_options.append(-DTrilinos_ENABLE_SEACASExodus=ON)

        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExodus_for', exodus_for))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExoIIv2for32', exoiiv2for32))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNemesis', nemesis))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASIoss', ioss))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASChaco', chaco))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASAprepro_lib', aprepro_lib))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSupes', supes))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSuplib', suplib))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSuplibC', suplibc))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSuplibCpp', suplibcpp))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSVDI', svdi))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASPLT', plt))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASAlgebra', algebra))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASAprepro', aprepro))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASBlot', blot))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASConjoin', conjoin))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEjoin', ejoin))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEpu', epu))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASCpup', cpup))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExo2mat', exo2mat))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExodiff', exodiff))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExomatlab', exomatlab))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExotxt', exotxt))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExo_format', exo_format))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEx1ex2v2', ex1ex2v2))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExotec2', exotec2))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASFastq', fastq))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGjoin', gjoin))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGen3D', gen3d))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGenshell', genshell))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGrepos', grepos))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExplore', explore))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMapvarlib', mapvarlib))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMapvar', mapvar))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMapvar-kd', mapvar-kd))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMat2exo', mat2exo))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNas2exo', nas2exo))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASZellij', zellij))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNemslice', nemslice))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNemspread', nemspread))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNumbers', numbers))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSlice', slice))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASTxtexo', txtexo))
        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEx2ex1v2', ex2ex1v2))

        return generated_cmake_options
   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        