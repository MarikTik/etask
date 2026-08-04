# tools/tests/schemav2/codegen/test_task_list_file.py
# SPDX-License-Identifier: MIT

from schemav2.tree import Tree
from schemav2.codegen.emitter import Emitter
from schemav2.codegen.task_list_file import TaskListFile


def test_render_typelist_no_trailing_comma():
    out = TaskListFile.render([
        ("../tasks/blink.hpp", "sys::blink"),
        ("../tasks/motor/spin.hpp", "sys::motor::spin"),
    ])
    assert "using task_list = etools::meta::typelist<" in out
    assert "sys::blink," in out          # non-last has comma
    assert "sys::motor::spin" in out
    assert "sys::motor::spin," not in out  # last has NO trailing comma (ill-formed)
    assert '#include "../tasks/blink.hpp"' in out
    assert "namespace generated {" in out
    assert "DO NOT EDIT" in out


def test_render_empty_is_wellformed():
    out = TaskListFile.render([])
    assert "using task_list = etools::meta::typelist<>;" in out


def test_emit_task_list_relative_includes(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "blink:\n  type: task\n"
        "motor:\n  type: scope\n  children:\n"
        "    spin:\n      type: task\n      params: { duty: uint8 }\n"
    )
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    report = Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    text = list_path.read_text()
    # includes are relative from generated/ to tasks/
    assert '#include "../tasks/blink.hpp"' in text
    assert '#include "../tasks/motor/spin.hpp"' in text
    assert "sys::blink," in text
    assert "sys::motor::spin" in text
    assert str(list_path) in report.created


def test_task_list_always_regenerated(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("blink:\n  type: task\n")
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    list_path.write_text("// hand edit\n")
    report = Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    assert "// hand edit" not in list_path.read_text()   # overwritten
    assert str(list_path) in report.updated


def test_concurrency_lowers_to_capacity(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "blink:\n  type: task\n"                          # default 1 -> bare
        "mover:\n  type: task\n  concurrency: 3\n"         # -> capacity<..., 3>
    )
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    text = list_path.read_text()
    assert "sys::blink," in text                        # bare, unchanged
    assert "etools::factories::utils::capacity<sys::mover, 3>" in text
    assert "#include <etools/factories/utils/capacity.hpp>" in text


def test_no_capacity_include_when_all_bare(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("blink:\n  type: task\n  concurrency: 1\n")   # explicit 1 == bare
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    text = list_path.read_text()
    assert "capacity<" not in text
    assert "factories/utils/capacity.hpp" not in text
