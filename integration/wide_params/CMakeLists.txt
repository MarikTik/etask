# integration/wide_params/CMakeLists.txt
#
# The host half of the type-system integration project. Builds the same sources
# PlatformIO builds for the ESP32 (see platformio.ini), against the same schema,
# which is the whole point: the two binaries have to agree on the wire, and the
# only way to find out that they do not is to build both from one schema.
#
#   cmake -S . -B build
#   cmake --build build
#
# A build only *checks* that the generated code is current with schema.yaml; it
# never regenerates. Run `cmake --build build --target app-etask-generate` after
# editing the schema, then re-configure so the glob picks up any new .cpp.
cmake_minimum_required(VERSION 3.20)
project(etask_wide_params LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------------------
# This node's identity on the wire (1..254), used when it initiates tasks itself.
# ---------------------------------------------------------------------------------------
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ---------------------------------------------------------------------------------------
# The etask framework.
#
# This project lives *inside* the etask repository, so it uses the checkout it is
# sitting in rather than fetching a tag. That is not a convenience: an integration
# project exists to catch a regression in the working tree, and one built against
# a published tag would pass while the tree next to it was broken.
#
# The FetchContent branch is the fallback for a copy of this directory lifted out
# of the repo, which is how a user would actually consume it.
# ---------------------------------------------------------------------------------------
get_filename_component(ETASK_REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
if(EXISTS "${ETASK_REPO_ROOT}/cmake/etask.cmake")
  # Examples and tests off: this project is the thing being built, and the
  # enclosing repo's own targets are not part of what it proves.
  set(ETASK_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
  set(ETASK_BUILD_TESTS    OFF CACHE BOOL "" FORCE)
  add_subdirectory("${ETASK_REPO_ROOT}" "${CMAKE_CURRENT_BINARY_DIR}/etask")
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
# The application.
#
# Everything lives under src/ rather than at the project root, because PlatformIO
# compiles src/ and nothing else - and this project has to build both ways from
# one tree. The cost is one extra path component; the alternative is two copies
# of every task body.
#
# The task bodies under src/sys are globbed rather than listed: the generator
# creates one .cpp per schema task, so a hand-maintained list would be a second
# place to forget a task.
# ---------------------------------------------------------------------------------------
file(GLOB_RECURSE APP_TASK_SOURCES CONFIGURE_DEPENDS
     "${CMAKE_CURRENT_SOURCE_DIR}/src/sys/*.cpp")

add_executable(app
  src/main.cpp
  src/app.cpp
  ${APP_TASK_SOURCES})

# ---------------------------------------------------------------------------------------
# Code generation. `cmake --build build --target app-etask-generate` rewrites the
# generated sections; a plain build only checks that they are current with the
# schema, and stops with that command if they are not.
#
# .schema.uids.json - the ledger keeping each task's wire uid stable - is
# maintained by the same run. Commit it: it is part of the wire contract, and
# this project's whole subject is a wire contract.
#
# PYTHON is named here because the host driver is the other half of the test:
# verify.py imports python/tasks.py, so the client bindings are as much an
# output of this schema as the firmware is.
# ---------------------------------------------------------------------------------------
etask_add_schema(app
  SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
  SRC       ${CMAKE_CURRENT_SOURCE_DIR}/src/sys
  GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/src/generated
  PYTHON    ${CMAKE_CURRENT_SOURCE_DIR}/python/tasks.py
)

# src/ is the include root, not the project root: it is what PlatformIO puts on
# the include path, so anchoring here is what keeps `#include "support/fold.hpp"`
# and `#include "config/wiring.hpp"` resolving identically under both builds.
target_include_directories(app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(app PRIVATE etask)
target_compile_definitions(app PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})

# This project is a CI subject, so it is built at the strictness CI will use.
# A padding or truncation warning here is the finding, not noise to be filtered:
# every conversion in this tree is deliberate, so any the compiler flags is one
# that was not.
target_compile_options(app PRIVATE
  $<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:-Wall;-Wextra;-Wconversion;-Werror>)
