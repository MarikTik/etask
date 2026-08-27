# etask.cmake - the CMake front door to the etask code generator.
#
# Exported from the package config, so it works identically whether etask was
# brought in with FetchContent or found with find_package(etask).
#
#   etask_add_schema(app
#     SCHEMA    ${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml
#     SRC       ${CMAKE_CURRENT_SOURCE_DIR}/src/sys
#     GENERATED ${CMAKE_CURRENT_SOURCE_DIR}/src/generated
#   )
#
# See etask_add_schema() below for the full argument list.

include_guard(GLOBAL)

# Where the generator lives, relative to this file. Set once here rather than at
# call time: this file is installed next to the package config, and a consumer's
# CMAKE_CURRENT_LIST_DIR would point at their project, not at etask.
set(_ETASK_CMAKE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "etask cmake module directory")

#[[
Locates the Python package that contains the code generator.

The generator ships *inside* etask - same repository, same tag as the headers -
so that a generator and the runtime it emits against can never be a version
apart. This finds that copy in either of the two layouts etask is consumed in:
a source checkout (FetchContent) or an installed package.

Sets ETASK_PYTHON_ROOT in the caller's scope, or leaves it undefined.
]]
function(_etask_find_generator)
  # cmake/etask.cmake -> the repo root -> etask-python/   (source checkout)
  get_filename_component(_source_root "${_ETASK_CMAKE_DIR}" DIRECTORY)
  # lib/cmake/etask/etask.cmake -> the prefix -> share/etask/python/  (installed)
  get_filename_component(_install_prefix "${_ETASK_CMAKE_DIR}/../../.." ABSOLUTE)

  foreach(_candidate
      "${_source_root}/etask-python"
      "${_install_prefix}/share/etask/python")
    if(EXISTS "${_candidate}/etask/schema/cli.py")
      set(ETASK_PYTHON_ROOT "${_candidate}" PARENT_SCOPE)
      return()
    endif()
  endforeach()
endfunction()

#[[
Wires a target's schema into the build.

Adds two things to the project:

  <target>-etask-generate   rewrites the generated code sections from the schema
  a pre-build freshness check on <target>

The check is what makes this safe to leave in place. It never regenerates:
rewriting a source tree as a side effect of building can clobber a half-finished
edit, and a build cannot ask first - there is no terminal under CI, in an IDE, or
in a background build. So a build whose generated code has fallen behind the
schema fails, naming the command that fixes it.

Arguments:
  SCHEMA     the schema file. Required.
  SRC        directory for task scaffolds - created once, then the user's.
             Required.
  GENERATED  directory for the always-regenerated projections of the schema
             (task ids, per-tier task lists, scope accessors). Required.
  PYTHON     optional path for the generated Python client bindings, for a PC or
             Pi peer. Omitted means they are not generated.
  UID_LEDGER optional path for the uid ledger, the committed record that keeps
             each task's wire uid stable as the schema grows. Defaults to
             .<schema>.uids.json beside the schema. Commit whichever it is: it
             is part of the wire contract.

The generated directory is added to the target's include path, and every
generated .cpp under SRC is added to its sources.
]]
function(etask_add_schema target)
  set(_one_value SCHEMA SRC GENERATED PYTHON UID_LEDGER)
  cmake_parse_arguments(ETASK "" "${_one_value}" "" ${ARGN})

  foreach(_required SCHEMA SRC GENERATED)
    if(NOT ETASK_${_required})
      message(FATAL_ERROR
        "etask_add_schema(${target}): ${_required} is required.\n"
        "  etask_add_schema(${target}\n"
        "    SCHEMA    \${CMAKE_CURRENT_SOURCE_DIR}/schema.yaml\n"
        "    SRC       \${CMAKE_CURRENT_SOURCE_DIR}/src/sys\n"
        "    GENERATED \${CMAKE_CURRENT_SOURCE_DIR}/src/generated)")
    endif()
  endforeach()

  if(NOT TARGET ${target})
    message(FATAL_ERROR
      "etask_add_schema(${target}): no such target. Create it with add_executable() "
      "or add_library() first - this function attaches generation to an existing target.")
  endif()

  find_package(Python3 REQUIRED COMPONENTS Interpreter)

  _etask_find_generator()
  if(NOT ETASK_PYTHON_ROOT)
    message(FATAL_ERROR
      "etask_add_schema(${target}): the code generator was not found.\n"
      "  It ships inside etask (etask-python/), so this means etask was installed "
      "without it. Reinstall etask, or install the generator directly:\n"
      "    pip install etask[codegen]")
  endif()

  # The arguments `generate` and `check` share. Building them once is what keeps
  # the check honest: it asks about exactly the files generation would write.
  set(_cli_args
    "${ETASK_SCHEMA}"
    --out "${ETASK_SRC}"
    --task-id "${ETASK_GENERATED}/task_id.hpp"
    --task-list "${ETASK_GENERATED}/task_list.hpp"
    --scopes "${ETASK_GENERATED}/scopes.hpp")
  if(ETASK_PYTHON)
    list(APPEND _cli_args --python "${ETASK_PYTHON}")
  endif()
  if(ETASK_UID_LEDGER)
    set(_generate_args ${_cli_args} --uid-ledger "${ETASK_UID_LEDGER}")
  else()
    set(_generate_args ${_cli_args})
  endif()

  set(_runner ${CMAKE_COMMAND} -E env
      "PYTHONPATH=${ETASK_PYTHON_ROOT}"
      ${Python3_EXECUTABLE} -m etask.schema.cli)

  set(_generate_target ${target}-etask-generate)
  add_custom_target(${_generate_target}
    COMMAND ${_runner} generate ${_generate_args}
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    COMMENT "etask: regenerating ${target}'s generated sections from ${ETASK_SCHEMA}"
    VERBATIM)

  # The freshness gate, run before the target compiles. `check` writes nothing
  # and exits non-zero when the schema has moved ahead of the generated code, so
  # a stale build stops here with instructions rather than compiling something
  # that no longer matches its schema.
  set(_check_target ${target}-etask-check)
  add_custom_target(${_check_target}
    COMMAND ${_runner} check ${_cli_args}
            --hint "cmake --build ${CMAKE_BINARY_DIR} --target ${_generate_target}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    COMMENT "etask: checking ${target}'s generated code against ${ETASK_SCHEMA}"
    VERBATIM)
  add_dependencies(${target} ${_check_target})

  # Generated task bodies are globbed rather than derived from the schema: CMake
  # would have to run the generator at configure time to know their names, and
  # that is the silent regeneration this design exists to avoid. CONFIGURE_DEPENDS
  # re-globs when the directory changes, so a newly generated task is picked up
  # without a manual re-configure on the generators that support it.
  file(GLOB_RECURSE _task_sources CONFIGURE_DEPENDS "${ETASK_SRC}/*.cpp")
  if(_task_sources)
    target_sources(${target} PRIVATE ${_task_sources})
  endif()

  # The generated headers include the contexts beside them, and a task includes
  # `generated/scopes.hpp` by a path relative to the tree root - so the directory
  # *containing* both is the include root, not either one of them.
  get_filename_component(_generated_parent "${ETASK_GENERATED}" DIRECTORY)
  target_include_directories(${target} PRIVATE "${_generated_parent}")
endfunction()
