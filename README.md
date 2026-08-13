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

## Docker-based Testing (Recommended)

### Quick smoke tests
```bash
./docker-run.sh quick
```

### Submit results to CDash
```bash
./docker-cdash.sh Experimental
```
Results will be submitted to: https://my.cdash.org/index.php?project=Trilinos

Dashboard types:
- `Experimental` - One-time test submissions (default)
- `Nightly` - Scheduled nightly builds
- `Continuous` - Continuous integration builds

## Local Testing (without Docker)

### Direct pytest
```bash
pip install -r requirements.txt
pytest test/quick_test.py -m quick
```

### Via CMake/CTest
```bash
mkdir build
cd build
cmake ..
ctest -D Experimental
```
