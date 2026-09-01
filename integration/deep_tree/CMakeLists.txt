# integration/deep_tree/CMakeLists.txt
#
# The host half of this integration test. It builds one executable, `deep_tree`,
# which verify.py drives over stdin.
#
#   cmake -S . -B build
#   cmake --build build --target deep_tree-etask-generate   # after a schema edit
#   cmake --build build
#
# ## Why this does not FetchContent etask
#
# A scaffolded project fetches etask from its repository, because that is how a
# user consumes it. This one lives *inside* that repository, and the whole point
# of an integration test is to run the generator and the runtime as they stand in
# the working tree - not as they stand on a tag. So it adds the checkout above it
# directly. ETASK_ROOT exists to let a caller point that elsewhere; the default is
# the right answer for anyone running this from the repo.
cmake_minimum_required(VERSION 3.20)
project(deep_tree LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# This node's identity on the wire (1..254). Nothing here speaks over a link, but
# `internal_channel` uses it as the initiator id on every task it starts.
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ../.. from here is the etask checkout this test belongs to.
get_filename_component(_default_etask_root "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
set(ETASK_ROOT "${_default_etask_root}" CACHE PATH
    "The etask checkout to test against (defaults to the one containing this project)")

add_subdirectory("${ETASK_ROOT}" "${CMAKE_BINARY_DIR}/etask-build")

# main.cpp is the host entry point; app.cpp is the board's, and is deliberately
# absent here. Compiling both would give the link two lifecycles and no single
# answer about which one ran.
add_executable(deep_tree
  src/main.cpp
  src/support/exercise.cpp
  src/support/witness.cpp)

# `etask_add_schema` adds the freshness gate, the regeneration target, and every
# generated task body under SRC. Everything about this call is ordinary except
# the paths, which are under src/ so that the PlatformIO build beside this one
# compiles the identical tree - PlatformIO only looks in src/.
etask_add_schema(deep_tree
  SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
  SRC       ${CMAKE_CURRENT_SOURCE_DIR}/src/sys
  GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/src/generated
  PYTHON    ${CMAKE_CURRENT_SOURCE_DIR}/python/tasks.py
)

# src/ is the sole include root, matching what the PlatformIO script sets: every
# top-level directory under it is then reachable by its own path from any depth -
# `#include "support/witness.hpp"` from a task five scopes down, with no `../`.
target_include_directories(deep_tree PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(deep_tree PRIVATE etask)
target_compile_definitions(deep_tree PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})
