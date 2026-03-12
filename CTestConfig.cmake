# This file should be placed in the root directory of your project.
## Then modify the CMakeLists.txt file in the root directory of your
## project to incorporate the testing dashboard.
##
## # The following are required to submit to the CDash dashboard:
##   ENABLE_TESTING()
##   INCLUDE(CTest)

SET(CTEST_BUILD_NAME "Trilinos_Spack_Packages")
SET(CTEST_NIGHTLY_START_TIME 04:00:00 UTC)
SET(CTEST_DROP_METHOD "https")
SET(CTEST_DROP_SITE "sems-cdash-son.sandia.gov/cdash")
SET(CTEST_PROJECT_NAME "Trilinos")
SET(CTEST_DROP_LOCATION "/submit.php?project=Trilinos")
SET(CTEST_TRIGGER_SITE "")
SET(CTEST_DROP_SITE_CDASH TRUE)
