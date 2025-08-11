cmake_minimum_required(VERSION 3.20)
project(etask LANGUAGES CXX)

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

# Ensure etools doesn't build its own tests when vendored here
set(ETOOLS_BUILD_TESTS OFF CACHE BOOL "Disable etools unit tests" FORCE)

FetchContent_Declare(
  etools
  GIT_REPOSITORY https://github.com/MarikTik/etools.git
  GIT_TAG main
)
FetchContent_MakeAvailable(etools)

# Link etask -> etools (etools links eser internally)
target_link_libraries(etask INTERFACE etools)

# ---------------------------------------------------------------------------------------
# Examples (optional)
# ---------------------------------------------------------------------------------------
option(ETASK_BUILD_EXAMPLES "Build example executables for etask" ON)
if(ETASK_BUILD_EXAMPLES)
  file(GLOB_RECURSE ETASK_EXAMPLE_SOURCES
      "${CMAKE_CURRENT_SOURCE_DIR}/example/*.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/example/**/*.cpp"
  )
  if(ETASK_EXAMPLE_SOURCES)
    add_executable(etask_examples ${ETASK_EXAMPLE_SOURCES})
    target_link_libraries(etask_examples PRIVATE etask)
  endif()
endif()

# ---------------------------------------------------------------------------------------
# Testing: GoogleTest for etask's own tests
# ---------------------------------------------------------------------------------------
include(CTest) # defines BUILD_TESTING
if(BUILD_TESTING)
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
#   etask  -> etools -> eser
# This avoids "target not in any export set" errors on install(EXPORT ...).
# ---------------------------------------------------------------------------------------

# Install etask public headers
install(
  DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/etask/
  DESTINATION include/etask
  FILES_MATCHING PATTERN "*.hpp"
)

# Collect targets to export; require that etools/eser exist (they should, via FetchContent)
set(ETASK_EXPORT_TARGETS etask)

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
