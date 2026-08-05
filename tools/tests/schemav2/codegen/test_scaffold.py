# tools/tests/schemav2/codegen/test_scaffold.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

from schemav2.codegen.scaffold import Scaffold, ScaffoldReport

_FILES = [
    "CMakeLists.txt",
    "main.cpp",
    "app.hpp",
    "app.cpp",
    "schema.yaml",
    "config/protocol.hpp",
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

    assert len(report.created) == 10
    assert report.skipped == []


def test_write_is_idempotent_and_preserves_user_edits(tmp_path):
    Scaffold.write(tmp_path)

    app_cpp = tmp_path / "app.cpp"
    sentinel = "\n// USER EDIT SENTINEL\n"
    app_cpp.write_text(app_cpp.read_text() + sentinel)

    report = Scaffold.write(tmp_path)

    assert report.created == []
    assert len(report.skipped) == 10
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


def test_cmakelists_generate_target_points_at_sys(tmp_path):
    Scaffold.write(tmp_path)
    cmake = (tmp_path / "CMakeLists.txt").read_text()
    assert "--out        ${CMAKE_CURRENT_SOURCE_DIR}/sys" in cmake
    assert "sys/*.cpp" in cmake
    assert "/tasks" not in cmake
    assert "/system" not in cmake
