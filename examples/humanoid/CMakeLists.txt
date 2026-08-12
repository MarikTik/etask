#
# Starter CMake for an etask application. This is the *scaffolded* (non-generated)
# half of the project; the generated half - the sys/ task tree and generated/
# (task_id enum + task_list typelist) - comes from `etask generate` on schema.yaml.
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
# Code generation: schema.yaml -> sys/ scaffolds (once) + generated/ (always).
#
#   cmake --build build --target etask-generate
#
# Run this after editing schema.yaml, then re-configure so CMake picks up any
# newly generated sys/**/*.cpp task bodies (globbed at configure time).
#
# The run also maintains .schema.uids.json - the ledger that keeps each task's
# wire uid stable as the schema grows. Commit it alongside schema.yaml: it is
# part of the wire contract, and losing it renumbers tasks your peers know.
#
# It also emits python/tasks.py - the client bindings a PC or Raspberry Pi uses
# to drive this device (see etask-python/). Delete the --python line if this
# project has no Python peer.
# ---------------------------------------------------------------------------------------
find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_custom_target(etask-generate
  COMMAND ${CMAKE_COMMAND} -E env
          PYTHONPATH=${etask_SOURCE_DIR}/etask-python
          ${Python3_EXECUTABLE} -m etask.schema.cli generate
          ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
          --out        ${CMAKE_CURRENT_SOURCE_DIR}/sys
          --task-id    ${CMAKE_CURRENT_SOURCE_DIR}/generated/task_id.hpp
          --task-list  ${CMAKE_CURRENT_SOURCE_DIR}/generated/task_list.hpp
          --python     ${CMAKE_CURRENT_SOURCE_DIR}/python/tasks.py
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMENT "etask: generating sys/ scaffolds and generated/ (task_id, task_list) from schema.yaml"
  VERBATIM
)

# ---------------------------------------------------------------------------------------
# The application: the root entry point + lifecycle (main.cpp, app.cpp), the
# generated task bodies under sys/, and any .cpp you add under hal/ or support/.
# (Re-run CMake configure after adding files so the globs pick them up.)
# ---------------------------------------------------------------------------------------
file(GLOB_RECURSE APP_TASK_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/sys/*.cpp")
file(GLOB_RECURSE APP_LIB_SOURCES  CONFIGURE_DEPENDS
     "${CMAKE_CURRENT_SOURCE_DIR}/hal/*.cpp"
     "${CMAKE_CURRENT_SOURCE_DIR}/support/*.cpp")

add_executable(app main.cpp app.cpp ${APP_TASK_SOURCES} ${APP_LIB_SOURCES})

# The project root is the sole include root: every top-level directory is then
# reachable by its own path from ANY file at ANY depth - `#include "hal/imu/x.hpp"`,
# `#include "support/channels/y.hpp"`, `#include "config/protocol.hpp"` - with no
# `../` walks. Add the root, not each subdir, so the top-level prefix is required
# (and never ambiguous).
target_include_directories(app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(app PRIVATE etask)
target_compile_definitions(app PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})
