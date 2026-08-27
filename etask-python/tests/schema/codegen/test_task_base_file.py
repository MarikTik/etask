# tools/tests/etask.schema/codegen/test_task_base_file.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter

_SCHEMA = """
blink:
  type: polled_task
  params: {}
"""


def build(tmp_path, text=_SCHEMA):
    sp = tmp_path / "schema.yaml"
    sp.write_text(text)
    return sp


def test_task_hpp_created_at_root_with_alias_guard_and_include(tmp_path):
    out = tmp_path / "sys"
    Emitter.generate(Tree.build(build(tmp_path)), out)

    task_hpp = out / "task.hpp"
    assert task_hpp.exists()
    text = task_hpp.read_text()
    assert "using instant_task  = etask::core::instant_task;" in text
    assert "using oneshot_task  = etask::core::oneshot_task<global::task_id>;" in text
    assert "using polled_task   = etask::core::polled_task<global::task_id>;" in text
    assert "using stateful_task = etask::core::stateful_task<global::task_id>;" in text
    assert "#ifndef SYS_TASK_HPP_" in text
    assert "#define SYS_TASK_HPP_" in text
    assert '#include "../generated/task_id.hpp"' in text


def test_task_hpp_created_once_never_overwritten(tmp_path):
    sp = build(tmp_path)
    out = tmp_path / "sys"
    Emitter.generate(Tree.build(sp), out)

    task_hpp = out / "task.hpp"
    sentinel = "\n// USER EDIT SENTINEL\n"
    task_hpp.write_text(task_hpp.read_text() + sentinel)

    report = Emitter.generate(Tree.build(sp), out)

    assert sentinel in task_hpp.read_text()
    assert str(task_hpp) in report.unchanged
    assert str(task_hpp) not in report.updated
