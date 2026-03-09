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

repo_ls_out=$(spack repo ls)

#$(spack repo ls)|grep "trilinos"

#echo $repo_ls_out
#echo $?

if echo "$repo_ls_out" | grep -q trilinos; then
    echo "Trilinos repo is already setup in spack"
else
    echo "Adding the trilinos repo to spack."
    spack repo add ${PWD}/spack_repo/trilinos
fi

unset repo_ls_out

