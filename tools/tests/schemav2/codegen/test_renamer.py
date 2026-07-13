# tools/tests/schemav2/codegen/test_renamer.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import pytest

from schemav2.tree import Tree
from schemav2.codegen.emitter import Emitter
from schemav2.codegen.renamer import Renamer
from schemav2.errors.rename_error import RenameError
from schemav2.errors.invalid_identifier_error import InvalidIdentifierError

_SCHEMA = """\
system:
  type: scope
  children:
    reboot:            # keep this comment
      type: task
      uid: 200
      params: {}
motor:
  type: abstract_scope
  instances: [m1, m2]
  children:
    on:
      type: task
      params: {}
"""


def setup(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(_SCHEMA)
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    return sp, out


def test_rename_concrete_task(tmp_path):
    sp, out = setup(tmp_path)
    # user body in the .cpp
    cpp = out / "system" / "reboot.cpp"
    cpp.write_text(cpp.read_text().replace(
        "        // TODO: initialize the task from its parameters.",
        "        do_reboot();  // USER",
    ))

    old, new = Renamer.rename(sp, out, "system.reboot", "restart")
    assert (old, new) == ("reboot", "restart")

    # schema: key renamed, comment + formatting preserved
    schema_text = sp.read_text()
    assert "    restart:            # keep this comment" in schema_text
    assert "reboot" not in schema_text

    # files renamed, tokens rewritten, body preserved
    assert not (out / "system" / "reboot.hpp").exists()
    hpp = (out / "system" / "restart.hpp").read_text()
    assert "class restart : public task" in hpp
    assert "TASKS_SYSTEM_RESTART_HPP_" in hpp
    assert "global::task_id::system_restart" in hpp
    new_cpp = (out / "system" / "restart.cpp").read_text()
    # reboot sits under the `system` scope, so its ctor takes the injected context
    assert "restart::restart([[maybe_unused]] context& ctx)" in new_cpp
    assert "do_reboot();  // USER" in new_cpp


def test_rename_collision_raises(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "s:\n  type: scope\n  children:\n"
        "    a: { type: task, params: {} }\n"
        "    b: { type: task, params: {} }\n"
    )
    out = tmp_path / "tasks"
    Emitter.generate(Tree.build(sp), out)
    with pytest.raises(RenameError):
        Renamer.rename(sp, out, "s.a", "b")


def test_rename_bad_identifier_raises(tmp_path):
    sp, out = setup(tmp_path)
    with pytest.raises(InvalidIdentifierError):
        Renamer.rename(sp, out, "system.reboot", "2bad")


def test_rename_through_abstract_scope_unsupported(tmp_path):
    sp, out = setup(tmp_path)
    with pytest.raises(RenameError):
        Renamer.rename(sp, out, "motor.on", "spin")


def test_rename_unknown_task_raises(tmp_path):
    sp, out = setup(tmp_path)
    with pytest.raises(RenameError):
        Renamer.rename(sp, out, "system.nope", "x")
