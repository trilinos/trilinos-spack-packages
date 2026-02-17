import sys
import xml.etree.ElementTree as ET
import argparse
import os
import re

parser = argparse.ArgumentParser(description='Create Spack logic from Tribits logic')
parser.add_argument('-i', '--input', default='tribits.xml', help='Tribits XML file')
parser.add_argument('-d', '--output-dir', default='./spack_repo/trilinos/packages', help='directory to write spack files')
args = parser.parse_args()

# list of packages that have their own spack packages outside of trilinos
external_spack_packages=["Kokkos", "kokkos-kernals", "seacas", "KokkosKernels", "SEACAS"]

tree = ET.parse(args.input)
root = tree.getroot()

exclude_name_list = ["ParentPackage", "TrilinosInstallTests", "TrilinosATDMConfigTests"] + external_spack_packages


class trilinos_package:
    def __init__(self, packageName, root):
        self.name=packageName
        self.spack_package_name=packageName
        self.spack_package_directory_name=packageName
        self.spack_package_header_name=packageName
        self.root=root
        self.required_own_subpackages=[]
        self.required_trilinos_subpackages=[]
        self.required_trilinos_packages=[]
        self.optional_own_subpackages=[]
        self.optional_trilinos_subpackages=[]
        self.optional_trilinos_packages=[]
        self.required_tpls=[]
        self.optional_tpls=[]
        self.all_tpls=[]
        self.all_subpackages=[]
        self.all_trilinos_package_dependencies=[]
        self.parent_package=""

        self.set_spack_package_names()
        self.set_dependency_lists()
        self.cleanup_lists()

    def set_dependency_lists(self):
        for package in root:
            if package.get("name") == self.name:
                packageProperties = {child.tag: child.attrib for child in package}
                self.parent_package=packageProperties['ParentPackage']['value']
                for prop in packageProperties:
                    dep_list=[]
                    if 'value' in packageProperties[prop]:
                        package_list=packageProperties[prop].get('value').split(",")
                        for package in package_list:
                            dep_list.append(package)
                    #else:
                    #    dep_list=None

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

                #check to see if this package is a subpackage
                #self.parent_package=packageProperties['ParentPackage']['value']

                #Required library trilinos package dependencies:
                if(lib_req_dep_packages):
                    for dep in lib_req_dep_packages:
                        parent_pkg = self.get_parent_package_name(dep)
                        if parent_pkg == "":
                            #this is not a subpackage so it is added to the list of required trilinos packages and will be expressed as a spack dependency
                            self.required_trilinos_packages.append(dep)
                        elif parent_pkg == self.name:
                            #this is a required subpackage of the current package and will be explicitly turned on with no variant
                            self.required_own_subpackages.append(dep)
                        elif parent_pkg in external_spack_packages:
                            self.required_tpls.append(parent_pkg)
                        else:
                            #this is a subpackage from another trilinos package and needs to be expressed as a spack dependency + variant
                            self.required_trilinos_subpackages.append(dep)

                #roll up required dependencies from subpackages:
                if(self.required_own_subpackages):
                    for pkg in self.required_own_subpackages:
                        tmp_pkg=trilinos_package(pkg, root)
                        self.required_trilinos_packages.append(tmp_pkg.parent_package)
                        self.required_trilinos_subpackages + tmp_pkg.required_trilinos_subpackages

                if(self.required_trilinos_subpackages):
                    for pkg in self.required_trilinos_subpackages:
                        tmp_pkg=trilinos_package(pkg, root)
                        self.required_trilinos_packages + tmp_pkg.required_trilinos_packages
                        self.required_trilinos_subpackages + tmp_pkg.required_trilinos_subpackages

                #Optional library trilinos package dependencies:
                if(lib_opt_dep_packages):
                    for dep in lib_opt_dep_packages:
                        parent_pkg = self.get_parent_package_name(dep)
                        if parent_pkg == "":
                            #this is not a subpackage so it is added to the list of optional trilinos packages and will be expressed as a spack variant with dependency
                            self.optional_trilinos_packages.append(dep)
                            pass
                        elif parent_pkg == self.name:
                            #this is an optional subpackage of the current package and will be expressed as a variant
                            self.optional_own_subpackages.append(dep)
                        elif parent_pkg in external_spack_packages:
                            self.optional_tpls.append(parent_pkg)
                        else:
                            #this is a subpackage from another trilinos package and needs to be expressed as a spack variant that enables dependency + variant
                            self.optional_trilinos_subpackages.append(dep)


                
                #required trilinos tpl dependencies
                self.required_tpls=lib_req_dep_tpls

                #optional trilinos tpl dependencies
                self.optional_tpls=lib_opt_dep_tpls

                for external_spack_package in external_spack_packages:
                    if self.required_trilinos_packages:
                        if external_spack_package in self.required_trilinos_packages:
                            self.required_trilinos_packages=list(set(self.required_trilinos_packages)).remove(external_spack_package)
                            self.required_tpls.append(external_spack_package)
                            if self.required_trilinos_packages == None:
                                self.required_trilinos_packages=[]

                self.all_tpls=lib_opt_dep_tpls + lib_req_dep_tpls
                self.all_subpackages = self.required_own_subpackages + self.optional_own_subpackages + self.required_trilinos_subpackages + self.optional_trilinos_subpackages
                self.all_trilinos_package_dependencies = self.required_trilinos_packages + self.optional_trilinos_packages

    def cleanup_lists(self):
        #remove duplicates and own package name from lists
        def remove_duplicates_and_package_name_from(list_to_clean):
            tmp_set=set(list_to_clean)
            if self.name in tmp_set:
                tmp_set.remove(self.name)
            list_to_clean=list(tmp_set)
            list_to_clean.sort()
            return list_to_clean

        self.required_own_subpackages=remove_duplicates_and_package_name_from(self.required_own_subpackages)
        self.required_trilinos_packages=remove_duplicates_and_package_name_from(self.required_trilinos_packages)
        self.required_trilinos_subpackages=remove_duplicates_and_package_name_from(self.required_trilinos_subpackages)
        self.optional_own_subpackages=remove_duplicates_and_package_name_from(self.optional_own_subpackages)
        self.optional_trilinos_packages=remove_duplicates_and_package_name_from(self.optional_trilinos_packages)
        self.optional_trilinos_subpackages=remove_duplicates_and_package_name_from(self.optional_trilinos_subpackages)
        self.optional_tpls=remove_duplicates_and_package_name_from(self.optional_tpls)
        self.required_tpls=remove_duplicates_and_package_name_from(self.required_tpls)
        self.all_tpls=remove_duplicates_and_package_name_from(self.all_tpls)
        self.all_trilinos_package_dependencies=remove_duplicates_and_package_name_from(self.all_trilinos_package_dependencies)

        #remove trilinos packages that have an external spack package (kokkos, kokkos kernals, seacas ...) from the lists of 
        #trilinos dependencies and ass to the tpl lists
        for package in self.required_trilinos_packages:
            if package in external_spack_packages:
                self.required_own_subpackages.remove(package)
                self.required_tpls.append(package)
        for package in self.optional_trilinos_packages:
            if package in external_spack_packages:
                self.optional_trilinos_packages.remove(package)
                self.optional_tpls.append(package)
        
    def is_subpackage(self):
        if self.parent_package != "":
            return False
        else:
            return True
        
    def get_parent_package_name(self, packageName=""):
        if packageName == "":
            packageName=self.name

        for package in self.root:
            if package.get("name") == packageName:
                packageProperties = {child.tag: child.attrib for child in package}
                parent_package=packageProperties['ParentPackage']['value']
                return parent_package
        
        return ""
        
    def is_subpackage(self, packageName):
        parent_package=""
        for package in self.root:
            if package.get("name") == packageName:
               packageProperties = {child.tag: child.attrib for child in package}
               parent_package=packageProperties["ParentPackage"].get("value")
        
        if parent_package == "":
            return False
        else:
            return True        
            
    def write_spack_package_header(self, file):
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

    # List of automatically generated cmake arguments
    trilinos_package_auto_cmake_args=[]
    \n''')

    def write_spack_package_optional_own_subpackage(self, file, writing_cmake_section=False, white_space="    "):
        # These are optional subpackages of the current package.  There will be a spack variant and a cmake arg
        if self.optional_own_subpackages:
            for subpackage in self.optional_own_subpackages:
                file.write(f"{white_space}### Optional subpackage {subpackage} ###\n")
                if not writing_cmake_section:
                    file.write(f"{white_space}variant('{subpackage.replace(self.name,'').lower()}', default=True, description='Enable {subpackage}')\n")
                else:
                    file.write(f"{white_space}trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_ENABLE_{subpackage}', '{subpackage.replace(self.name, '').lower()}'))\n")
                tmp_pkg=trilinos_package(subpackage, self.root)
                subpackage_tpls = tmp_pkg.all_tpls
                trilinos_package_dependencies = tmp_pkg.all_trilinos_package_dependencies
                #if subpackage_tpls or trilinos_package_dependencies:
                #    if not writing_cmake_section:
                #       file.write(f"{white_space}with when('+{subpackage.replace(self.name,'').lower()}'):\n")
                for tpl in subpackage_tpls:
                    if not writing_cmake_section:
                        file.write(f"{white_space}variant('{tpl.lower()}', default=True, description='Enable TPL {tpl}')\n")
                        file.write(f"{white_space}depends_on('{tpl.lower()}', when='+{tpl.lower()}')\n")
                        file.write(f"{white_space}#conflicts('+{subpackage.replace(self.name,'').lower()}~{tpl.lower()}')\n")
                    else:
                        file.write(f"{white_space}trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_{tpl}', '{subpackage.replace(self.name, '').lower()}'))\n")

                for trilinos_dep in trilinos_package_dependencies:
                    if not writing_cmake_section:
                        file.write(f"{white_space}variant('{trilinos_dep.lower()}', default=True, description='Enable {trilinos_dep}')\n")
                        file.write(f"{white_space}depends_on_trilinos_package('{self.get_trilinos_spack_package_name(trilinos_dep)}')\n")
                        file.write(f"{white_space}#conflicts('+{subpackage.replace(self.name,'').lower()}~{trilinos_dep.lower()}')\n")
                    else:
                        file.write(f"{white_space}trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_{trilinos_dep}', '{subpackage.replace(self.name, '').lower()}'))\n")
                file.write("\n")
            file.write("\n")

    def write_spack_package_required_own_subpackage(self, file, writing_cmake_section=False, white_space="    "):
        # These are required subpackages of the current package.  Just add the cmake args
        if self.required_own_subpackages:
            for subpackage in self.required_own_subpackages:
                file.write(f"{white_space}### Required subpackage {subpackage} ###\n")
                if writing_cmake_section:
                    file.write(f"{white_space}trilinos_package_auto_cmake_args.append('TRILINOS_ENABLE_{subpackage}=ON')\n")
            file.write("\n")

            file.write(f"{white_space}### Required tpls of {self.name} from subpackage requirements###\n")
            for subpackage in self.required_own_subpackages:
                tmp_pkg=trilinos_package(subpackage, self.root)
                subpackage_tpls = tmp_pkg.all_tpls
                trilinos_package_dependencies = tmp_pkg.all_trilinos_package_dependencies
                for trilinos_dep in trilinos_package_dependencies:
                    if trilinos_dep in external_spack_packages:
                        trilinos_package_dependencies.remove(trilinos_dep)
                        subpackage_tpls.append(trilinos_dep)
                for tpl in subpackage_tpls:
                    if not writing_cmake_section:
                        file.write(f"{white_space}#depends_on('{self.get_spack_package_name(tpl)}')\n")
                    else:
                        file.write(f"{white_space}trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_{tpl}=ON')\n")
                for trilinos_dep in trilinos_package_dependencies:
                    if not writing_cmake_section:
                        file.write(f"{white_space}#depends_on_trilinos_package('{self.get_trilinos_spack_package_name(trilinos_dep)}')\n")
                    else:
                        file.write(f"{white_space}trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_{trilinos_dep}=ON')\n")
            file.write("\n")

    def write_spack_package_required_tpls(self, file, writing_cmake_section=False, white_space="    "):
        # These are required tpls of the current package
        if self.required_tpls:
            file.write(f"{white_space}### Required tpl dependencies of {self.name} ###\n")
            for tpl in self.required_tpls:
                if not writing_cmake_section:
                    file.write(f"{white_space}#depends_on('{self.get_spack_package_name(tpl)}')\n")
                else:
                    file.write(f"{white_space}trilinos_package_auto_cmake_args.append('TRILINOS_TPL_ENABLE_{tpl}=ON')\n")
                file.write("\n")

    def write_spack_package_optional_tpls(self, file, writing_cmake_section=False, white_space="    "):
        # These are optional tpls of the current package
        if self.optional_tpls:
            file.write(f"{white_space}###Optional tpl dependencies of {self.name} ###\n")
            for tpl in self.optional_tpls:
                if not writing_cmake_section:
                    file.write(f"{white_space}variant('{tpl.lower()}', default=True, description='Enable {tpl}')\n")
                    file.write(f"{white_space}##depends_on('{tpl.lower()}', when='+{tpl.lower()}')\n")
                else:
                    file.write(f"{white_space}trilinos_package_auto_cmake_args.append(self.define_from_variant('TRILINOS_TPL_ENABLE_{tpl}', '{tpl.lower()}'))\n")
                file.write("\n")

    def write_spack_package_variants(self, file):
        # These are optional subpackages of the current package.  There will be a spack variant added here and a cmake arg added later
        #if self.optional_own_subpackages:
        #    file.write(f"    ### Variants automatically generated from optional subpackages of {self.name} ###\n")
        #    for subpackage in self.optional_own_subpackages:
        #        file.write(f"    variant('{subpackage.replace(self.name,'').lower()}', default=True, description='Enable {subpackage}')\n")
         #   file.write("\n")

        # These are optional subpackages of another package.  There will be a spack variant added here and a depends_on(...) added later
        if self.optional_trilinos_subpackages:
            file.write(f"    ### Variants automatically generated from optional trilinos subpackages ###\n")
            for subpackage in self.optional_trilinos_subpackages:
                file.write(f"    variant('{subpackage.replace(self.name,'').lower()}', default=True, description='Enable {subpackage}')\n")
            file.write("\n")

        # optional trilinos packages.  Add a spack variant here and a depends_on(...) later
        if self.optional_trilinos_packages:
            file.write(f"    ### Optional Trilinos dependencies variants ###\n")
            for trilinos_package in self.optional_trilinos_packages:
                file.write(f"    variant('{self.get_trilinos_spack_package_name(trilinos_package)}', default=True, description='Enable {trilinos_package} support')\n")
            file.write("\n")

        # These are optional sTPLs.  There will be a spack variant added here and a depends_on(...) added later
        if self.optional_tpls:
            file.write(f"    ### Optional TPLs variants ###\n")
            for tpl in self.optional_tpls:
                file.write(f"    variant('{tpl.lower()}', default=True, description='Enable {tpl}')\n")
            file.write("\n")

    def write_spack_package_conflicts(self, file):
        print("writing conflicts")

    def write_spack_package_tpls(self, file):
        if self.required_trilinos_packages:
            file.write(f"    ### Required Trilinos packages ###\n")
            for trilinos_package in self.required_trilinos_packages:
                file.write(f"    #depends_on_trilinos_package('{self.get_trilinos_spack_package_name(trilinos_package)}')\n")
            file.write("\n")

        if self.optional_trilinos_packages:
            file.write(f"    ### Optional Trilinos packages ###\n")
            for trilinos_package in self.optional_trilinos_packages:
                file.write(f"    #depends_on_trilinos_package('{self.get_trilinos_spack_package_name(trilinos_package)}', when='+{self.get_trilinos_spack_package_name(trilinos_package)}')\n")
            file.write("\n")

        if self.required_tpls:
            file.write(f"    ### Required TPLs automatically generated ###\n")
            for tpl in self.required_tpls:
                file.write(f"    #depends_on({tpl.lower()})\n")
            file.write("\n")

        if self.optional_tpls:
            file.write(f"    ### Optional TPLs automatically generated ###\n")
            for tpl in self.optional_tpls:
                file.write(f"    #depends_on({tpl.lower()}, when='+{tpl.lower()}')\n")
            file.write("\n")

    def write_spack_package_generated_cmake_args(self, file):
        ws="        "
        file.write(f"    def generated_trilinos_package_cmake_args(self):\n")
        file.write(f"{ws}### auto generated cmake arguments\n")
        file.write(f"{ws}trilinos_package_auto_cmake_args = []\n")
        self.write_spack_package_required_tpls(file, writing_cmake_section=True, white_space=ws)
        self.write_spack_package_optional_tpls(file, writing_cmake_section=True, white_space=ws)
        self.write_spack_package_required_own_subpackage(file, writing_cmake_section=True, white_space=ws)
        self.write_spack_package_optional_own_subpackage(file, writing_cmake_section=True, white_space=ws)
        file.write(f"{ws}return trilinos_package_auto_cmake_args\n")

    def write_spack_package_footer(self, file):
        file.write('''
    def cmake_args(self):
        args = []
        args.extend(self.generated_trilinos_base_cmake_args())
        args.extend(self.trilinos_package_auto_cmake_args)
        return args
        ''')

    def write_spack_package(self, install_root):
        if self.is_subpackage(self):
            print(f"{self.name} is a subpackage")
            return
        
        output_file = f"{install_root}/{self.spack_package_directory_name}/package.py"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        print(f"Writing spack package for {self.name}: {output_file}")
        with open (f"{output_file}", 'w') as file:
            self.write_spack_package_header(file)
            self.write_spack_package_required_tpls(file)
            self.write_spack_package_optional_tpls(file)
            self.write_spack_package_required_own_subpackage(file)
            self.write_spack_package_optional_own_subpackage(file)
            #self.write_spack_package_variants(file)
            #self.write_spack_package_conflicts(file)
            #self.write_spack_package_tpls(file)
            self.write_spack_package_generated_cmake_args(file)
            self.write_spack_package_footer(file)

    def set_spack_package_names(self):

        self.spack_package_name = self.get_trilinos_spack_package_name(self.name)
        self.spack_package_directory_name = self.get_spack_package_directory_name(self.name)
        self.spack_package_header_name=self.get_spack_package_header_name(self.name)

    def get_spack_package_name(self, packageName=""):
        if packageName == "":
            packageName=self.name

        # Initialize tmp_string with a default value
        tmp_string = packageName.replace("_","")

        # Define a function to convert matched uppercase letters to lowercase
        def replace_match(match):
            return match.group(0).lower()

        # Use re.sub() to find sequences of uppercase letters and replace them
        tmp_string = re.sub(r'[A-Z]+', replace_match, packageName)
        #return tmp_string.replace("shy-lu","shylu")
        return tmp_string
    
    def get_trilinos_spack_package_name(self, packageName=""):
        if packageName == "":
            packageName=self.name

        # Initialize tmp_string with a default value
        tmp_string = packageName.replace("_","")

        # Define a function to convert matched uppercase letters to lowercase
        def replace_match(match):
            return '-' + match.group(0).lower()

        # Use re.sub() to find sequences of uppercase letters and replace them
        tmp_string = "trilinos" + re.sub(r'[A-Z]+', replace_match, packageName)
        #return tmp_string.replace("shy-lu","shylu")
        return tmp_string

    def get_spack_package_directory_name(self, packageName=""):
        if packageName == "":
            packageName=self.name
        # Initialize tmp_string with a default value
        tmp_string = self.get_trilinos_spack_package_name(packageName)

        return tmp_string.replace("-", "_").replace("__","_")

    def get_spack_package_header_name(self, packageName=""):
        if packageName == "":
            packageName=self.name
        if packageName == "ShyLU_Node":
            return "TrilinosShyLuNode"
        elif packageName == "ShyLU_DD":
            return "TrilinosShyLuDd"

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
        print("")
        print("*************")
        print(f"Package Name: {self.name}")
        print(f"Spack Package Name: {self.spack_package_name}")
        print(f"Parent Package: {self.parent_package}")
        print(f"{self.name} is a subpackage: {self.is_subpackage(self)}")
        print(f"Spack Package Directory Name: {self.spack_package_directory_name}")
        print(f"Spack Package Header Name: {self.spack_package_header_name}")
        print(f"Required {self.name} subpackages:")
        for req_sub_pkg in self.required_own_subpackages:
            print(f"  - {req_sub_pkg}")
        print(f"Required Trilinos subpackages:")
        for req_sub_pkg in self.required_trilinos_subpackages:
            print(f"  - {req_sub_pkg}")
        print(f"Required Trilinos Packages:")
        for req_tril_pkg in self.required_trilinos_packages:
            print(f"  - {req_tril_pkg}")
        print(f"Required TPLs:")
        for req_tpl in self.required_tpls:
            print(f"  - {req_tpl}")
        print(f"Optional {self.name} Subpackages:")
        for opt_sub_pkg in self.optional_own_subpackages:
            print(f"  - {opt_sub_pkg}")
        print(f"Optional Trilinos Subpackages:")
        for opt_sub_pkg in self.optional_trilinos_subpackages:
            print(f"  - {opt_sub_pkg}")
        print(f"Optional Trilinos Packages:")
        for opt_tril_pkg in self.optional_trilinos_packages:
            print(f"  - {opt_tril_pkg}")
        print(f"Optional TPLs:")
        for opt_tpl in self.optional_tpls:
            print(f"  - {opt_tpl}")
     

skip_loop=True

#pkg_list=["Panzer", "Panzer", "Teuchos", "MueLu"]
pkg_list=["Teuchos", "Panzer"]

if skip_loop:
    for pkg in pkg_list:
        tmp_pkg=trilinos_package(pkg, root)
        tmp_pkg.printout()
        tmp_pkg.write_spack_package(args.output_dir)

else:
    for package in root:
        if package.get("name") not in exclude_name_list and package.find("ParentPackage").get("value") == "":
            pkg=trilinos_package(package.get("name"), root)
            pkg.write_spack_package(args.output_dir)


