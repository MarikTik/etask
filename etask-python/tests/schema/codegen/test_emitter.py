# tools/tests/etask.schema/codegen/test_emitter.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import pytest

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter

_SCHEMA = """
arm:
  type: scope
  children:
    shoulder:
      type: scope
      children:
        move:
          type: polled_task
          params: { angle: float, speed: uint8 }
system:
  type: scope
  children:
    reboot:
      type: polled_task
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
        "      type: polled_task\n"
        "      params: {}\n"
        "      returns: { ok: bool }\n"
        "    no_ret:\n"
        "      type: polled_task\n"
        "      params: {}\n"
    )
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)

    with_ret_hpp = (out / "s" / "with_ret.hpp").read_text()
    assert "etask::core::outcome on_complete(etask::core::completion_reason reason) override;" in with_ret_hpp
    assert '#include <etask/core/outcome.hpp>' in with_ret_hpp
    with_ret_cpp = (out / "s" / "with_ret.cpp").read_text()
    assert "etask::core::outcome with_ret::on_complete(" in with_ret_cpp
    assert "etask::core::completion_reason reason" in with_ret_cpp

    # a no-return task emits no on_complete OVERRIDE and no outcome include
    # (it uses the base default). The lifecycle doc may still *mention* it.
    no_ret_hpp = (out / "s" / "no_ret.hpp").read_text()
    assert "on_complete(etask::core::completion_reason reason) override;" not in no_ret_hpp
    assert "#include <etask/core/outcome.hpp>" not in no_ret_hpp
    no_ret_cpp = (out / "s" / "no_ret.cpp").read_text()
    assert "::on_complete(" not in no_ret_cpp


def test_root_level_task_receives_system_context(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("reboot:\n  type: polled_task\n  params: {}\n")
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
        "  type: polled_task\n"
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
    # the hooks this tier carries are declared and documented - and only those
    for hook in ("on_execute", "is_finished"):
        assert f"void {hook}() override;" in hpp or f"bool {hook}() override;" in hpp
    # a polled_task cannot be suspended, so it pays for no suspension hooks
    for hook in ("on_pause", "on_resume"):
        assert f"void {hook}() override;" not in hpp
    # on_start is gone from the framework: setup belongs in the constructor
    assert "on_start" not in hpp
    # the hooks it does have carry their framework-authored docs
    assert "@brief One slice of work" in hpp                    # on_execute doc
    assert "@brief Whether the task is done" in hpp             # is_finished doc


def test_on_complete_return_doc_enumerates_returns(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "read:\n"
        "  type: polled_task\n"
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
        "  type: polled_task\n"
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
        "      type: polled_task\n"
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
        "  type: polled_task\n"
        "  brief: 'toggles */ the LED /* now'\n"
        "  description: 'ends with */'\n"
        "  params: {}\n"
    )
    out = tmp_path / "tasks"
    from etask.schema.tree import Tree
    from etask.schema.codegen.emitter import Emitter
    Emitter.generate(Tree.build(sp), out)
    hpp = (out / "blink.hpp").read_text()
    # the raw closing delimiter must not survive anywhere except the real block ends
    assert "*/ the LED" not in hpp
    assert "ends with */" not in hpp
    assert "* /" in hpp        # escaped form present
    # the only real block-closers are the guarded ones, not user text


# -----------------------
# Prepare-then-commit
# -----------------------

def test_a_broken_anchor_leaves_the_tree_untouched(tmp_path):
    # A mangled //! etask:sig anchor is discovered while planning the *second*
    # task. Nothing may have been written by then - not the first task's update,
    # not the brand-new task's files.
    from etask.schema.errors.anchor_not_found_error import AnchorNotFoundError

    sp = build(tmp_path)
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)

    move_hpp = out / "arm" / "shoulder" / "move.hpp"
    reboot_hpp = out / "system" / "reboot.hpp"
    reboot_hpp.write_text(reboot_hpp.read_text().replace(" //! etask:sig", ""))
    before = {p: p.read_text() for p in out.rglob("*.?pp")}

    # both existing tasks gain a param, and a third task appears
    sp.write_text(
        _SCHEMA.replace("params: { angle: float, speed: uint8 }",
                        "params: { angle: float, speed: uint8, ramp: uint16 }")
               .replace("      params: {}\n", "      params: { force: bool }\n")
        + "    halt:\n      type: polled_task\n      params: {}\n"
    )

    with pytest.raises(AnchorNotFoundError):
        Emitter.generate(Tree.build(sp), out)

    assert {p: p.read_text() for p in out.rglob("*.?pp")} == before  # no partial rewrite
    assert not (out / "system" / "halt.hpp").exists()                # and nothing created


def test_generated_files_are_not_written_when_planning_fails(tmp_path):
    from etask.schema.errors.anchor_not_found_error import AnchorNotFoundError

    sp = build(tmp_path)
    out = tmp_path / "tasks"
    task_id = tmp_path / "generated" / "task_id.hpp"
    Emitter.generate(Tree.build(sp), out, task_id)
    before = task_id.read_text()

    move_hpp = out / "arm" / "shoulder" / "move.hpp"
    move_hpp.write_text(move_hpp.read_text().replace(" //! etask:sig", ""))
    sp.write_text(_SCHEMA.replace("params: { angle: float, speed: uint8 }",
                                  "params: { angle: float, speed: uint8, ramp: uint16 }")
                  + "extra:\n  type: polled_task\n  params: {}\n")

    with pytest.raises(AnchorNotFoundError):
        Emitter.generate(Tree.build(sp), out, task_id)

    assert task_id.read_text() == before  # the enum did not move ahead of the tree


def test_no_temp_files_are_left_behind(tmp_path):
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(build(tmp_path)), out)
    assert [p.name for p in out.rglob("*.tmp")] == []


# -----------------------
# Schema/firmware drift the emitter cannot fix itself
# -----------------------

def test_a_task_that_gains_returns_later_is_reported(tmp_path):
    # Only the ctor signature is reconciled in an existing task file, so adding
    # `returns:` to an already-generated task produces no on_complete at all.
    # That must not pass silently: the schema would promise a result the
    # firmware never sends.
    sp = tmp_path / "schema.yaml"
    sp.write_text("t:\n  type: polled_task\n  params: {}\n")
    out = tmp_path / "tasks"
    assert Emitter.generate(Tree.build(sp), out).notes == []

    sp.write_text("t:\n  type: polled_task\n  params: {}\n  returns: { ok: bool }\n")
    report = Emitter.generate(Tree.build(sp), out)

    assert len(report.notes) == 1
    assert "declares returns" in report.notes[0]
    assert "on_complete" in report.notes[0]


def test_a_freshly_generated_task_with_returns_is_not_reported(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("t:\n  type: polled_task\n  returns: { ok: bool }\n")
    report = Emitter.generate(Tree.build(sp), tmp_path / "tasks")
    assert report.notes == []
    # ...and the override really is there.
    assert "on_complete(etask::core::completion_reason" in (tmp_path / "tasks" / "t.hpp").read_text()
