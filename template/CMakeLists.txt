# SPDX-License-Identifier: MIT
#
# Starter CMake for an etask application. Copy this whole directory into a new
# project, then follow README.md: configure, generate, build.
cmake_minimum_required(VERSION 3.20)
project(etask_app LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------------------
# This node's identity on the wire (1..254), used when it initiates tasks itself.
# ---------------------------------------------------------------------------------------
set(ECOMM_BOARD_ID 1 CACHE STRING "This device's ecomm node id (1..254)")

# ---------------------------------------------------------------------------------------
# The etask framework. It transitively brings ecomm + etools, and its repository
# also carries the schema code generator used by the `etask-generate` target below.
# ---------------------------------------------------------------------------------------
include(FetchContent)
FetchContent_Declare(
  etask
  GIT_REPOSITORY https://github.com/MarikTik/etask.git
  GIT_TAG        main   # pin to a release tag for reproducible builds
)
FetchContent_MakeAvailable(etask)

# ---------------------------------------------------------------------------------------
# Code generation: schema.yaml -> tasks/ scaffolds (once) + generated/task_id.hpp (always).
#
#   cmake --build build --target etask-generate
#
# Run this after editing schema.yaml, then re-configure so CMake picks up any
# newly generated tasks/*.cpp (the app sources are globbed at configure time).
# ---------------------------------------------------------------------------------------
find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_custom_target(etask-generate
  COMMAND ${CMAKE_COMMAND} -E env
          PYTHONPATH=${etask_SOURCE_DIR}/tools/src
          ${Python3_EXECUTABLE} -m schemav2.cli generate
          ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
          --out        ${CMAKE_CURRENT_SOURCE_DIR}/tasks
          --task-id    ${CMAKE_CURRENT_SOURCE_DIR}/generated/task_id.hpp
          --task-list  ${CMAKE_CURRENT_SOURCE_DIR}/generated/task_list.hpp
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMENT "etask: generating tasks/ scaffolds and generated/ (task_id, task_list) from schema.yaml"
  VERBATIM
)

# ---------------------------------------------------------------------------------------
# The application: main.cpp + your config .cpp (app.cpp) + the generated task
# bodies under tasks/. (Re-run CMake configure after generating new tasks so the
# globs pick them up.)
# ---------------------------------------------------------------------------------------
file(GLOB_RECURSE APP_CONFIG_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/config/*.cpp")
file(GLOB_RECURSE APP_TASK_SOURCES   CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tasks/*.cpp")

add_executable(app main.cpp ${APP_CONFIG_SOURCES} ${APP_TASK_SOURCES})
target_link_libraries(app PRIVATE etask)
target_compile_definitions(app PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})
