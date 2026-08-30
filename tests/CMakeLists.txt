# tests/CMakeLists.txt
#
# One executable per test file, mirroring etools' layout so that moving between
# the two repositories does not mean learning a second convention.
#
# The top-level CMakeLists.txt only adds this directory when etask is the project
# being built, so a consumer never pays for GoogleTest.

include(GoogleTest)

file(GLOB_RECURSE TEST_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

# etask leans on `constexpr` for the wire contract - a link's uid allowlist, the
# preamble layout, payload sizing - and asserting on those at compile time is the
# point. The default evaluation limits are reached by a schema of any real size.
set(GNU_OPTIONS
    -fconstexpr-ops-limit=2147483647
    -fconstexpr-loop-limit=2147483647
)
set(CLANG_OPTIONS
    -fconstexpr-steps=2147483647
)
set(MSVC_OPTIONS
    /constexpr:depth2147483647
)

# One name that builds every test. The directory is added EXCLUDE_FROM_ALL - a
# consumer must not pay for GoogleTest - so the default target skips these, and
# CI would otherwise have to name each executable and drift as they are added.
add_custom_target(all_tests)

foreach(test_src ${TEST_SOURCES})
    get_filename_component(test_name ${test_src} NAME_WE)

    add_executable(${test_name} ${test_src})
    add_dependencies(all_tests ${test_name})
    target_link_libraries(${test_name} PRIVATE etask GTest::gtest_main)

    if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        target_compile_options(${test_name} PRIVATE ${GNU_OPTIONS})
    elseif (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        target_compile_options(${test_name} PRIVATE ${CLANG_OPTIONS})
    elseif (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        target_compile_options(${test_name} PRIVATE ${MSVC_OPTIONS})
    endif()

    # The library is header-only and the tests are what a regression lands in
    # first, so they are built warning-clean and loudly.
    if (NOT MSVC)
        target_compile_options(${test_name} PRIVATE -Wall -Wextra -g -O0)
    endif()

    gtest_discover_tests(${test_name})
endforeach()
