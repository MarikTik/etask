# etask-python/tests/schema/test_freshness.py
# SPDX-License-Identifier: MIT
"""The staleness gate a build runs before compiling."""

import os
import pathlib

from etask.schema.freshness import Freshness
from etask.schema.cli import Cli


def project(tmp_path: pathlib.Path):
    """A schema and one generated file, the generated one newer."""
    schema = tmp_path / "schema.yaml"
    schema.write_text("t:\n  type: polled_task\n")
    generated = tmp_path / "generated" / "task_id.hpp"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text("// generated\n")
    _make_newer(generated, schema)
    return schema, generated


def _make_newer(newer: pathlib.Path, older: pathlib.Path) -> None:
    """Forces an unambiguous mtime ordering, whatever the filesystem's resolution."""
    stamp = older.stat().st_mtime + 10
    os.utime(newer, (stamp, stamp))


# ------------------------------------------------------------------ the check


def test_generated_newer_than_schema_is_fresh(tmp_path):
    schema, generated = project(tmp_path)
    assert Freshness.check(schema, [generated]).is_fresh


def test_schema_newer_than_generated_is_stale(tmp_path):
    schema, generated = project(tmp_path)
    _make_newer(schema, generated)
    state = Freshness.check(schema, [generated])
    assert not state.is_fresh
    assert state.stale == [generated]


def test_never_generated_is_missing_not_stale(tmp_path):
    """A project that has never been generated needs a different sentence."""
    schema = tmp_path / "schema.yaml"
    schema.write_text("t:\n  type: polled_task\n")
    absent = tmp_path / "generated" / "task_id.hpp"
    state = Freshness.check(schema, [absent])
    assert state.missing == [absent]
    assert not state.stale


def test_report_names_the_callers_own_command(tmp_path):
    """A user pasting another build system's command is a bad first experience."""
    schema, generated = project(tmp_path)
    _make_newer(schema, generated)
    report = Freshness.check(schema, [generated]).report("pio run -t etask-generate")
    assert "pio run -t etask-generate" in report
    assert str(generated) in report
    # and it must say the build did not silently rewrite anything
    assert "will not regenerate on its own" in report


# ------------------------------------------------------------------- the CLI


def outputs(tmp_path: pathlib.Path):
    return [
        str(tmp_path / "schema.yaml"),
        "--out", str(tmp_path / "sys"),
        "--task-id", str(tmp_path / "generated" / "task_id.hpp"),
        "--task-list", str(tmp_path / "generated" / "task_list.hpp"),
        "--scopes", str(tmp_path / "generated" / "scopes.hpp"),
    ]


def test_check_fails_before_first_generate(tmp_path):
    (tmp_path / "schema.yaml").write_text("t:\n  type: polled_task\n")
    assert Cli.main(["check"] + outputs(tmp_path)) == 1


def test_check_passes_right_after_generate(tmp_path):
    """The gate must not fire on a project that was just regenerated.

    Worth pinning: the emitter skips rewriting a file whose content is already
    correct, so without re-stamping those the check would report a project stale
    forever and regenerating would never clear it.
    """
    (tmp_path / "schema.yaml").write_text("t:\n  type: polled_task\n")
    assert Cli.main(["generate"] + outputs(tmp_path)) == 0
    assert Cli.main(["check"] + outputs(tmp_path)) == 0

    # ...and a second generate, which changes nothing at all, still leaves it fresh
    assert Cli.main(["generate"] + outputs(tmp_path)) == 0
    assert Cli.main(["check"] + outputs(tmp_path)) == 0


def test_check_fails_again_once_the_schema_moves_ahead(tmp_path):
    schema = tmp_path / "schema.yaml"
    schema.write_text("t:\n  type: polled_task\n")
    assert Cli.main(["generate"] + outputs(tmp_path)) == 0

    schema.write_text("t:\n  type: polled_task\nu:\n  type: instant_task\n")
    _make_newer(schema, tmp_path / "generated" / "task_id.hpp")
    assert Cli.main(["check"] + outputs(tmp_path)) == 1


def test_check_ignores_scaffolds(tmp_path):
    """Scaffolds are generate-once and user-owned, so an old one is correct."""
    schema = tmp_path / "schema.yaml"
    schema.write_text("t:\n  type: polled_task\n")
    assert Cli.main(["generate"] + outputs(tmp_path)) == 0

    # A task body older than the schema is the normal state of a file you wrote.
    body = tmp_path / "sys" / "t.cpp"
    os.utime(body, (0, 0))
    assert Cli.main(["check"] + outputs(tmp_path)) == 0
