# tools/tests/etask.schema/codegen/test_renamer.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import pytest

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter
from etask.schema.codegen.naming import Naming
from etask.schema.codegen.renamer import Renamer
from etask.schema.errors.rename_error import RenameError
from etask.schema.errors.invalid_identifier_error import InvalidIdentifierError

_SCHEMA = """\
system:
  system:
    type: scope
    children:
      reboot:            # keep this comment
        type: polled_task
        params: {}
  motor:
    type: abstract_scope
    instances: [m1, m2]
    children:
      on:
        type: polled_task
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
    assert "      restart:            # keep this comment" in schema_text
    assert "reboot" not in schema_text

    # files renamed, tokens rewritten, body preserved
    assert not (out / "system" / "reboot.hpp").exists()
    hpp = (out / "system" / "restart.hpp").read_text()
    assert "class restart : public polled_task" in hpp
    assert "SYS_SYSTEM_RESTART_HPP_" in hpp
    assert "global::task_id::system_restart" in hpp
    new_cpp = (out / "system" / "restart.cpp").read_text()
    # reboot sits under the `system` scope, so its ctor takes the injected context
    assert "restart::restart([[maybe_unused]] context& ctx)" in new_cpp
    assert "do_reboot();  // USER" in new_cpp


def test_rename_collision_raises(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n"
        "  s:\n    type: scope\n    children:\n"
        "      a: { type: polled_task, params: {} }\n"
        "      b: { type: polled_task, params: {} }\n"
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


def test_rename_targets_the_anchored_constructor_not_the_first_text_match(tmp_path):
    """An earlier textual `Old(` must not be mistaken for the constructor.

    The rewrite used a blind first-match regex, so anything shaped like a call
    on the class name - a doc example, an overload, a factory - that appeared
    above the constructor was renamed instead, leaving the real constructor
    declared under its old name and the file uncompilable.

    `//! etask:sig` marks the constructor unambiguously, and is what
    `SignatureUpdater` already keys on; this pins the renamer to the same anchor.
    """
    sp, out = setup(tmp_path)

    hpp = out / "system" / "reboot.hpp"
    text = hpp.read_text()
    # A doc example naming the class, sitting above the anchored constructor.
    # This is the decoy: it is the first `reboot(` in the file.
    text = text.replace(
        "    class reboot :",
        "    /// Usage: `auto t = reboot(ctx);` - a doc example, not the ctor.\n"
        "    class reboot :",
    )
    hpp.write_text(text)

    Renamer.rename(sp, out, "system.reboot", "restart")

    renamed = (out / "system" / "restart.hpp").read_text()
    # Naming.anchor, not the bare words: the generated doc block mentions
    # "(etask:sig)" in prose, and that line is not the constructor.
    anchored = [ln for ln in renamed.splitlines() if Naming.anchor in ln]
    assert anchored, "the constructor anchor went missing"
    # The constructor itself is what must carry the new name.
    assert "restart(" in anchored[0], (
        f"the anchored constructor was not renamed: {anchored[0]!r}"
    )
    # And no declaration of the old constructor may survive anywhere.
    assert "reboot(" not in renamed.replace(
        "auto t = reboot(ctx)", ""      # the decoy prose may keep its wording
    )
