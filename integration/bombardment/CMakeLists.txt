#
# The host half of the bombardment integration test.
#
# Builds src/ into one executable that hammers the task managers and prints a
# transcript of what each registration returned. verify.py runs this and checks
# the transcript; see that file for what is being proved and why.
#
#   cmake -S . -B build -DETASK_ROOT=../..
#   cmake --build build
#   ./build/bombardment
#
# The same tree also builds for ESP32 through platformio.ini - src/ is laid out
# the way PlatformIO expects so that neither build needs its own copy of the
# sources.
cmake_minimum_required(VERSION 3.20)
project(etask_bombardment LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------------------
# This node's identity on the wire (1..254). Nothing here talks to a peer, but
# internal_channel stamps it onto every task it starts, so it has to exist.
# ---------------------------------------------------------------------------------------
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ---------------------------------------------------------------------------------------
# The etask framework.
#
# Taken from the enclosing checkout by default, not from a tag on GitHub. This
# project's job is to test the headers sitting next to it - fetching a released
# etask instead would make the test pass or fail on code the developer is not
# editing, which is the one thing an integration test in-tree must not do.
#
# Point ETASK_ROOT elsewhere to run the same checks against another checkout.
# ---------------------------------------------------------------------------------------
get_filename_component(_default_etask_root "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
set(ETASK_ROOT "${_default_etask_root}" CACHE PATH
    "The etask checkout to build against (defaults to the one containing this test)")

# Checked against the CMake front door rather than a header: a wrong ETASK_ROOT
# otherwise surfaces as add_subdirectory failing on a missing CMakeLists, or -
# worse - as etask_add_schema() being undefined several lines later, neither of
# which names the actual mistake.
if(NOT EXISTS "${ETASK_ROOT}/cmake/etask.cmake")
  message(FATAL_ERROR
    "ETASK_ROOT does not look like an etask checkout: ${ETASK_ROOT}\n"
    "  Expected to find cmake/etask.cmake under it.")
endif()

add_subdirectory("${ETASK_ROOT}" "${CMAKE_CURRENT_BINARY_DIR}/etask")

# ---------------------------------------------------------------------------------------
# The harness: the entry point, the scenarios, and the generated task bodies.
#
# src/main.cpp is deliberately absent - that is the Arduino forwarder, and its
# `setup()`/`loop()` would be dead weight here at best and a clash with the
# core's `main` on the other target. The host entry point is src/host_main.cpp.
#
# Task sources are added by etask_add_schema() below rather than globbed here, so
# there is exactly one place that knows where the generated tree lives.
# ---------------------------------------------------------------------------------------
add_executable(bombardment src/host_main.cpp src/app.cpp)

# ---------------------------------------------------------------------------------------
# Code generation. A plain build only *checks* that the generated code matches
# schema.yaml and stops if it does not; rewriting it is an explicit target:
#
#   cmake --build build --target bombardment-etask-generate
# ---------------------------------------------------------------------------------------
etask_add_schema(bombardment
  SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
  SRC       ${CMAKE_CURRENT_SOURCE_DIR}/src/sys
  GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/src/generated
)

# src/ is the include root, matching what platformio.ini adds on the ESP32 side:
# a task includes "generated/scopes.hpp" and app.cpp includes "config/wiring.hpp",
# both relative to the directory that holds them all.
target_include_directories(bombardment PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(bombardment PRIVATE etask)
target_compile_definitions(bombardment PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})

# The harness exists to provoke the framework's refusal paths, and it must
# provoke them in an optimized build too - so warnings are errors here rather
# than a lint step someone runs separately.
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(bombardment PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

# ---------------------------------------------------------------------------------------
# ctest wiring, so the harness runs under `ctest` alongside etask's own suite.
# verify.py is the richer driver - it explains failures - but a bare non-zero
# exit is enough for CI to notice.
# ---------------------------------------------------------------------------------------
include(CTest)
add_test(NAME bombardment COMMAND bombardment)
