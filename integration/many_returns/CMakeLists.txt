#
# integration/many_returns - the reply direction, at its widest.
#
# This is the *scaffolded* (non-generated) half of the project; the generated
# half - the src/sys/ task tree and src/generated/ - comes from `etask generate`
# on schema.yaml, wired in by etask_add_schema() below.
cmake_minimum_required(VERSION 3.20)
project(etask_many_returns LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------------------
# This node's identity on the wire (1..254), used when it initiates tasks itself.
# ---------------------------------------------------------------------------------------
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ---------------------------------------------------------------------------------------
# The etask framework, and the code generator that ships inside it.
#
# Taken from this repository rather than fetched from a tag: an integration
# project's whole job is to test the etask sitting next to it, and a FetchContent
# pin would test a released one instead - passing on a branch that broke the
# thing under test. The path is relative to this file, so it survives being
# configured from anywhere.
# ---------------------------------------------------------------------------------------
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../.. etask-build)

# ---------------------------------------------------------------------------------------
# The application.
#
# main.cpp is the host entry point; arduino_main.cpp is the board's, and is
# deliberately NOT listed - the Arduino core supplies its own main(), so
# compiling both would define one twice. PlatformIO makes the opposite choice in
# platformio.ini, which is the only difference between the two builds.
# ---------------------------------------------------------------------------------------
file(GLOB_RECURSE APP_LIB_SOURCES CONFIGURE_DEPENDS
     "${CMAKE_CURRENT_SOURCE_DIR}/src/hal/*.cpp"
     "${CMAKE_CURRENT_SOURCE_DIR}/src/support/*.cpp")

add_executable(many_returns
  src/main.cpp
  src/app.cpp
  ${APP_LIB_SOURCES})

# ---------------------------------------------------------------------------------------
# Code generation. `cmake --build build --target many_returns-etask-generate`
# rewrites the generated sections; a plain build only *checks* that they are
# current with the schema, and stops with that command if they are not.
#
# .schema.uids.json - the ledger keeping each task's wire uid stable - is
# maintained by the same run. Commit it: it is part of the wire contract.
# ---------------------------------------------------------------------------------------
etask_add_schema(many_returns
  SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
  SRC       ${CMAKE_CURRENT_SOURCE_DIR}/src/sys
  GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/src/generated
  PYTHON    ${CMAKE_CURRENT_SOURCE_DIR}/python/tasks.py
)

# src/ is the sole include root: every directory under it is then reachable by
# its own path from ANY file at ANY depth - `#include "support/fixtures.hpp"`,
# `#include "generated/links.hpp"` - with no `../` walks. Add the root, not each
# subdir, so the top-level prefix is required (and never ambiguous). This is the
# same root PlatformIO puts on the include path, so the two builds resolve every
# include identically.
target_include_directories(many_returns PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(many_returns PRIVATE etask)
target_compile_definitions(many_returns PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})

# An integration project exists to catch what a warning would have caught, so
# warnings are errors here even when they are not for the library.
target_compile_options(many_returns PRIVATE -Wall -Wextra -Werror)
