**Setup Instructions**
'''
git clone git@github.com:trilinos/trilinos-spack-packages.git
cd trilinos-spack-packages
source setup-spack.sh
spack list trilinos-
'''

**Testing**
*Submitting to cdash*
'''
mkdir build
cd build
cmake ../
ctest -D Experimental
'''

*Local Testing*
'''
pip install -r requirements.txt
pytest test/short-test.py
'''
or
'''
pytest test/short-test.py
'''