#!/bin/bash
SPACK_SRC_DIR=$PWD/spack-src


# Check if the command 'spack' is available
if command -v spack &> /dev/null; then
    echo "Spack found already installed."
else
    echo "spack is not setup"
    if [ -d "$SPACK_SRC_DIR" ]; then
        echo "Using spack in '$SPACK_SRC_DIR'."
    else
        echo "cloning spack"
	git clone https://github.com/spack/spack.git $SPACK_SRC_DIR
    fi
    source $SPACK_SRC_DIR/share/spack/setup-env.sh

fi

echo "######################################"
spack --version
echo "######################################"
echo ""

spack repo add ${PWD}/spack_repo/trilinos
