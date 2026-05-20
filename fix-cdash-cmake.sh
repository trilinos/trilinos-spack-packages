#!/bin/bash
# Quick fix for cmake conflict in docker-cdash.sh

cd /projects/trilinos-spack-packages

echo "Fixing docker-cdash.sh cmake conflict..."

# Backup original
cp docker-cdash.sh docker-cdash.sh.backup

# Fix the spack load cmake line
sed -i 's/spack load python cmake &&/spack load python \&\& (spack load cmake 2>\/dev\/null || spack load $(spack find --format '\''\/{hash}'\'' cmake | head -1)) \&\&/' docker-cdash.sh

echo "Fixed! Backup saved to docker-cdash.sh.backup"

# Show the change
echo ""
echo "Changed from:"
grep "spack load python cmake" docker-cdash.sh.backup

echo ""
echo "Changed to:"
grep "spack load python" docker-cdash.sh | head -1

echo ""
echo "The nightly will now work on next run."
