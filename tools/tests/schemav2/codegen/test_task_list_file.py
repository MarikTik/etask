# tools/tests/schemav2/codegen/test_task_list_file.py
# SPDX-License-Identifier: MIT

from schemav2.tree import Tree
from schemav2.codegen.emitter import Emitter
from schemav2.codegen.task_list_file import TaskListFile


def test_render_typelist_no_trailing_comma():
    out = TaskListFile.render([
        ("../tasks/blink.hpp", "tasks::blink"),
        ("../tasks/motor/spin.hpp", "tasks::motor::spin"),
    ])
    assert "using task_list = etools::meta::typelist<" in out
    assert "tasks::blink," in out          # non-last has comma
    assert "tasks::motor::spin" in out
    assert "tasks::motor::spin," not in out  # last has NO trailing comma (ill-formed)
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
    assert "tasks::blink," in text
    assert "tasks::motor::spin" in text
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
