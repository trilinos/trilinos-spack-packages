import sys
import xml.etree.ElementTree as ET
import argparse
parser = argparse.ArgumentParser(description='Create Spack logic from Tribits logic')
parser.add_argument('-i', '--input', default='tribits.xml', help='Tribits XML file')
parser.add_argument('-o', '--output', default='spack.txt', help='Spack file')
args = parser.parse_args()
"""

First, run:
>> cmake -DTrilinos_DEPS_XML_OUTPUT_FILE=tribits.xml -P ../cmake/tribits/ci_support/TribitsDumpDepsXmlScript.cmake`

Next, run:
>> python spack_variants_from_tribits_projects.py -i /path/to/tribits.xml -o spack.txt

"""
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
get_spack_names_from_trilinos_package_name['Teuchos']={'spack_package_name':'kokkos', 'spack_package_header_name':'Kokkos'}
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

def write_trilinos_spack_package(root, packageName):
    print("\n")
    print("Writing spack package for " + packageName +":")
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
                print(f"Package Name: {info['name']}")
                print(f"Directory: {info['dir']}")
                print(f"Type: {info['type']}")

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
                        print("     #Required Trilinos package dependencies")
                    for subpackage in required_trilinos_packages:
                        print(f"    depends_on_trilinos_dependency(trilinos-{trilinos_dependency})")
                        print(f"    list_of_cmake_options.append(-DTPL_ENABLE_{trilinos_dependency})")
                        print("")
                            
                    if required_subpackages:
                        print(f"    #Required {packageName} subpackages")
                    for subpackage in required_subpackages:
                        print(f"    cmake_options.append(-D{packageName}_ENABLE_{subpackage}=ON)")
                        print(f"    cmake_options.append(-DTrilinos_ENABLE_{subpackage}=ON)")
                        print("")
                else:
                    print("    #No required Trilinos dependencies")
                    
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
                        print(f"    ### Optional Trilinos packages ###")
                    for subpackage in optional_trilinos_packages:
                        print(f"        when +optional_packages:")
                        print(f"            depends_on_trilinos_dependency(trilinos-{trilinos_dependency})")      
                        print(f"            list_of_cmake_options.append(-DTPL_ENABLE_{trilinos_dependency})")
                        print("")
                        
                    if optional_subpackages:
                        print(f"    ### Optional {packageName} subpackages ###")
                        for subpackage in optional_subpackages:
                            print(f"    variant({subpackage.lower()}, default=ON)")
                            print(f"    when(+{subpackage.lower()}):")
                            print(f"        cmake_options.append(-D{packageName}_ENABLE_{subpackage}=ON)")
                            print(f"        cmake_options.append(-DTrilinos_ENABLE_{subpackage}=ON)")
                            print("")
                        print(f   "when +all_optional_dependencies:")
                        for subpackage in optional_subpackages:
                            print(f"    variant({subpackage.lower()}, default=ON)")
                else:
                    print("    #No optional Trilinos dependencies")

print("Reading in Tribits logic from ".ljust(30), ":".center(4), args.input)
tree = ET.parse(args.input)
root = tree.getroot()

for package in root:
    if package.get("name") not in exclude_name_list \
            and not any ([ptype==package.get("type") for ptype in exclude_type]) \
            and not any([val in package.get("dir") for val in exclude_dir_list]) \
            and package.find("ParentPackage").get("value") == "":
        pass
#        write_trilinos_spack_package(root, package.get("name"))

write_trilinos_spack_package(root, "Teuchos")
