cmake_minimum_required(VERSION 3.20)
# Version is the one in library.json: headers and generator are released as a
# single unit, so a project pinning one pins the other.
project(etask VERSION 0.1.0 LANGUAGES CXX)

# ---------------------------------------------------------------------------------------
# C++ standard and header-only interface library
# ---------------------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(etask INTERFACE)

# During build: include repo root so consumers write #include <etask/...>
# During install: place headers in include/etask
target_include_directories(etask
  INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include/etask>
)

# ---------------------------------------------------------------------------------------
# Dependencies via FetchContent
# ---------------------------------------------------------------------------------------
include(FetchContent)

# Ensure etools/ecomm don't build their own tests when vendored here
set(ETOOLS_BUILD_TESTS OFF CACHE BOOL "Disable etools unit tests" FORCE)
set(ECOMM_BUILD_TESTS OFF CACHE BOOL "Disable ecomm unit tests" FORCE)

FetchContent_Declare(
  etools
  GIT_REPOSITORY https://github.com/MarikTik/etools.git
  GIT_TAG v1.2.0
)
FetchContent_MakeAvailable(etools)

FetchContent_Declare(
  ecomm
  GIT_REPOSITORY https://github.com/MarikTik/ecomm.git
  GIT_TAG v3.1.0
)
FetchContent_MakeAvailable(ecomm)

# Link etask -> etools, ecomm (etools links eser internally; ecomm links etools internally)
target_link_libraries(etask INTERFACE etools ecomm)

# ---------------------------------------------------------------------------------------
# The code generator's CMake front door: etask_add_schema().
#
# Included here so a FetchContent consumer has it as soon as etask is available,
# and installed + included from the package config below so a find_package()
# consumer gets exactly the same function. One definition, both paths.
# ---------------------------------------------------------------------------------------
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/etask.cmake)

# ---------------------------------------------------------------------------------------
# Examples (optional)
# ---------------------------------------------------------------------------------------
# Off for a consumer, on when etask itself is the project being built.
option(ETASK_BUILD_EXAMPLES "Build example executables for etask" ${PROJECT_IS_TOP_LEVEL})
if(ETASK_BUILD_EXAMPLES)
  # One executable per example, not one glob over all of them: each example is a
  # complete standalone project with its own main(), so a single target would be
  # three main()s and a link error. Each is named `example_<dir>`.
  #
  # An example's own CMakeLists.txt is deliberately NOT used here - it fetches
  # etask from GitHub, which is right for someone copying it as a starting point
  # and wrong for building the working tree it lives in. The sources are picked
  # up directly and linked against the local target instead, which is what makes
  # this a regression test of the checkout rather than of the last release.
  file(GLOB ETASK_EXAMPLE_DIRS
       LIST_DIRECTORIES true
       "${CMAKE_CURRENT_SOURCE_DIR}/examples/*")

  foreach(example_dir IN LISTS ETASK_EXAMPLE_DIRS)
    if(NOT IS_DIRECTORY "${example_dir}")
      continue()
    endif()
    if(NOT EXISTS "${example_dir}/main.cpp")
      continue()   # not a host-buildable example (a PlatformIO-only sketch, say)
    endif()

    get_filename_component(example_name "${example_dir}" NAME)
    file(GLOB_RECURSE example_sources "${example_dir}/*.cpp")

    add_executable(example_${example_name} ${example_sources})
    target_include_directories(example_${example_name} PRIVATE "${example_dir}")
    target_link_libraries(example_${example_name} PRIVATE etask)
    target_compile_features(example_${example_name} PRIVATE cxx_std_17)
  endforeach()
endif()

# ---------------------------------------------------------------------------------------
# Testing: GoogleTest for etask's own tests
# ---------------------------------------------------------------------------------------
# Gated on being top-level as well as on BUILD_TESTING: the latter defaults ON
# even for a project that only vendors etask, and a consumer should not pay for
# etask's test suite (or googletest) to depend on it.
set(ETASK_BUILD_TESTS_DEFAULT ${PROJECT_IS_TOP_LEVEL})
option(ETASK_BUILD_TESTS "Build unit tests for etask" ${ETASK_BUILD_TESTS_DEFAULT})

include(CTest) # defines BUILD_TESTING
if(ETASK_BUILD_TESTS AND BUILD_TESTING AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/CMakeLists.txt")
  enable_testing()

  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG release-1.12.1
  )
  FetchContent_MakeAvailable(googletest)

  add_subdirectory(tests EXCLUDE_FROM_ALL)
endif()

# ---------------------------------------------------------------------------------------
# Installation
# We vendor the full dependency chain in the same export:
#   etask  -> ecomm -> etools -> eser
# This avoids "target not in any export set" errors on install(EXPORT ...).
# ---------------------------------------------------------------------------------------

# Install etask public headers. The .tpp/.inl files are part of them, not build
# leftovers: every .hpp ends by including its definitions (see reply.hpp,
# outcome.hpp, status_code.hpp), so installing only *.hpp ships headers that
# cannot compile.
install(
  DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/etask/
  DESTINATION include/etask
  FILES_MATCHING
    PATTERN "*.hpp"
    PATTERN "*.tpp"
    PATTERN "*.inl"
)

# Collect targets to export; require that ecomm/etools/eser exist (they should, via FetchContent)
set(ETASK_EXPORT_TARGETS etask)

if(NOT TARGET ecomm)
  message(FATAL_ERROR "Expected target 'ecomm' to exist (fetched via FetchContent).")
endif()
list(APPEND ETASK_EXPORT_TARGETS ecomm)

if(NOT TARGET etools)
  message(FATAL_ERROR "Expected target 'etools' to exist (fetched via FetchContent).")
endif()
list(APPEND ETASK_EXPORT_TARGETS etools)

if(NOT TARGET eser)
  message(FATAL_ERROR "Expected target 'eser' to exist (provided by etools).")
endif()
list(APPEND ETASK_EXPORT_TARGETS eser)

# Install targets (INTERFACE libs install as importable targets)
install(
  TARGETS ${ETASK_EXPORT_TARGETS}
  EXPORT etaskTargets
)

# Generate and install an export file containing all three targets.
# Consumers can then do: find_package(etask CONFIG) and link etask::etask
install(
  EXPORT etaskTargets
  NAMESPACE etask::
  DESTINATION lib/cmake/etask
)

# ---------------------------------------------------------------------------------------
# Package config, so find_package(etask) actually works.
#
# install(EXPORT) alone only ships the targets file; without a config file
# find_package has nothing to load. This also carries etask_add_schema() and the
# generator itself into the install tree, so an installed etask can generate code
# exactly as a fetched one does - which is the whole point of shipping the
# generator in the same repository as the headers.
# ---------------------------------------------------------------------------------------
include(CMakePackageConfigHelpers)

configure_package_config_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/cmake/etaskConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/etaskConfig.cmake
  INSTALL_DESTINATION lib/cmake/etask
)

write_basic_package_version_file(
  ${CMAKE_CURRENT_BINARY_DIR}/etaskConfigVersion.cmake
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMajorVersion
)

install(
  FILES
    ${CMAKE_CURRENT_BINARY_DIR}/etaskConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/etaskConfigVersion.cmake
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/etask.cmake
  DESTINATION lib/cmake/etask
)

# The generator, beside the headers it emits against. `_etask_find_generator()`
# looks here in an installed tree; the pycache is excluded because it is build
# leftovers, not source.
install(
  DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/etask-python/etask
  DESTINATION share/etask/python
  PATTERN "__pycache__" EXCLUDE
)
