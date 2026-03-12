# Setup Instructions
1. clone the repo
```
git clone git@github.com:trilinos/trilinos-spack-packages.git
```
Setup spack to use this repository as a spack repo
```
cd trilinos-spack-packages
source setup-spack.sh
spack list trilinos-
```
note that `setup-spack.sh` will install spack and activate it unless you have it already active in your environment
```
$ spack list trilinos-
trilinos-adelus                 trilinos-rtop
trilinos-amesos2                trilinos-sacado
trilinos-anasazi                trilinos-shards
trilinos-base-class             trilinos-shylu
trilinos-belos                  trilinos-shylu-dd
trilinos-catalyst-ioss-adapter  trilinos-shylu-node
trilinos-compadre               trilinos-stokhos
trilinos-galeri                 trilinos-stratimikos
trilinos-ifpack2                trilinos-teko
trilinos-intrepid2              trilinos-tempus
trilinos-krino                  trilinos-teuchos
trilinos-magistrate             trilinos-thyra
trilinos-minitensor             trilinos-tpetra
trilinos-muelu                  trilinos-trilinosatdmconfigtests
trilinos-nox                    trilinos-trilinosbuildstats
trilinos-pamgen                 trilinos-trilinoscouplings
trilinos-panzer                 trilinos-trilinosframeworktests
trilinos-percept                trilinos-trilinosinstalltests
trilinos-phalanx                trilinos-trilinosss
trilinos-piro                   trilinos-xpetra
trilinos-pytrilinos2            trilinos-zoltan
trilinos-rol                    trilinos-zoltan2
==> 44 packages

```

# Testing
## Submitting to cdash
```
mkdir build
cd build
cmake ../
ctest -D Experimental
```

## Local Testing
```
pip install -r requirements.txt
pytest test/short-test.py
```
or
```
pytest test/short-test.py
```
