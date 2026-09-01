# etask-python/tests/schema/codegen/test_wire_region.py
# SPDX-License-Identifier: MIT
"""The wire-contract block: `uid`, `params`, `scope`.

These three declarations are the framework's, not the user's, and they are what
the manager reads to build a task from a request payload. They were emitted once
and never refreshed, which meant adding a parameter to an existing task rewrote
its constructor and left `params` naming the old argument list - so the device
decoded a different argument list than the peer encoded, and it compiled.
"""

import pathlib

import pytest

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter
from etask.schema.codegen.naming import Naming
from etask.schema.codegen.wire_region import WireRegion


ONE_PARAM = (
    "system:\n"
    "  motor:\n"
    "    type: scope\n"
    "    children:\n"
    "      spin:\n"
    "        type: polled_task\n"
    "        params: { duty: uint8 }\n"
)

TWO_PARAMS = (
    "system:\n"
    "  motor:\n"
    "    type: scope\n"
    "    children:\n"
    "      spin:\n"
    "        type: polled_task\n"
    "        params: { duty: uint8, ramp: float }\n"
)


def generate(tmp_path, schema):
    """Generates into `tmp_path`, returning the task header's text and path."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    schema_path = tmp_path / "schema.yaml"
    schema_path.write_text(schema)
    out = tmp_path / "sys"
    report = Emitter.generate(
        Tree.build(schema_path), out,
        task_id_path=tmp_path / "generated" / "task_id.hpp",
        scopes_path=tmp_path / "generated" / "scopes.hpp",
    )
    header = out / "motor" / "spin.hpp"
    return header.read_text(), header, report


# ------------------------------------------------------------------ the markers

def test_a_generated_task_carries_the_markers(tmp_path):
    text, _, _ = generate(tmp_path, ONE_PARAM)
    assert Naming.wire_begin in text
    assert Naming.wire_end in text
    assert text.index(Naming.wire_begin) < text.index(Naming.wire_end)


def test_the_block_holds_all_three_declarations(tmp_path):
    text, _, _ = generate(tmp_path, ONE_PARAM)
    block = "".join(WireRegion.extract(text))
    assert "static constexpr global::task_id uid" in block
    assert "using params =" in block
    assert "scope_index_t scope =" in block


# ---------------------------------------------------------------- reconciliation

def test_adding_a_parameter_refreshes_params(tmp_path):
    """The bug this region exists for.

    `params` is what the manager unpacks a payload according to, so a stale one
    makes the device decode a different argument list than the peer sent - while
    still compiling, and while the generated Python client has the new
    signature. The two ends then disagree with nothing to notice it.
    """
    text, _, _ = generate(tmp_path, ONE_PARAM)
    assert "typelist<std::uint8_t>" in text

    # Same directory, so the second run updates rather than creates.
    text, _, _ = generate(tmp_path, TWO_PARAMS)
    assert "typelist<std::uint8_t, float>" in text, "params must track the schema"
    assert "typelist<std::uint8_t>;" not in text, "the old list must be gone"


def test_the_constructor_and_params_agree_after_a_change(tmp_path):
    """They are two statements of one fact and must not be able to disagree."""
    generate(tmp_path, ONE_PARAM)
    text, _, _ = generate(tmp_path, TWO_PARAMS)

    assert "spin(std::uint8_t duty, float ramp, context& ctx);" in text
    assert "typelist<std::uint8_t, float>" in text


def test_a_users_body_survives_reconciliation(tmp_path):
    _, header, _ = generate(tmp_path, ONE_PARAM)
    text = header.read_text().replace(
        "        bool is_finished() override;",
        "        bool is_finished() override;\n\n"
        "        /// Mine.\n        int my_own_member = 7;",
    )
    header.write_text(text)

    text, _, _ = generate(tmp_path, TWO_PARAMS)
    assert "int my_own_member = 7;" in text, "a user's member must not be touched"
    assert "typelist<std::uint8_t, float>" in text


def test_reconciliation_is_idempotent(tmp_path):
    generate(tmp_path, ONE_PARAM)
    first, _, _ = generate(tmp_path, ONE_PARAM)
    second, _, report = generate(tmp_path, ONE_PARAM)
    assert first == second


# -------------------------------------------------------------------- migration

def test_a_file_predating_the_markers_is_detected(tmp_path):
    text, _, _ = generate(tmp_path, ONE_PARAM)
    # Strip whole marker lines: the markers are indented, so replacing the bare
    # form would leave the indentation behind.
    old = "\n".join(
        line for line in text.splitlines()
        if Naming.wire_begin not in line and Naming.wire_end not in line
    )
    assert WireRegion.needs_migration(old)
    assert not WireRegion.needs_migration(text)


def test_migration_adds_the_markers_and_refreshes_the_block(tmp_path):
    """Done for the user, not asked of them.

    The alternative is a note per task file telling them to delete a block by
    hand - dozens of identical edits on a real project, and until they are made
    the declarations stay stale. A migration nobody performs is not one.
    """
    text, header, _ = generate(tmp_path, ONE_PARAM)
    old = "\n".join(
        line for line in text.splitlines()
        if Naming.wire_begin not in line and Naming.wire_end not in line
    ) + "\n"
    header.write_text(old)

    migrated, _, report = generate(tmp_path, TWO_PARAMS)
    assert Naming.wire_begin in migrated
    assert "typelist<std::uint8_t, float>" in migrated
    assert not [note for note in report.notes if "could not be located" in note]


def test_migration_preserves_a_member_below_the_block(tmp_path):
    """The cut is bounded by the declarations, not by the closing brace.

    Cutting to the brace would be simpler and would delete whatever the user put
    after the block - which some projects do.
    """
    text, header, _ = generate(tmp_path, ONE_PARAM)
    lines = [
        line for line in text.splitlines()
        if Naming.wire_begin not in line and Naming.wire_end not in line
    ]
    # A member after the wire declarations, before the class closes.
    closing = lines.index("    };")
    lines[closing:closing] = ["", "    private:", "        int mine_ = 3;"]
    header.write_text("\n".join(lines) + "\n")

    migrated, _, _ = generate(tmp_path, TWO_PARAMS)
    assert "int mine_ = 3;" in migrated, "a member below the block must survive"
    assert "typelist<std::uint8_t, float>" in migrated


def test_an_unlocatable_block_is_reported_not_guessed(tmp_path):
    """A wrong cut would delete the user's code, so it declines instead."""
    fresh, _, _ = generate(tmp_path, ONE_PARAM)
    assert WireRegion.migrate("struct nothing {};", fresh) is None
