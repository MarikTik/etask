# tools/tests/etask.schema/codegen/test_scaffold.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

from etask.schema.codegen.scaffold import Scaffold, ScaffoldReport

_FILES = [
    "CMakeLists.txt",
    "main.cpp",
    "app.hpp",
    "app.cpp",
    "schema.yaml",
    "config/wiring.hpp",
    "config/router.hpp",
    "hal/README.md",
    "support/README.md",
]


def test_files_lists_all_ten_in_order():
    files = Scaffold.files()
    assert [rel for rel, _ in files] == _FILES


def test_write_creates_all_files(tmp_path):
    report = Scaffold.write(tmp_path)

    for rel in _FILES:
        assert (tmp_path / rel).exists(), rel

    assert len(report.created) == len(_FILES)
    assert report.skipped == []


def test_write_is_idempotent_and_preserves_user_edits(tmp_path):
    Scaffold.write(tmp_path)

    app_cpp = tmp_path / "app.cpp"
    sentinel = "\n// USER EDIT SENTINEL\n"
    app_cpp.write_text(app_cpp.read_text() + sentinel)

    report = Scaffold.write(tmp_path)

    assert report.created == []
    assert len(report.skipped) == len(_FILES)
    assert sentinel in app_cpp.read_text()
    assert str(app_cpp) in report.skipped


def test_app_hpp_lives_at_root_with_own_namespace_and_guard(tmp_path):
    Scaffold.write(tmp_path)
    hpp = (tmp_path / "app.hpp").read_text()
    assert "namespace app {" in hpp
    assert "APP_HPP_" in hpp


def test_wiring_hpp_uses_config_namespace(tmp_path):
    Scaffold.write(tmp_path)
    wiring = (tmp_path / "config" / "wiring.hpp").read_text()
    assert "namespace config {" in wiring


def test_hal_ships_a_readme_not_a_header(tmp_path):
    Scaffold.write(tmp_path)
    # hal/ is documented, not seeded with an example header
    assert not (tmp_path / "hal" / "example_motor.hpp").exists()
    readme = (tmp_path / "hal" / "README.md").read_text()
    assert "namespace hal" in readme
    assert "nest" in readme.lower()                 # encourages directories-in-directories
    assert 'hal/motor/brushless.hpp' in readme       # root-relative include example


def test_support_ships_a_readme_not_a_header(tmp_path):
    Scaffold.write(tmp_path)
    assert not (tmp_path / "support" / "example_channel.hpp").exists()
    readme = (tmp_path / "support" / "README.md").read_text()
    assert "namespace support" in readme
    assert "nest" in readme.lower()
    assert "support/channels/uart_channel.hpp" in readme
    assert "serial_channel" not in readme


def test_top_level_dirs_are_includable_from_anywhere(tmp_path):
    Scaffold.write(tmp_path)
    cmake = (tmp_path / "CMakeLists.txt").read_text()
    # the project root is the include root -> `#include "hal/..."` works at any depth
    assert "target_include_directories(app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})" in cmake
    # hal/ and support/ .cpp files are compiled into the app
    assert "hal/*.cpp" in cmake
    assert "support/*.cpp" in cmake


def test_main_cpp_drives_app_lifecycle_no_config_setup(tmp_path):
    Scaffold.write(tmp_path)
    main_cpp = (tmp_path / "main.cpp").read_text()
    assert "app::setup()" in main_cpp
    assert "app::loop()" in main_cpp

    for rel in _FILES:
        text = (tmp_path / rel).read_text()
        assert "config::setup" not in text


def test_cmakelists_generates_through_the_supported_entry_point(tmp_path):
    # The previous version of this test asserted the raw `--out ...` flags of a
    # hand-rolled custom target, which is how that target kept passing while
    # pointing `PYTHONPATH` at `tools/src` - a directory that no longer exists.
    # Every scaffolded project got a CMakeLists that could not generate. So the
    # assertion is now about *which entry point* is used: `etask_add_schema()`
    # owns the flags, and cannot go stale relative to the CLI it invokes.
    Scaffold.write(tmp_path)
    cmake = (tmp_path / "CMakeLists.txt").read_text()

    assert "etask_add_schema(app" in cmake
    assert "tools/src" not in cmake, "the generator no longer lives there"
    assert "-m etask.schema.cli" not in cmake, "the CLI is called via the helper"

    for required in ("SCHEMA", "SRC", "GENERATED"):
        assert required in cmake, f"etask_add_schema needs {required}"


def test_cmakelists_generation_is_attached_after_the_target_exists(tmp_path):
    # `etask_add_schema()` fails with a FATAL_ERROR if its target is not defined
    # yet, so the order in the emitted file is load-bearing rather than stylistic.
    Scaffold.write(tmp_path)
    cmake = (tmp_path / "CMakeLists.txt").read_text()
    assert cmake.index("add_executable(app") < cmake.index("etask_add_schema(app")


def test_cmakelists_still_globs_the_task_tree(tmp_path):
    Scaffold.write(tmp_path)
    cmake = (tmp_path / "CMakeLists.txt").read_text()
    assert "sys/*.cpp" in cmake
    # Two earlier names for the task tree; neither should reappear as a source
    # directory. Anchored to the glob rather than matched bare, so that an
    # unrelated mention - `python/tasks.py` is one - does not read as a relapse.
    assert "/tasks/*.cpp" not in cmake
    assert "/system/*.cpp" not in cmake
