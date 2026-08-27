# tools/tests/etask.schema/codegen/test_doc_sync.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
#
# End-to-end doc behaviour through the emitter: schema-derived doc blocks stay in
# sync until the user edits them, and no license is forced on the user's code.

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter


def _schema(tmp_path, brief):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "motor:\n"
        "  type: scope\n"
        "  brief: a DC motor\n"
        "  children:\n"
        "    spin:\n"
        "      type: polled_task\n"
        f"      brief: {brief}\n"
        "      params: { duty: uint8 }\n"
    )
    return sp


def _regen(sp, out):
    return Emitter.generate(Tree.build(sp), out)


# --------------------------------------------------------------- no forced license

def test_generated_files_carry_no_license(tmp_path):
    out = tmp_path / "sys"
    _regen(_schema(tmp_path, "spin the motor"), out)
    for rel in ("task.hpp", "context.hpp", "motor/spin.hpp", "motor/spin.cpp",
                "motor/context.hpp"):
        assert "SPDX-License-Identifier" not in (out / rel).read_text(), rel


# --------------------------------------------------------------- sync until touched

def test_untouched_task_doc_resyncs_from_schema(tmp_path):
    sp = _schema(tmp_path, "spin the motor")
    out = tmp_path / "sys"
    _regen(sp, out)
    hpp = out / "motor" / "spin.hpp"
    assert "@brief spin the motor" in hpp.read_text()

    # schema brief changes; the doc was never touched -> it re-syncs
    _schema(tmp_path, "spin FASTER")            # overwrites sp in place
    report = _regen(sp, out)
    text = hpp.read_text()
    assert "@brief spin FASTER" in text
    assert "spin the motor" not in text
    assert str(hpp) in report.updated


def test_edited_task_doc_is_preserved_on_regen(tmp_path):
    sp = _schema(tmp_path, "spin the motor")
    out = tmp_path / "sys"
    _regen(sp, out)
    hpp = out / "motor" / "spin.hpp"

    # user rewrites the (class) brief by hand
    hpp.write_text(hpp.read_text().replace("* @brief spin the motor",
                                           "* @brief HAND WRITTEN", 1))

    # schema brief changes -> the edited block must NOT be clobbered
    _schema(tmp_path, "something else entirely")
    _regen(sp, out)
    text = hpp.read_text()
    assert "HAND WRITTEN" in text
    # the block the user took over does not get the new schema text
    assert text.count("@brief something else entirely") <= 1  # only the still-synced block, if any


def test_edited_block_freezes_only_itself(tmp_path):
    sp = _schema(tmp_path, "brief one")
    out = tmp_path / "sys"
    _regen(sp, out)
    hpp = out / "motor" / "spin.hpp"

    # edit only the FIRST @brief occurrence (the @file block); leave the class block
    original = hpp.read_text()
    hpp.write_text(original.replace("* @brief brief one", "* @brief FILE EDIT", 1))

    _schema(tmp_path, "brief two")
    _regen(sp, out)
    text = hpp.read_text()
    assert "FILE EDIT" in text                 # edited file block kept
    assert "@brief brief two" in text          # untouched class block re-synced


def test_untouched_context_doc_resyncs_from_schema(tmp_path):
    sp = _schema(tmp_path, "spin the motor")
    out = tmp_path / "sys"
    _regen(sp, out)
    ctx = out / "motor" / "context.hpp"
    assert "a DC motor" in ctx.read_text()

    # change the scope brief; context doc untouched -> re-syncs
    sp.write_text(sp.read_text().replace("brief: a DC motor", "brief: a brushless motor"))
    _regen(sp, out)
    assert "a brushless motor" in ctx.read_text()


def test_edited_context_doc_is_preserved(tmp_path):
    sp = _schema(tmp_path, "spin the motor")
    out = tmp_path / "sys"
    _regen(sp, out)
    ctx = out / "motor" / "context.hpp"
    ctx.write_text(ctx.read_text().replace("a DC motor", "MY MOTOR NOTES"))

    sp.write_text(sp.read_text().replace("brief: a DC motor", "brief: a stepper motor"))
    _regen(sp, out)
    text = ctx.read_text()
    assert "MY MOTOR NOTES" in text
    assert "a stepper motor" not in text
