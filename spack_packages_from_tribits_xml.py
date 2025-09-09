import sys
import xml.etree.ElementTree as ET
import argparse
import os
parser = argparse.ArgumentParser(description='Create Spack logic from Tribits logic')
parser.add_argument('-i', '--input', default='tribits.xml', help='Tribits XML file')
parser.add_argument('-d', '--output-dir', default='./generated-spack-packages', help='directory to write spack files')
args = parser.parse_args()

spack_var_str = str()
spack_disable_var_str = str()
spack_noncond_var_str = str()
spack_cond_var_str = str()
parent_package_variants = []
nonparent_package_variants = []
all_package_variants = []
exclude_name_list = ["ParentPackage", "TrilinosInstallTests", "TrilinosATDMConfigTests"]
exclude_dir_list = []#"commonTools",]
exclude_type = ["EX",]

hide='''
get_spack_names_from_trilinos_package_name={}
get_spack_names_from_trilinos_package_name['Adelus']={'spack_package_name':'trilinos-adelus', 'spack_package_header_name':'TrilinosAdelus'}
get_spack_names_from_trilinos_package_name['Amesos']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Amesos2']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Anasazi']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['AztecOO']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Belos']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Compadre']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Epetra']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['EpetraExt']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Galeri']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Gtest']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Ifpack']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Ifpack2']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Intrepid']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Intrepid2']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Isorropia']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Kokkos']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['KokkosKernels']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Krino']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['ML']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['MiniTensor']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['MueLu']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['NOX']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Pamgen']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Panzer']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Percept']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Phalanx']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Piro']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Pliris']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['PyTrilinos']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['ROL']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['RTOp']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['SEACAS']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['STK']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Sacado']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Shards']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['ShyLU']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['ShyLU_DD']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['ShyLU_Node']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Stokhos']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Stratimikos']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Teko']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Tempus']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Teuchos']={'spack_package_name':'trilinos-teuchos', 'spack_package_header_name':'TrilinosTeuchos'}
get_spack_names_from_trilinos_package_name['Thyra']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Tpetra']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['TrilinosBuildStats']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['TrilinosCouplings']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['TrilinosFrameworkTests']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['TrilinosSS']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Triutils']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Xpetra']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Zoltan']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Zoltan2']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Zoltan2Core']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
get_spack_names_from_trilinos_package_name['Zoltan2Sphynx']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
'''

class trilinos_package:
    def __init__(self, packageName, root):
        self.name=packageName
        self.spack_package_name=packageName
        self.spack_package_directory_name=packageName
        self.spack_package_header_name=packageName
        self.required_subpackages=[]
        self.required_trilinos_packages=[]
        self.optional_subpackages=[]
        self.optional_trilinos_packages=[]

        self.set_spack_package_names()
        self.set_dependency_lists()

    def set_dependency_lists(self):
        for package in root:
            if package.get("name") == self.name:
                packageProperties = {child.tag: child.attrib for child in package}
                print(packageProperties)
                for prop in packageProperties:
                    if 'value' in packageProperties[prop]:
                        dep_list=packageProperties[prop]['value'].split(",")
                    else:
                        dep_list=None

                    if prop == "LIB_REQUIRED_DEP_PACKAGES":
                        lib_req_dep_packages=dep_list
                    elif prop == "LIB_OPTIONAL_DEP_PACKAGES":
                        lib_opt_dep_packages=dep_list
                    elif prop == "TEST_REQUIRED_DEP_PACKAGES":
                        tst_req_dep_packages=dep_list
                    elif prop == "TEST_OPTIONAL_DEP_PACKAGES":
                        tst_opt_dep_packages=dep_list
                    elif prop == "LIB_REQUIRED_DEP_TPLS":
                        lib_req_dep_tpls=dep_list
                    elif prop == "LIB_OPTIONAL_DEP_TPLS":
                        lib_opt_dep_tpls=dep_list
                    elif prop == "TEST_REQUIRED_DEP_TPLS":
                        tst_req_dep_tpls=dep_list
                    elif prop == "TEST_OPTIONAL_DEP_TPLS":
                        tst_opt_dep_tpls=dep_list
                        
                #Required library trilinos package dependencies:
                if(lib_req_dep_packages):
                    for trilinos_dependency in lib_req_dep_packages:
                        if trilinos_dependency.startswith(self.name):
                            self.required_subpackages.append(trilinos_dependency)
                        else:
                            self.required_trilinos_packages.append(trilinos_dependency)

                #Optional library trilinos package dependencies
                if(lib_opt_dep_packages):
                    for trilinos_dependency in lib_opt_dep_packages:
                        if trilinos_dependency.startswith(self.name):
                            self.optional_subpackages.append(trilinos_dependency)
                        else:
                            self.optional_trilinos_packages.append(trilinos_dependency)

    def write_spack_package_header(self, file):
        print("writing header")
        file.write(f'''#
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

class {self.spack_package_header_name}(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    \n''')


    def write_spack_package_variants(self, file):
        print("writing variants")
        if self.optional_subpackages:
            file.write(f"    ### Variants automatically generated from optional subpackages ###\n")
            for subpackage in self.optional_subpackages:
                file.write(f"    variant({subpackage.replace(self.name,"").lower()}, default=True, description='Enable {subpackage}')\n")
            file.write("\n")

    def write_spack_package_conflicts(self, file):
        print("writing conflicts")

    def write_spack_package_tpls(self, file):
        print("writing tpls")

    def write_spack_package_generated_cmake_args(self, file):
        print("writing generated cmake args")
        file.write(f"    def generated_trilinos_package_cmake_args(self):\n")
        file.write(f"        # auto generated cmake arguments\n")
        file.write(f"        generated_cmake_options = []\n")
        if self.required_subpackages:
            for subpackage in self.required_subpackages:
                file.write(f"        generated_cmake_options.append(-DTrilinos_ENABLE_{subpackage}=ON)\n")
            file.write("\n")
        if self.optional_subpackages:
            for subpackage in self.optional_subpackages:
                file.write(f"        generated_cmake_options.append(self.define_from_variant('TRILINOS_ENABLE_{subpackage}', {subpackage.replace(self.name, "").lower()}))\n")
    
        file.write(f"\n")
        file.write(f"        return generated_cmake_options\n")


    def write_spack_package_footer(self, file):
        print("writing footer")
        file.write('''   
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        ''')

    def write_spack_package(self, install_root):
        output_file = f"{install_root}/{self.spack_package_directory_name}/package.py"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        print(f"Writing spack package for {self.name}: {output_file}")
        with open (f"{output_file}", 'w') as file:
            self.write_spack_package_header(file)
            self.write_spack_package_variants(file)
            self.write_spack_package_conflicts(file)
            self.write_spack_package_tpls(file)
            self.write_spack_package_generated_cmake_args(file)
            self.write_spack_package_footer(file)

    def set_spack_package_names(self):
       # Initialize tmp_string with a default value
        tmp_string = self.name
        print(tmp_string)

        # Check if the first character is uppercase and modify accordingly
        if tmp_string[0].isupper(): 
            tmp_string = tmp_string[0].lower() + tmp_string[1:]

        # Replace the first uppercase letter with a lowercase letter prefixed by a hyphen
        for index, char in enumerate(tmp_string):
            if char.isupper():  # Check if the character is uppercase
                tmp_string = tmp_string[:index] + "-" + char.lower() + tmp_string[index + 1:].lower()
                break  # Exit the loop after the first replacement

        # Assign the modified string to self.spack_package_name
        self.spack_package_name = "trilinos-" + tmp_string
        self.spack_package_directory_name = self.spack_package_name.replace("-","_")

        for index, char in enumerate(tmp_string):
            if char == "-":  # Check for hyphens
                tmp_string = tmp_string[:index] + tmp_string[index+1].upper() + tmp_string[index + 2:]

        self.spack_package_header_name="Trilinos" + tmp_string[0].upper() + tmp_string[1:]               

    def printout(self):
        print(f"Package Name: {self.name}")
        print(f"Spack Package Name: {self.spack_package_name}")
        print(f"Spack Package Directory Name: {self.spack_package_directory_name}")
        print(f"Spack Package Header Name: {self.spack_package_header_name}")
        print(f"Required subpackages: {self.required_subpackages}")
        print(f"Required Trilinos Packages: {self.required_trilinos_packages}")
        print(f"Optional Subpackages: {self.optional_subpackages}")
        print(f"Optional Trilinos Packages: {self.optional_trilinos_packages}")



def write_trilinos_spack_package(root, packageName):
    spack_package_name=get_spack_names_from_trilinos_package_name[packageName]['spack_package_name'].replace("-", "_")
    spack_package_header_name=get_spack_names_from_trilinos_package_name[packageName]['spack_package_header_name']
    output_file = f"{args.output_dir}/{spack_package_name}/package.py"
    print(f"Writing spack package for {packageName}: {output_file}")
    for package in root:
        if package.get("name") == packageName:

            packageProperties = {child.tag: child.attrib for child in package}
            package_info=[]
            package_info.append({
                'name': packageName,
                'dir': package.get("dir"),
                'type': package.get("type"),
                'properties': packageProperties
            })

            for info in package_info:
                
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open (f"{output_file}", 'w') as file:
                    file.write(f'''# Copyright Spack Project Developers. See COPYRIGHT file for details.
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

class {spack_package_header_name}(TrilinosBaseClass):
    """The Trilinos Project is an effort to develop algorithms and enabling
    technologies within an object-oriented software framework for the solution
    of large-scale, complex multi-physics engineering and scientific problems.
    A unique design feature of Trilinos is its focus on packages.
    """

    maintainers("jfrye")
    #Package Name: {info['name']}
    #Directory: {info['dir']}
    #Type: {info['type']}

    # ###################### Versions ##########################
    # Handled in TrilinosBaseClass
    \n''')
                    

                    for prop, attr in info['properties'].items():
                        if attr.get("value") is None:
                            dep_list=None
                        else:
                            dep_list=attr.get("value").split(',')
                        
                        if prop == "LIB_REQUIRED_DEP_PACKAGES":
                            lib_req_dep_packages=dep_list
                        elif prop == "LIB_OPTIONAL_DEP_PACKAGES":
                            lib_opt_dep_packages=dep_list
                        elif prop == "TEST_REQUIRED_DEP_PACKAGES":
                            tst_req_dep_packages=dep_list
                        elif prop == "TEST_OPTIONAL_DEP_PACKAGES":
                            tst_opt_dep_packages=dep_list
                        elif prop == "LIB_REQUIRED_DEP_TPLS":
                            lib_req_dep_tpls=dep_list
                        elif prop == "LIB_OPTIONAL_DEP_TPLS":
                            lib_opt_dep_tpls=dep_list
                        elif prop == "TEST_REQUIRED_DEP_TPLS":
                            tst_req_dep_tpls=dep_list
                        elif prop == "TEST_OPTIONAL_DEP_TPLS":
                            tst_opt_dep_tpls=dep_list
                        
                    #Required library trilinos package dependencies:
                    if(lib_req_dep_packages):
                        required_trilinos_packages=[]
                        required_subpackages=[]
                        for trilinos_dependency in lib_req_dep_packages:
                            if trilinos_dependency.startswith(packageName):
                                required_subpackages.append(trilinos_dependency)
                            else:
                                required_trilinos_packages.append(trilinos_dependency)

                        if required_trilinos_packages:
                            file.write("     #Required Trilinos package dependencies\n")
                        for subpackage in required_trilinos_packages:
                            file.write(f"    depends_on_trilinos_dependency(trilinos-{trilinos_dependency})\n")
                            file.write(f"    list_of_cmake_options.append(-DTPL_ENABLE_{trilinos_dependency})\n")
                            file.write("\n")
                                
                        if required_subpackages:
                            file.write(f"    #Required {packageName} subpackages\n")
                        for subpackage in required_subpackages:
                            file.write(f"    cmake_options.append(-D{packageName}_ENABLE_{subpackage}=ON)\n")
                            file.write(f"    cmake_options.append(-DTrilinos_ENABLE_{subpackage}=ON)\n")
                            file.write("\n")
                    else:
                        file.write("    #No required Trilinos dependencies\n")
                        
                    #Optional library trilinos package dependencies
                    if(lib_opt_dep_packages):

                        optional_trilinos_packages=[]
                        optional_subpackages=[]
                        for trilinos_dependency in lib_opt_dep_packages:
                            if trilinos_dependency.startswith(packageName):
                                optional_subpackages.append(trilinos_dependency)
                            else:
                                optional_trilinos_packages.append(trilinos_dependency)
                
                        if optional_trilinos_packages:
                            file.write(f"    ### Optional Trilinos packages ###\n")
                        for subpackage in optional_trilinos_packages:
                            file.write(f"        when +optional_packages:\n")
                            file.write(f"            depends_on_trilinos_dependency(trilinos-{trilinos_dependency})\n")      
                            file.write(f"            list_of_cmake_options.append(-DTPL_ENABLE_{trilinos_dependency})\n")
                            file.write("\n")
                            
                        if optional_subpackages:
                            file.write(f"    ### Optional {packageName} subpackages ###\n")
                            for subpackage in optional_subpackages:
                                file.write(f"    variant({subpackage.lower()}, default=ON)\n")
                                file.write(f"    when(+{subpackage.lower()}):\n")
                                file.write(f"        cmake_options.append(-D{packageName}_ENABLE_{subpackage}=ON)\n")
                                file.write(f"        cmake_options.append(-DTrilinos_ENABLE_{subpackage}=ON)\n")
                                file.write("\n")
                            file.write(f"    when +all_optional_dependencies:\n")
                            for subpackage in optional_subpackages:
                                file.write(f"    variant({subpackage.lower()}, default=ON)\n")
                    else:
                        file.write("    #No optional Trilinos dependencies\n")
                    file.write('''   
    def generated_trilinos_package_cmake_args(self):
        args = [
        "-DTrilinos_ENABLE_Tpetra=ON",
        "-DTPL_ENABLE_Teuchos=ON",
        ]
    
        return args

    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_cmake_args())
        return args
        ''')

print("Reading in Tribits logic from ".ljust(30), ":".center(4), args.input)
tree = ET.parse(args.input)
root = tree.getroot()

for package in root:
    if package.get("name") not in exclude_name_list \
            and not any ([ptype==package.get("type") for ptype in exclude_type]) \
            and not any([val in package.get("dir") for val in exclude_dir_list]) \
            and package.find("ParentPackage").get("value") == "":
        pkg=trilinos_package(package.get("name"), root)
        pkg.printout()
        pkg.write_spack_package(args.output_dir)

#teuchos_pkg=trilinos_package("Teuchos", root)
#teuchos_pkg.printout()
#teuchos_pkg.write_spack_package(args.output_dir)

#trilinos_ss_pkg=trilinos_package("TrilinosSS", root)
#trilinos_ss_pkg.printout()
#trilinos_ss_pkg.write_spack_package(args.output_dir)
#write_trilinos_spack_package(root, "Teuchos")
