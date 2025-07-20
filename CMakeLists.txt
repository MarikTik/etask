cmake_minimum_required(VERSION 3.20)
project(etask LANGUAGES CXX)

# Required C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# --- Fetch dependencies ---
include(FetchContent)
FetchContent_Declare(
  ser
  GIT_REPOSITORY https://github.com/MarikTik/ser.git
  GIT_TAG main
)
FetchContent_MakeAvailable(ser)

# --- Declare etask header-only interface library ---
add_library(etask INTERFACE)

# Public headers (etask is the root include dir)
target_include_directories(etask
  INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
)

# Internal headers (only for local builds/tests)
target_include_directories(etask
  INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/etask/internal>
)

# Link to dependencies
target_link_libraries(etask INTERFACE ser)

# --- Install all public headers under include/etask ---
install(
  DIRECTORY etask/
  DESTINATION include/etask
  FILES_MATCHING PATTERN "*.hpp"
)

# --- Executable for local testing ---
add_executable(lib_test example/main.cpp)
target_link_libraries(lib_test etask)
