#!/bin/bash
tmp_dir_name="tmp-generate-xml"-$(date +%F)
new_xml_file_name="TrilinosPackageDependencies"-$(date +%F)".xml"

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
echo "The script lives in: $SCRIPT_DIR"

echo $tmp_dir_name
echo $SCRIPT_DIR

cd $SCRIPT_DIR
source setup-spack.sh

mkdir -p $tmp_dir_name
cd $tmp_dir_name

rm -rf Trilinos
git clone https://github.com/trilinos/Trilinos.git
cd Trilinos
git checkout develop
cd ../

rm -rf trilinos-configure
mkdir -p trilinos-configure
cd trilinos-configure

cmake -D Trilinos_DEPS_XML_OUTPUT_FILE:FILEPATH=$PWD/$new_xml_file_name ../Trilinos/

cp $new_xml_file_name $SCRIPT_DIR/xml_files

cd $SCRIPT_DIR

python3 generate_spack_packages.py --xml xml_files/$new_xml_file_name

cd $tmp_dir_name
rm -rf test-spack-packages
mkdir -p test-spack-packages
cd test-spack-packages

cmake $SCRIPT_DIR
nohup ctest -D Experimental &

cd $SCRIPT_DIR
