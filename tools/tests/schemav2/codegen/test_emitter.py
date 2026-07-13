# tools/tests/schemav2/codegen/test_emitter.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

from schemav2.tree import Tree
from schemav2.codegen.emitter import Emitter

_SCHEMA = """
arm:
  type: scope
  children:
    shoulder:
      type: scope
      children:
        move:
          type: task
          params: { angle: float, speed: uint8 }
system:
  type: scope
  children:
    reboot:
      type: task
      params: {}
"""


def build(tmp_path, text=_SCHEMA):
    sp = tmp_path / "schema.yaml"
    sp.write_text(text)
    return sp


def test_generate_creates_dir_tree(tmp_path):
    out = tmp_path / "tasks"
    report = Emitter.generate(Tree.build(build(tmp_path)), out)

    assert (out / "arm" / "shoulder" / "move.hpp").exists()
    assert (out / "arm" / "shoulder" / "move.cpp").exists()
    assert (out / "system" / "reboot.hpp").exists()
    # task-owning scopes (shoulder, system) each get a context.hpp; arm does not
    assert (out / "arm" / "shoulder" / "context.hpp").exists()
    assert (out / "system" / "context.hpp").exists()
    assert not (out / "arm" / "context.hpp").exists()
    assert len(report.created) == 6  # 4 task files + 2 contexts
    assert report.updated == []


def test_hpp_has_native_typed_ctor_with_context_last(tmp_path):
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(build(tmp_path)), out)
    hpp = (out / "arm" / "shoulder" / "move.hpp").read_text()
    assert "move(float angle, std::uint8_t speed, context& ctx); //! etask:sig" in hpp
    assert '#include "context.hpp"' in hpp
    assert "namespace tasks::arm::shoulder {" in hpp
    assert "global::task_id::arm_shoulder_move" in hpp


def test_cpp_marks_only_context_maybe_unused(tmp_path):
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(build(tmp_path)), out)
    cpp = (out / "arm" / "shoulder" / "move.cpp").read_text()
    # params bare, context last and [[maybe_unused]]
    assert "move::move(float angle, std::uint8_t speed, [[maybe_unused]] context& ctx)" in cpp


def test_context_class_generated_once(tmp_path):
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(build(tmp_path)), out)
    ctx = out / "arm" / "shoulder" / "context.hpp"
    ctx.write_text(ctx.read_text().replace(
        "        // TODO: add hardware handles / state for this scope.",
        "        int pin = 5;  // USER",
    ))
    report = Emitter.generate(Tree.build(build(tmp_path)), out)
    # context is user-owned: never rewritten
    assert "int pin = 5;  // USER" in ctx.read_text()
    assert str(ctx) in report.unchanged


def test_regenerate_updates_ctor_preserving_bodies(tmp_path):
    sp = build(tmp_path)
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)

    # user fills a body
    cpp_path = out / "arm" / "shoulder" / "move.cpp"
    cpp = cpp_path.read_text().replace(
        "        // TODO: initialize the task from its parameters.",
        "        _angle = angle;  // USER",
    )
    cpp_path.write_text(cpp)

    # schema param added
    sp.write_text(_SCHEMA.replace(
        "params: { angle: float, speed: uint8 }",
        "params: { angle: float, speed: uint8, ramp: uint16 }",
    ))
    report = Emitter.generate(Tree.build(sp), out)

    updated = cpp_path.read_text()
    assert "std::uint16_t ramp" in updated          # ctor updated
    assert "_angle = angle;  // USER" in updated      # body preserved
    assert cpp_path.as_posix() in [p.replace("\\", "/") for p in report.updated]


def test_regenerate_unchanged_when_schema_same(tmp_path):
    sp = build(tmp_path)
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    report = Emitter.generate(Tree.build(sp), out)
    assert report.created == []
    assert report.updated == []
    assert len(report.unchanged) == 6  # 4 task files + 2 contexts


def test_cpp_has_no_include_guard(tmp_path):
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(build(tmp_path)), out)
    cpp = (out / "arm" / "shoulder" / "move.cpp").read_text()
    assert "#ifndef" not in cpp
    assert "#endif" not in cpp
    # the .hpp still guards
    assert "#ifndef" in (out / "arm" / "shoulder" / "move.hpp").read_text()


def test_on_complete_emitted_only_with_returns(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "s:\n  type: scope\n  children:\n"
        "    with_ret:\n"
        "      type: task\n"
        "      params: {}\n"
        "      returns: { ok: bool }\n"
        "    no_ret:\n"
        "      type: task\n"
        "      params: {}\n"
    )
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)

    with_ret_hpp = (out / "s" / "with_ret.hpp").read_text()
    assert "etools::memory::buffer<> on_complete(bool interrupted) override;" in with_ret_hpp
    assert '#include <etools/memory/buffer.hpp>' in with_ret_hpp
    with_ret_cpp = (out / "s" / "with_ret.cpp").read_text()
    assert "buffer<> with_ret::on_complete" in with_ret_cpp

    no_ret_hpp = (out / "s" / "no_ret.hpp").read_text()
    assert "on_complete" not in no_ret_hpp
    assert "buffer" not in no_ret_hpp


def test_root_level_task_has_no_context(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("reboot:\n  type: task\n  params: {}\n")
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    hpp = (out / "reboot.hpp").read_text()
    assert "reboot(); //! etask:sig" in hpp
    assert "context" not in hpp
    assert not (out / "context.hpp").exists()
