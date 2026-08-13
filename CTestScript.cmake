# CTest script for CDash submission with SSL workarounds
# This script is used by docker-cdash.sh

# Set SSL verification to off for corporate environments
set(CTEST_CURL_OPTIONS "CURLOPT_SSL_VERIFYPEER;0;CURLOPT_SSL_VERIFYHOST;0")

# Get dashboard type from environment (default: Experimental)
set(DASHBOARD_TYPE "$ENV{DASHBOARD_TYPE}")
if(NOT DASHBOARD_TYPE)
    set(DASHBOARD_TYPE "Experimental")
endif()

# Set source and binary directories
set(CTEST_SOURCE_DIRECTORY "/opt/trilinos-spack-packages")
set(CTEST_BINARY_DIRECTORY "/opt/trilinos-spack-packages/build")

# Set CMake generator
set(CTEST_CMAKE_GENERATOR "Unix Makefiles")

# Read configuration from CTestConfig.cmake
ctest_read_custom_files(${CTEST_SOURCE_DIRECTORY})

# Configure
ctest_start(${DASHBOARD_TYPE})
ctest_configure(BUILD "${CTEST_BINARY_DIRECTORY}" SOURCE "${CTEST_SOURCE_DIRECTORY}")

# Build (not applicable for this project)
# ctest_build()

# Test
ctest_test()

# Coverage (optional)
# ctest_coverage()

# Submit to CDash
ctest_submit()
