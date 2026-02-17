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

    # List of automatically generated cmake arguments
    trilinos_package_auto_cmake_args=[]
    
    ###Optional tpl dependencies of SEACAS ###
    variant('mpi', default=True, description='Enable MPI')
    ##depends_on('mpi', when='+mpi')

    ### Required subpackage SEACASExodus ###

    ### Required tpls of SEACAS from subpackage requirements###
    #depends_on('hdf5')
    #depends_on('mpi')
    #depends_on('netcdf')
    #depends_on('pnetcdf')
    #depends_on('pthread')

    ### Optional subpackage SEACASAlgebra ###
    variant('algebra', default=True, description='Enable SEACASAlgebra')

    ### Optional subpackage SEACASAprepro ###
    variant('aprepro', default=True, description='Enable SEACASAprepro')

    ### Optional subpackage SEACASAprepro_lib ###
    variant('aprepro_lib', default=True, description='Enable SEACASAprepro_lib')

    ### Optional subpackage SEACASBlot ###
    variant('blot', default=True, description='Enable SEACASBlot')

    ### Optional subpackage SEACASChaco ###
    variant('chaco', default=True, description='Enable SEACASChaco')

    ### Optional subpackage SEACASConjoin ###
    variant('conjoin', default=True, description='Enable SEACASConjoin')

    ### Optional subpackage SEACASCpup ###
    variant('cpup', default=True, description='Enable SEACASCpup')

    ### Optional subpackage SEACASEjoin ###
    variant('ejoin', default=True, description='Enable SEACASEjoin')

    ### Optional subpackage SEACASEpu ###
    variant('epu', default=True, description='Enable SEACASEpu')

    ### Optional subpackage SEACASEx1ex2v2 ###
    variant('ex1ex2v2', default=True, description='Enable SEACASEx1ex2v2')

    ### Optional subpackage SEACASEx2ex1v2 ###
    variant('ex2ex1v2', default=True, description='Enable SEACASEx2ex1v2')

    ### Optional subpackage SEACASExo2mat ###
    variant('exo2mat', default=True, description='Enable SEACASExo2mat')
    variant('matio', default=True, description='Enable TPL Matio')
    depends_on('matio', when='+matio')
    #conflicts('+exo2mat~matio')

    ### Optional subpackage SEACASExoIIv2for32 ###
    variant('exoiiv2for32', default=True, description='Enable SEACASExoIIv2for32')
    variant('netcdf', default=True, description='Enable TPL Netcdf')
    depends_on('netcdf', when='+netcdf')
    #conflicts('+exoiiv2for32~netcdf')

    ### Optional subpackage SEACASExo_format ###
    variant('exo_format', default=True, description='Enable SEACASExo_format')

    ### Optional subpackage SEACASExodiff ###
    variant('exodiff', default=True, description='Enable SEACASExodiff')

    ### Optional subpackage SEACASExodus_for ###
    variant('exodus_for', default=True, description='Enable SEACASExodus_for')
    variant('netcdf', default=True, description='Enable TPL Netcdf')
    depends_on('netcdf', when='+netcdf')
    #conflicts('+exodus_for~netcdf')

    ### Optional subpackage SEACASExomatlab ###
    variant('exomatlab', default=True, description='Enable SEACASExomatlab')

    ### Optional subpackage SEACASExotec2 ###
    variant('exotec2', default=True, description='Enable SEACASExotec2')

    ### Optional subpackage SEACASExotxt ###
    variant('exotxt', default=True, description='Enable SEACASExotxt')

    ### Optional subpackage SEACASExplore ###
    variant('explore', default=True, description='Enable SEACASExplore')

    ### Optional subpackage SEACASFastq ###
    variant('fastq', default=True, description='Enable SEACASFastq')

    ### Optional subpackage SEACASGen3D ###
    variant('gen3d', default=True, description='Enable SEACASGen3D')

    ### Optional subpackage SEACASGenshell ###
    variant('genshell', default=True, description='Enable SEACASGenshell')

    ### Optional subpackage SEACASGjoin ###
    variant('gjoin', default=True, description='Enable SEACASGjoin')

    ### Optional subpackage SEACASGrepos ###
    variant('grepos', default=True, description='Enable SEACASGrepos')

    ### Optional subpackage SEACASIoss ###
    variant('ioss', default=True, description='Enable SEACASIoss')
    variant('adios2', default=True, description='Enable TPL ADIOS2')
    depends_on('adios2', when='+adios2')
    #conflicts('+ioss~adios2')
    variant('awssdk', default=True, description='Enable TPL AWSSDK')
    depends_on('awssdk', when='+awssdk')
    #conflicts('+ioss~awssdk')
    variant('cgns', default=True, description='Enable TPL CGNS')
    depends_on('cgns', when='+cgns')
    #conflicts('+ioss~cgns')
    variant('catalyst2', default=True, description='Enable TPL Catalyst2')
    depends_on('catalyst2', when='+catalyst2')
    #conflicts('+ioss~catalyst2')
    variant('cereal', default=True, description='Enable TPL Cereal')
    depends_on('cereal', when='+cereal')
    #conflicts('+ioss~cereal')
    variant('dllib', default=True, description='Enable TPL DLlib')
    depends_on('dllib', when='+dllib')
    #conflicts('+ioss~dllib')
    variant('datawarp', default=True, description='Enable TPL DataWarp')
    depends_on('datawarp', when='+datawarp')
    #conflicts('+ioss~datawarp')
    variant('faodel', default=True, description='Enable TPL Faodel')
    depends_on('faodel', when='+faodel')
    #conflicts('+ioss~faodel')
    variant('hdf5', default=True, description='Enable TPL HDF5')
    depends_on('hdf5', when='+hdf5')
    #conflicts('+ioss~hdf5')
    variant('parmetis', default=True, description='Enable TPL ParMETIS')
    depends_on('parmetis', when='+parmetis')
    #conflicts('+ioss~parmetis')
    variant('pthread', default=True, description='Enable TPL Pthread')
    depends_on('pthread', when='+pthread')
    #conflicts('+ioss~pthread')
    variant('kokkos', default=True, description='Enable Kokkos')
    depends_on_trilinos_package('trilinos-kokkos')
    #conflicts('+ioss~kokkos')
    variant('pamgen', default=True, description='Enable Pamgen')
    depends_on_trilinos_package('trilinos-pamgen')
    #conflicts('+ioss~pamgen')
    variant('zoltan', default=True, description='Enable Zoltan')
    depends_on_trilinos_package('trilinos-zoltan')
    #conflicts('+ioss~zoltan')

    ### Optional subpackage SEACASMapvar ###
    variant('mapvar', default=True, description='Enable SEACASMapvar')

    ### Optional subpackage SEACASMapvar-kd ###
    variant('mapvar-kd', default=True, description='Enable SEACASMapvar-kd')

    ### Optional subpackage SEACASMapvarlib ###
    variant('mapvarlib', default=True, description='Enable SEACASMapvarlib')

    ### Optional subpackage SEACASMat2exo ###
    variant('mat2exo', default=True, description='Enable SEACASMat2exo')
    variant('matio', default=True, description='Enable TPL Matio')
    depends_on('matio', when='+matio')
    #conflicts('+mat2exo~matio')

    ### Optional subpackage SEACASNas2exo ###
    variant('nas2exo', default=True, description='Enable SEACASNas2exo')

    ### Optional subpackage SEACASNemesis ###
    variant('nemesis', default=True, description='Enable SEACASNemesis')
    variant('hdf5', default=True, description='Enable TPL HDF5')
    depends_on('hdf5', when='+hdf5')
    #conflicts('+nemesis~hdf5')
    variant('mpi', default=True, description='Enable TPL MPI')
    depends_on('mpi', when='+mpi')
    #conflicts('+nemesis~mpi')
    variant('netcdf', default=True, description='Enable TPL Netcdf')
    depends_on('netcdf', when='+netcdf')
    #conflicts('+nemesis~netcdf')
    variant('pnetcdf', default=True, description='Enable TPL Pnetcdf')
    depends_on('pnetcdf', when='+pnetcdf')
    #conflicts('+nemesis~pnetcdf')
    variant('pthread', default=True, description='Enable TPL Pthread')
    depends_on('pthread', when='+pthread')
    #conflicts('+nemesis~pthread')

    ### Optional subpackage SEACASNemslice ###
    variant('nemslice', default=True, description='Enable SEACASNemslice')
    variant('zoltan', default=True, description='Enable Zoltan')
    depends_on_trilinos_package('trilinos-zoltan')
    #conflicts('+nemslice~zoltan')

    ### Optional subpackage SEACASNemspread ###
    variant('nemspread', default=True, description='Enable SEACASNemspread')

    ### Optional subpackage SEACASNumbers ###
    variant('numbers', default=True, description='Enable SEACASNumbers')

    ### Optional subpackage SEACASPLT ###
    variant('plt', default=True, description='Enable SEACASPLT')

    ### Optional subpackage SEACASSVDI ###
    variant('svdi', default=True, description='Enable SEACASSVDI')
    variant('x11', default=True, description='Enable TPL X11')
    depends_on('x11', when='+x11')
    #conflicts('+svdi~x11')

    ### Optional subpackage SEACASSlice ###
    variant('slice', default=True, description='Enable SEACASSlice')
    variant('metis', default=True, description='Enable TPL METIS')
    depends_on('metis', when='+metis')
    #conflicts('+slice~metis')
    variant('zoltan', default=True, description='Enable Zoltan')
    depends_on_trilinos_package('trilinos-zoltan')
    #conflicts('+slice~zoltan')

    ### Optional subpackage SEACASSupes ###
    variant('supes', default=True, description='Enable SEACASSupes')

    ### Optional subpackage SEACASSuplib ###
    variant('suplib', default=True, description='Enable SEACASSuplib')

    ### Optional subpackage SEACASSuplibC ###
    variant('suplibc', default=True, description='Enable SEACASSuplibC')

    ### Optional subpackage SEACASSuplibCpp ###
    variant('suplibcpp', default=True, description='Enable SEACASSuplibCpp')

    ### Optional subpackage SEACASTxtexo ###
    variant('txtexo', default=True, description='Enable SEACASTxtexo')

    ### Optional subpackage SEACASZellij ###
    variant('zellij', default=True, description='Enable SEACASZellij')
    variant('zoltan', default=True, description='Enable Zoltan')
    depends_on_trilinos_package('trilinos-zoltan')
    #conflicts('+zellij~zoltan')


    def generated_trilinos_package_cmake_args(self):
        ### auto generated cmake arguments
        trilinos_package_auto_cmake_args = []
        ###Optional tpl dependencies of SEACAS ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'mpi'))

        ### Required subpackage SEACASExodus ###
        trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_SEACASExodus=ON')

        ### Required tpls of SEACAS from subpackage requirements###
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_HDF5=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_MPI=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Netcdf=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Pnetcdf=ON')
        trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_Pthread=ON')

        ### Optional subpackage SEACASAlgebra ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASAlgebra', 'algebra'))

        ### Optional subpackage SEACASAprepro ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASAprepro', 'aprepro'))

        ### Optional subpackage SEACASAprepro_lib ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASAprepro_lib', 'aprepro_lib'))

        ### Optional subpackage SEACASBlot ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASBlot', 'blot'))

        ### Optional subpackage SEACASChaco ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASChaco', 'chaco'))

        ### Optional subpackage SEACASConjoin ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASConjoin', 'conjoin'))

        ### Optional subpackage SEACASCpup ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASCpup', 'cpup'))

        ### Optional subpackage SEACASEjoin ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEjoin', 'ejoin'))

        ### Optional subpackage SEACASEpu ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEpu', 'epu'))

        ### Optional subpackage SEACASEx1ex2v2 ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEx1ex2v2', 'ex1ex2v2'))

        ### Optional subpackage SEACASEx2ex1v2 ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASEx2ex1v2', 'ex2ex1v2'))

        ### Optional subpackage SEACASExo2mat ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExo2mat', 'exo2mat'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Matio', 'exo2mat'))

        ### Optional subpackage SEACASExoIIv2for32 ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExoIIv2for32', 'exoiiv2for32'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Netcdf', 'exoiiv2for32'))

        ### Optional subpackage SEACASExo_format ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExo_format', 'exo_format'))

        ### Optional subpackage SEACASExodiff ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExodiff', 'exodiff'))

        ### Optional subpackage SEACASExodus_for ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExodus_for', 'exodus_for'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Netcdf', 'exodus_for'))

        ### Optional subpackage SEACASExomatlab ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExomatlab', 'exomatlab'))

        ### Optional subpackage SEACASExotec2 ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExotec2', 'exotec2'))

        ### Optional subpackage SEACASExotxt ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExotxt', 'exotxt'))

        ### Optional subpackage SEACASExplore ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASExplore', 'explore'))

        ### Optional subpackage SEACASFastq ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASFastq', 'fastq'))

        ### Optional subpackage SEACASGen3D ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGen3D', 'gen3d'))

        ### Optional subpackage SEACASGenshell ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGenshell', 'genshell'))

        ### Optional subpackage SEACASGjoin ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGjoin', 'gjoin'))

        ### Optional subpackage SEACASGrepos ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASGrepos', 'grepos'))

        ### Optional subpackage SEACASIoss ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASIoss', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ADIOS2', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_AWSSDK', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_CGNS', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Catalyst2', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Cereal', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_DLlib', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_DataWarp', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Faodel', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_HDF5', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_ParMETIS', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Pthread', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Kokkos', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Pamgen', 'ioss'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Zoltan', 'ioss'))

        ### Optional subpackage SEACASMapvar ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMapvar', 'mapvar'))

        ### Optional subpackage SEACASMapvar-kd ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMapvar-kd', 'mapvar-kd'))

        ### Optional subpackage SEACASMapvarlib ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMapvarlib', 'mapvarlib'))

        ### Optional subpackage SEACASMat2exo ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASMat2exo', 'mat2exo'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Matio', 'mat2exo'))

        ### Optional subpackage SEACASNas2exo ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNas2exo', 'nas2exo'))

        ### Optional subpackage SEACASNemesis ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNemesis', 'nemesis'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_HDF5', 'nemesis'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_MPI', 'nemesis'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Netcdf', 'nemesis'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Pnetcdf', 'nemesis'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Pthread', 'nemesis'))

        ### Optional subpackage SEACASNemslice ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNemslice', 'nemslice'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Zoltan', 'nemslice'))

        ### Optional subpackage SEACASNemspread ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNemspread', 'nemspread'))

        ### Optional subpackage SEACASNumbers ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASNumbers', 'numbers'))

        ### Optional subpackage SEACASPLT ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASPLT', 'plt'))

        ### Optional subpackage SEACASSVDI ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSVDI', 'svdi'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_X11', 'svdi'))

        ### Optional subpackage SEACASSlice ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSlice', 'slice'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_METIS', 'slice'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Zoltan', 'slice'))

        ### Optional subpackage SEACASSupes ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSupes', 'supes'))

        ### Optional subpackage SEACASSuplib ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSuplib', 'suplib'))

        ### Optional subpackage SEACASSuplibC ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSuplibC', 'suplibc'))

        ### Optional subpackage SEACASSuplibCpp ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASSuplibCpp', 'suplibcpp'))

        ### Optional subpackage SEACASTxtexo ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASTxtexo', 'txtexo'))

        ### Optional subpackage SEACASZellij ###
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_SEACASZellij', 'zellij'))
        trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_Zoltan', 'zellij'))


        return trilinos_package_auto_cmake_args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        