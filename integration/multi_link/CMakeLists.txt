#
# integration/multi_link - one board, two links, different policies.
#
# Buildable two ways, on purpose:
#
#   standalone   cmake -S integration/multi_link -B build
#                brings etask in itself, the way a real consumer project would
#   in-tree      added by the repository's own CMakeLists as part of CI
#                reuses the `etask` target that already exists
#
# The difference is the `if(TARGET etask)` below and nothing else, so the thing
# CI compiles is the same thing a user would.
cmake_minimum_required(VERSION 3.20)
project(etask_multi_link LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------------------
# This node's identity on the wire (1..254). `net` is a `network` link, so its
# frames carry addresses and this value actually appears on the wire; `bench` is
# point_to_point and ignores it. verify.py has to agree with this number.
# ---------------------------------------------------------------------------------------
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ---------------------------------------------------------------------------------------
# The etask framework, and with it the schema code generator and etask_add_schema().
# ---------------------------------------------------------------------------------------
if(NOT TARGET etask)
  # Standalone: the checkout three levels up is this project's own copy of etask,
  # used in preference to a fetched one so the integration project always tests
  # the working tree it lives in rather than whatever `main` happens to be.
  get_filename_component(_etask_root "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
  if(EXISTS "${_etask_root}/cmake/etask.cmake")
    add_subdirectory("${_etask_root}" "${CMAKE_BINARY_DIR}/etask" EXCLUDE_FROM_ALL)
  else()
    include(FetchContent)
    FetchContent_Declare(
      etask
      GIT_REPOSITORY https://github.com/MarikTik/etask.git
      GIT_TAG        main)
    FetchContent_MakeAvailable(etask)
  endif()
endif()

# ---------------------------------------------------------------------------------------
# The application.
# ---------------------------------------------------------------------------------------
add_executable(multi_link
  main.cpp
  app.cpp
  support/channels/stream_channel.cpp)

# The project root is the sole include root, so every top-level directory is
# reachable by its own path from any depth - `#include "support/channels/..."`,
# `#include "generated/links.hpp"` - with no `../` walks.
target_include_directories(multi_link PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(multi_link PRIVATE etask)
target_compile_definitions(multi_link PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})

# ---------------------------------------------------------------------------------------
# Code generation: schema.yaml -> sys/ scaffolds (once) + generated/ (always).
#
#   cmake --build build --target multi_link-etask-generate
#
# Adds a pre-build freshness check too, so a build whose generated code has
# fallen behind schema.yaml fails naming the command that fixes it, rather than
# silently regenerating a source tree mid-build.
#
# Also adds every sys/**/*.cpp to the target, which is why the task bodies are
# not listed in add_executable above.
# ---------------------------------------------------------------------------------------
etask_add_schema(multi_link
  SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
  SRC       ${CMAKE_CURRENT_SOURCE_DIR}/sys
  GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/generated
  PYTHON    ${CMAKE_CURRENT_SOURCE_DIR}/python/tasks.py)

# The per-link machinery is largely compile-time - `carries()` folds to a
# constant, the frame sizes are static_asserted - so warnings here are load
# bearing rather than hygiene, and an unused-parameter in a task body usually
# means a scaffold was left unfilled.
target_compile_options(multi_link PRIVATE -Wall -Wextra)
