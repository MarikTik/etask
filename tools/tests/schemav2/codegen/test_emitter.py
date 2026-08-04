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
    # every scope gets a context, plus the system root at the out root
    assert (out / "context.hpp").exists()                    # system::context (root)
    assert (out / "arm" / "context.hpp").exists()            # composes arm.shoulder
    assert (out / "arm" / "shoulder" / "context.hpp").exists()
    assert (out / "system" / "context.hpp").exists()
    assert (out / "task.hpp").exists()                       # the task-base alias
    assert len(report.created) == 9  # task.hpp + 4 task files + 4 contexts
    assert report.updated == []


def test_hpp_has_native_typed_ctor_with_context_last(tmp_path):
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(build(tmp_path)), out)
    hpp = (out / "arm" / "shoulder" / "move.hpp").read_text()
    assert "move(float angle, std::uint8_t speed, context& ctx); //! etask:sig" in hpp
    assert '#include "context.hpp"' in hpp
    assert "namespace sys::arm::shoulder {" in hpp
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
        "        // Add this scope's own hardware handles / state here.",
        "        int pin = 5;  // USER",
    ))
    report = Emitter.generate(Tree.build(build(tmp_path)), out)
    # a scope's own state is user-owned: never rewritten
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
    assert len(report.unchanged) == 9  # task.hpp + 4 task files + 4 contexts


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
    assert "etools::memory::buffer<> on_complete(etask::core::completion_reason reason) override;" in with_ret_hpp
    assert '#include <etools/memory/buffer.hpp>' in with_ret_hpp
    with_ret_cpp = (out / "s" / "with_ret.cpp").read_text()
    assert "buffer<> with_ret::on_complete(" in with_ret_cpp
    assert "etask::core::completion_reason reason" in with_ret_cpp

    # a no-return task emits no on_complete OVERRIDE and no buffer include
    # (it uses the base default). The lifecycle doc may still *mention* it.
    no_ret_hpp = (out / "s" / "no_ret.hpp").read_text()
    assert "on_complete(etask::core::completion_reason reason) override;" not in no_ret_hpp
    assert "#include <etools/memory/buffer.hpp>" not in no_ret_hpp
    no_ret_cpp = (out / "s" / "no_ret.cpp").read_text()
    assert "::on_complete(" not in no_ret_cpp


def test_root_level_task_receives_system_context(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("reboot:\n  type: task\n  params: {}\n")
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    hpp = (out / "reboot.hpp").read_text()
    # a root task now receives the system::context (the composition root)
    assert "reboot(context& ctx); //! etask:sig" in hpp
    assert '#include "context.hpp"' in hpp
    assert "namespace sys {" in hpp
    # the system::context itself is generated at the out root
    root_ctx = (out / "context.hpp").read_text()
    assert "namespace sys {" in root_ctx
    assert "struct context {" in root_ctx


def test_task_docs_carry_brief_and_description(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "blink:\n"
        "  type: task\n"
        "  brief: toggle the status LED\n"
        "  description: |\n"
        "    Drives the on-board LED. Off by default; each run flips it.\n"
        "  params: {}\n"
    )
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    hpp = (out / "blink.hpp").read_text()
    # brief appears at file and class level; description as the class detail.
    assert "* @brief toggle the status LED" in hpp
    assert "Drives the on-board LED. Off by default; each run flips it." in hpp
    # every lifecycle hook is documented
    for hook in ("on_start", "on_execute", "on_pause", "on_resume", "is_finished"):
        assert f"void {hook}() override;" in hpp or f"bool {hook}() override;" in hpp
    assert "@brief One-time setup" in hpp          # on_start doc
    assert "must not persist" in hpp               # on_pause doc


def test_on_complete_return_doc_enumerates_returns(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "read:\n"
        "  type: task\n"
        "  returns: { ax: float, ay: float }\n"
    )
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    hpp = (out / "read.hpp").read_text()
    assert "reason == completion_reason::finished" in hpp
    assert "- ax : float" in hpp
    assert "- ay : float" in hpp


def test_positional_returns_documented_by_index(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "grasp:\n"
        "  type: task\n"
        "  returns: [uint8, float]\n"
    )
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    hpp = (out / "grasp.hpp").read_text()
    assert "- [0] : std::uint8_t" in hpp
    assert "- [1] : float" in hpp


def test_context_doc_uses_scope_brief(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "motor:\n"
        "  type: scope\n"
        "  brief: a DC motor and its driver\n"
        "  children:\n"
        "    spin:\n"
        "      type: task\n"
        "      params: { duty: uint8 }\n"
    )
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    ctx = (out / "motor" / "context.hpp").read_text()
    assert "a DC motor and its driver" in ctx
    assert "sys::motor" in ctx


def test_comment_delimiter_in_description_is_escaped(tmp_path):
    # A user's brief/description could contain */ - which would close the
    # generated /** */ block early. It must be escaped, not emitted raw.
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "blink:\n"
        "  type: task\n"
        "  brief: 'toggles */ the LED /* now'\n"
        "  description: 'ends with */'\n"
        "  params: {}\n"
    )
    out = tmp_path / "tasks"
    from schemav2.tree import Tree
    from schemav2.codegen.emitter import Emitter
    Emitter.generate(Tree.build(sp), out)
    hpp = (out / "blink.hpp").read_text()
    # the raw closing delimiter must not survive anywhere except the real block ends
    assert "*/ the LED" not in hpp
    assert "ends with */" not in hpp
    assert "* /" in hpp        # escaped form present
    # the only real block-closers are the guarded ones, not user text
