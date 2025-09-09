import sys
import xml.etree.ElementTree as ET
import argparse
import os
import re

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
exclude_dir_list = []
exclude_type = ["EX",]

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
        self.required_tpls=[]
        self.optional_tpls=[]

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

                #required trilinos tpl dependencies
                self.required_tpls=lib_req_dep_tpls

                #optional trilinos tpl dependencies
                self.optional_tpls=lib_opt_dep_tpls

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
        if self.optional_subpackages:
            file.write(f"    ### Variants automatically generated from optional subpackages ###\n")
            for subpackage in self.optional_subpackages:
                file.write(f"    variant({subpackage.replace(self.name,"").lower()}, default=True, description='Enable {subpackage}')\n")
            file.write("\n")

        if self.optional_tpls:
            file.write(f"    ### Optional TPLs variants ###\n")
            for tpl in self.optional_tpls:
                file.write(f"    variant({tpl.lower()}, default=True, description='Enable tpl')\n")
            file.write("\n")

    def write_spack_package_conflicts(self, file):
        print("writing conflicts")

    def write_spack_package_tpls(self, file):
        print("writing tpls")
        if self.required_tpls:
            file.write(f"    ### Required TPLs automatically generated ###\n")
            for tpl in self.required_tpls:
                file.write(f"    depends_on({tpl.lower()})\n")
            file.write("\n")

        if self.optional_tpls:
            file.write(f"    ### Optional TPLs automatically generated ###\n")
            for tpl in self.optional_tpls:
                file.write(f"    depends_on({tpl.lower()}, when='+{tpl.lower()}')\n")
            file.write("\n")
    

    def write_spack_package_generated_cmake_args(self, file):
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
       
        self.spack_package_name = self.get_spack_package_name(self.name)
        self.spack_package_directory_name = self.get_spack_package_directory_name(self.name)
        self.spack_package_header_name=self.get_spack_package_header_name(self.name) 

    def get_spack_package_name(self, packageName):
        # Initialize tmp_string with a default value
        tmp_string = packageName.replace("_","")
        print(tmp_string)

        # Define a function to convert matched uppercase letters to lowercase
        def replace_match(match):
            return '-' + match.group(0).lower()

        # Use re.sub() to find sequences of uppercase letters and replace them
        tmp_string = "trilinos" + re.sub(r'[A-Z]+', replace_match, packageName)
        return tmp_string.replace("shy-lu","shylu")


    def get_spack_package_directory_name(self, packageName):
        # Initialize tmp_string with a default value
        tmp_string = self.get_spack_package_name(packageName)
        
        return "trilinos_" + tmp_string.replace("-", "_").replace("__","_")

    def get_spack_package_header_name(self, packageName):
        # Define a function to capitalize the first letter and lowercase the rest
        def replace_match(match):
            # Get the matched group
            group = match.group(0)
            # Capitalize the first letter and lowercase the rest
            return group[0].upper() + group[1:].lower()

        # Use re.sub() to find sequences of uppercase letters and replace them
        modified_string = re.sub(r'[A-Z]+', replace_match, packageName.replace("_",""))
        return "Trilinos" + modified_string


    def printout(self):
        print(f"Package Name: {self.name}")
        print(f"Spack Package Name: {self.spack_package_name}")
        print(f"Spack Package Directory Name: {self.spack_package_directory_name}")
        print(f"Spack Package Header Name: {self.spack_package_header_name}")
        print(f"Required subpackages: {self.required_subpackages}")
        print(f"Required Trilinos Packages: {self.required_trilinos_packages}")
        print(f"Optional Subpackages: {self.optional_subpackages}")
        print(f"Optional Trilinos Packages: {self.optional_trilinos_packages}")

tree = ET.parse(args.input)
root = tree.getroot()

for package in root:
    if package.get("name") not in exclude_name_list \
            and not any ([ptype==package.get("type") for ptype in exclude_type]) \
            and not any([val in package.get("dir") for val in exclude_dir_list]) \
            and package.find("ParentPackage").get("value") == "":
#        pass
        pkg=trilinos_package(package.get("name"), root)
        pkg.printout()
        pkg.write_spack_package(args.output_dir)

#pkg=trilinos_package("Teuchos", root)
#print(pkg.get_spack_package_name("TrilinosSS"))
#print(pkg.get_spack_package_directory_name("STK"))
#print(pkg.get_spack_package_name("STK"))