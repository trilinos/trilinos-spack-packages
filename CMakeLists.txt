cmake_minimum_required(VERSION 3.10)
cmake_policy(SET CMP0110 NEW)

project(TrilinosSpackPackages)

# Find Python 3 executable, fail if we can't find it via REQUIRED
find_package (Python3 COMPONENTS Interpreter REQUIRED) 

INCLUDE(CTest)
ENABLE_TESTING()

# Set a variable so we can use it later
set(test_file "long-test.py")

find_program(PYTEST_EXEC pytest pytest.exe)

function(add_pytest_test testName)
  add_test(test_${testName} ${PYTEST_EXEC} ${CMAKE_SOURCE_DIR}/test/${test_file} -k ${testName})
  set_property(TEST test_${testName} PROPERTY FAIL_REGULAR_EXPRESSION "FAILED")
endfunction()

EXECUTE_PROCESS(
    COMMAND bash -c "spack list trilinos-"
    OUTPUT_VARIABLE spack_package_names_list
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
string(REPLACE "\n" ";" spack_package_names_list "${spack_package_names_list}")

add_pytest_test("spack_version")
add_pytest_test("spack_list")
add_pytest_test("spack_find")

foreach(package IN LISTS spack_package_names_list)
    add_pytest_test("spack_info[${package}]")
endforeach()

foreach(package IN LISTS spack_package_names_list)
    add_pytest_test("spack_spec[${package}]")
endforeach()
