#!/bin/bash

source setup-spack.sh

tmp_dir_name="tmp-generate-xml"-$(date +%F)
new_xml_file_name="TrilinosPackageDependencies"-$(date +%F)".xml"

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
echo "The script lives in: $SCRIPT_DIR"

echo $tmp_dir_name
echo $SCRIPT_DIR

cd $SCRIPT_DIR

mkdir -p $tmp_dir_name
cd $tmp_dir_name

rm -rf Trilinos
git clone https://github.com/trilinos/Trilinos.git

rm -rf build
mkdir -p build
cd build

cmake -D Trilinos_DEPS_XML_OUTPUT_FILE:FILEPATH=$PWD/$new_xml_file_name ../Trilinos/

cp $new_xml_file_name $SCRIPT_DIR/xml_files
