# tools/tests/etask.schema/test_cli.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import json

from etask.schema.cli import main


_SCHEMA = """
arm:
  type: scope
  children:
    move:
      type: polled_task
      params: { angle: float }
    grip:
      type: polled_task
      params: {}
"""


def write_schema(tmp_path, text=_SCHEMA):
    path = tmp_path / "schema.yaml"
    path.write_text(text)
    return path


def generate(tmp_path, *extra):
    schema = tmp_path / "schema.yaml"
    return main(["generate", str(schema), "--out", str(tmp_path / "sys"), *extra])


def test_generate_writes_the_ledger_next_to_the_schema(tmp_path):
    write_schema(tmp_path)
    assert generate(tmp_path) == 0

    ledger = tmp_path / ".schema.uids.json"
    assert ledger.exists()
    data = json.loads(ledger.read_text())
    assert set(data["uids"]) == {"arm.move", "arm.grip"}
    assert data["uid_bytes"] == 1


def test_regenerating_after_an_edit_keeps_every_uid(tmp_path):
    write_schema(tmp_path)
    generate(tmp_path)
    before = json.loads((tmp_path / ".schema.uids.json").read_text())["uids"]

    write_schema(tmp_path, _SCHEMA + "halt:\n  type: polled_task\n  params: {}\n")
    generate(tmp_path)
    after = json.loads((tmp_path / ".schema.uids.json").read_text())["uids"]

    assert {k: after[k] for k in before} == before
    assert "halt" in after


def test_no_uid_ledger_writes_nothing(tmp_path):
    write_schema(tmp_path)
    assert generate(tmp_path, "--no-uid-ledger") == 0
    assert not (tmp_path / ".schema.uids.json").exists()


def test_custom_ledger_path_is_honored(tmp_path):
    write_schema(tmp_path)
    custom = tmp_path / "wire" / "ids.json"
    assert generate(tmp_path, "--uid-ledger", str(custom)) == 0
    assert custom.exists()
    assert not (tmp_path / ".schema.uids.json").exists()


def test_rename_carries_the_uid_to_the_new_path(tmp_path):
    schema = write_schema(tmp_path)
    generate(tmp_path)
    before = json.loads((tmp_path / ".schema.uids.json").read_text())["uids"]["arm.move"]

    assert main(["rename", str(schema), "--out", str(tmp_path / "sys"),
                 "arm.move", "glide"]) == 0
    generate(tmp_path)

    after = json.loads((tmp_path / ".schema.uids.json").read_text())
    assert after["uids"]["arm.glide"] == before   # same task, same wire id
    assert "arm.move" not in after["uids"]
    assert after["retired"] == {}                 # it moved, it did not die


def test_rename_without_the_ledger_leaves_it_alone(tmp_path):
    schema = write_schema(tmp_path)
    generate(tmp_path)
    original = json.loads((tmp_path / ".schema.uids.json").read_text())["uids"]

    assert main(["rename", str(schema), "--out", str(tmp_path / "sys"),
                 "arm.move", "glide", "--no-uid-ledger"]) == 0
    assert json.loads((tmp_path / ".schema.uids.json").read_text())["uids"] == original
