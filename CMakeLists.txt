cmake_minimum_required(VERSION 3.20)
project(etask)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
include(FetchContent)

FetchContent_Declare(
  ser
  GIT_REPOSITORY https://github.com/MarikTik/ser.git
  GIT_TAG main
)

FetchContent_MakeAvailable(ser)

add_executable(${PROJECT_NAME} src/main.cpp)

target_link_libraries(${PROJECT_NAME} ser)