# etask-python/tests/schema/codegen/test_tier_codegen.py
# SPDX-License-Identifier: MIT
"""What each tier generates: base class, hooks, and the drift the emitter reports."""

import pathlib

import pytest

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter


def generate(tmp_path: pathlib.Path, schema: str):
    tmp_path.mkdir(parents=True, exist_ok=True)
    sp = tmp_path / "schema.yaml"
    sp.write_text(schema)
    out = tmp_path / "sys"
    report = Emitter.generate(Tree.build(sp), out)
    return out, report


# ------------------------------------------------------------- base classes


@pytest.mark.parametrize("tier", ["instant_task", "oneshot_task", "polled_task", "stateful_task"])
def test_task_derives_from_its_tier(tmp_path, tier):
    out, _ = generate(tmp_path, f"t:\n  type: {tier}\n")
    assert f"class t : public {tier} {{" in (out / "t.hpp").read_text()


def test_instant_task_declares_no_hooks_at_all(tmp_path):
    """Its constructor is the whole task - there is no lifecycle to override."""
    out, _ = generate(tmp_path, "stop:\n  type: instant_task\n  params: { hard: bool }\n")
    hpp = (out / "stop.hpp").read_text()
    for hook in ("on_execute", "on_pause", "on_resume"):
        assert f"void {hook}() override;" not in hpp
    assert "is_finished() override;" not in hpp
    assert "on_complete(" not in hpp
    # but it is still a real task: uid and typed constructor
    assert "static constexpr global::task_id uid" in hpp
    assert "stop(bool hard, context& ctx);" in hpp

    cpp = (out / "stop.cpp").read_text()
    assert "this constructor *is* the task" in cpp


def test_oneshot_task_executes_but_cannot_override_is_finished(tmp_path):
    """is_finished is sealed final in the base, so the scaffold must not declare it."""
    out, _ = generate(tmp_path, "read:\n  type: oneshot_task\n  returns: { v: float }\n")
    hpp = (out / "read.hpp").read_text()
    assert "void on_execute() override;" in hpp
    # The class doc explains that is_finished is sealed; what must not appear is
    # a *declaration* of it, which would not compile against the final base.
    assert "is_finished() override;" not in hpp
    assert "on_complete(etask::core::completion_reason reason) override;" in hpp


def test_polled_task_decides_when_it_is_finished(tmp_path):
    out, _ = generate(tmp_path, "spin:\n  type: polled_task\n")
    hpp = (out / "spin.hpp").read_text()
    assert "void on_execute() override;" in hpp
    assert "bool is_finished() override;" in hpp
    assert "on_pause" not in hpp


def test_stateful_task_carries_the_suspension_pair(tmp_path):
    out, _ = generate(tmp_path, "hold:\n  type: stateful_task\n")
    hpp = (out / "hold.hpp").read_text()
    for hook in ("on_execute", "is_finished", "on_pause", "on_resume"):
        assert hook in hpp


def test_no_tier_generates_on_start(tmp_path):
    """on_start is gone from the framework; setup belongs in the constructor."""
    for tier in ("instant_task", "oneshot_task", "polled_task", "stateful_task"):
        out, _ = generate(tmp_path / tier, f"t:\n  type: {tier}\n")
        assert "on_start" not in (out / "t.hpp").read_text()
        assert "on_start" not in (out / "t.cpp").read_text()


# ---------------------------------------------------------------- task.hpp


def test_task_base_file_binds_every_tier(tmp_path):
    out, _ = generate(tmp_path, "t:\n  type: polled_task\n")
    text = (out / "task.hpp").read_text()
    assert "etask::core::instant_task;" in text
    assert "etask::core::oneshot_task<global::task_id>;" in text
    assert "etask::core::polled_task<global::task_id>;" in text
    assert "etask::core::stateful_task<global::task_id>;" in text


def test_stale_task_base_is_reported_not_overwritten(tmp_path):
    """A project predating the tiers keeps its file, and is told what it lacks."""
    out, _ = generate(tmp_path, "t:\n  type: polled_task\n")
    task_hpp = out / "task.hpp"
    task_hpp.write_text("using task = etask::core::task<global::task_id>;\n")

    sp = tmp_path / "schema.yaml"
    report = Emitter.generate(Tree.build(sp), out)

    assert task_hpp.read_text() == "using task = etask::core::task<global::task_id>;\n"
    note = "\n".join(report.notes)
    assert "predates the task tiers" in note
    assert "instant_task" in note and "stateful_task" in note


# ------------------------------------------------------------- tier drift


def test_changing_a_tier_is_reported(tmp_path):
    """The generator never rewrites a body, so a tier change needs a hand edit."""
    sp = tmp_path / "schema.yaml"
    sp.write_text("t:\n  type: polled_task\n")
    out = tmp_path / "sys"
    Emitter.generate(Tree.build(sp), out)

    sp.write_text("t:\n  type: stateful_task\n")
    report = Emitter.generate(Tree.build(sp), out)

    note = "\n".join(report.notes)
    assert "is now a stateful_task" in note
    assert "still derives from polled_task" in note
    assert "on_pause" in note        # says which hooks it now needs


def test_no_drift_note_when_the_tier_is_unchanged(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("t:\n  type: polled_task\n")
    out = tmp_path / "sys"
    Emitter.generate(Tree.build(sp), out)
    report = Emitter.generate(Tree.build(sp), out)
    assert not [n for n in report.notes if "still derives from" in n]


# ------------------------------------------------------------- task_list


def test_task_list_routes_each_tier_to_its_manager(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "cmd:\n  type: instant_task\n"
        "once:\n  type: oneshot_task\n"
        "poll:\n  type: polled_task\n"
        "hold:\n  type: stateful_task\n"
    )
    out = tmp_path / "sys"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), out, task_list_path=list_path)
    text = list_path.read_text()

    instant = text.split("using instant_tasks")[1].split(">;")[0]
    polled = text.split("using polled_tasks")[1].split(">;")[0]
    stateful = text.split("using stateful_tasks")[1].split(">;")[0]

    assert "sys::cmd" in instant
    # A oneshot task is a polled task: same manager, same list.
    assert "sys::once" in polled and "sys::poll" in polled
    assert "sys::hold" in stateful
    assert "sys::cmd" not in polled and "sys::hold" not in polled


# --------------------------------------------------------- python bindings


def test_instant_command_binding_is_synchronous(tmp_path):
    """An instant task sends no reply, so awaiting one would hang forever."""
    from etask.schema.codegen.python_file import PythonFile

    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "cmd:\n  type: instant_task\n  params: { hard: bool }\n"
        "once:\n  type: oneshot_task\n  returns: { v: float }\n"
    )
    root = Tree.build(sp)
    text = PythonFile.render(root, root.uid_bytes or 1)

    cmd = text.split("class _Cmd(")[1].split("class ")[0]
    assert "InstantTaskBinding" in text.split("class _Cmd(")[1][:40]
    assert "def __call__(self, *, hard: bool) -> None:" in cmd
    assert "async def" not in cmd
    assert "self._dispatch(" in cmd

    once = text.split("class _Once(")[1].split("class ")[0]
    assert "async def __call__" in once
    assert "self._invoke(" in once
