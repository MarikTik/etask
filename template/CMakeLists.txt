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
# The application: the root entry point + lifecycle (main.cpp, app.cpp), the
# generated task bodies under sys/, and any .cpp you add under hal/ or support/.
# (Re-run CMake configure after adding files so the globs pick them up.)
# ---------------------------------------------------------------------------------------
file(GLOB_RECURSE APP_LIB_SOURCES  CONFIGURE_DEPENDS
     "${CMAKE_CURRENT_SOURCE_DIR}/hal/*.cpp"
     "${CMAKE_CURRENT_SOURCE_DIR}/support/*.cpp")

add_executable(app main.cpp app.cpp ${APP_LIB_SOURCES})

# ---------------------------------------------------------------------------------------
# Code generation: schema.yaml -> sys/ scaffolds (once) + generated/ (always).
#
#   cmake --build build --target app-etask-generate
#
# Run that after editing schema.yaml. A plain build never regenerates on its own -
# rewriting your tree as a side effect of compiling can clobber an edit you are in
# the middle of, and a build has no terminal to ask from. Instead it checks, and
# stops with the command above if the schema has moved ahead.
#
# The run also maintains .schema.uids.json - the ledger that keeps each task's
# wire uid stable as the schema grows. Commit it alongside schema.yaml: it is
# part of the wire contract, and losing it renumbers tasks your peers know.
#
# Add PYTHON to also emit the typed client a PC or Pi drives this node with.
# ---------------------------------------------------------------------------------------
etask_add_schema(app
  SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
  SRC       ${CMAKE_CURRENT_SOURCE_DIR}/sys
  GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/generated
  # PYTHON  ${CMAKE_CURRENT_SOURCE_DIR}/python/tasks.py
)

# The project root is the sole include root: every top-level directory is then
# reachable by its own path from ANY file at ANY depth - `#include "hal/imu/x.hpp"`,
# `#include "support/channels/y.hpp"`, `#include "config/protocol.hpp"` - with no
# `../` walks. Add the root, not each subdir, so the top-level prefix is required
# (and never ambiguous).
target_include_directories(app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(app PRIVATE etask)
target_compile_definitions(app PRIVATE ECOMM_BOARD_ID=${ECOMM_BOARD_ID})
