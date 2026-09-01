#
# The host half of the `all_tiers` integration project (see project/ci-plan.md).
#
# Builds the same sources PlatformIO builds for the ESP32, so that a lifecycle
# difference between the two targets shows up as a differing report rather than
# as a project that only exists on one of them. `verify.py` runs the binary this
# produces and asserts on what it prints.
cmake_minimum_required(VERSION 3.20)
project(etask_all_tiers LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------------------
# This node's identity on the wire (1..254), used when it initiates tasks itself.
# ---------------------------------------------------------------------------------------
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ---------------------------------------------------------------------------------------
# etask itself.
#
# Taken from the enclosing checkout rather than fetched, because this project
# exists to test *that* checkout: a FetchContent pointing at the published main
# would quietly verify a different library than the one being changed. The
# fallback keeps the project buildable when it is copied out on its own.
# ---------------------------------------------------------------------------------------
get_filename_component(_etask_root "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

if(EXISTS "${_etask_root}/etask/core/core.hpp")
  add_subdirectory("${_etask_root}" "${CMAKE_CURRENT_BINARY_DIR}/etask")
else()
  include(FetchContent)
  FetchContent_Declare(
    etask
    GIT_REPOSITORY https://github.com/MarikTik/etask.git
    GIT_TAG        main   # pin to a release tag for reproducible builds
  )
  FetchContent_MakeAvailable(etask)
endif()

# ---------------------------------------------------------------------------------------
# The application: entry point, lifecycle, the scenario driver under support/,
# and the generated task bodies (added by etask_add_schema below).
# ---------------------------------------------------------------------------------------
file(GLOB_RECURSE APP_LIB_SOURCES CONFIGURE_DEPENDS
     "${CMAKE_CURRENT_SOURCE_DIR}/hal/*.cpp"
     "${CMAKE_CURRENT_SOURCE_DIR}/support/*.cpp")

add_executable(all_tiers main.cpp app.cpp ${APP_LIB_SOURCES})

# ---------------------------------------------------------------------------------------
# Code generation. `cmake --build build --target all_tiers-etask-generate` rewrites
# the generated sections; a plain build only *checks* that they are current with
# the schema, and stops with that command if they are not.
#
# .schema.uids.json - the ledger keeping each task's wire uid stable - is
# maintained by the same run. Commit it: it is part of the wire contract.
# ---------------------------------------------------------------------------------------
etask_add_schema(all_tiers
  SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
  SRC       ${CMAKE_CURRENT_SOURCE_DIR}/sys
  GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/generated
  PYTHON    ${CMAKE_CURRENT_SOURCE_DIR}/python/tasks.py
)

# The project root is the sole include root: every top-level directory is then
# reachable by its own path from ANY file at ANY depth - `#include "config/wiring.hpp"`,
# `#include "support/lifecycle/report.hpp"` - with no `../` walks.
target_include_directories(all_tiers PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(all_tiers PRIVATE etask)
target_compile_definitions(all_tiers PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})

# A conformance project that compiled with warnings would be a poor place to
# find out the framework's headers had drifted, so they are errors here.
if(NOT MSVC)
  target_compile_options(all_tiers PRIVATE -Wall -Wextra)
endif()
