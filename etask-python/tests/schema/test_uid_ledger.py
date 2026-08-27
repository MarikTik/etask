# tools/tests/etask.schema/test_uid_ledger.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import json

import pytest

from etask.schema.tree import Tree
from etask.schema.uid_ledger import UidLedger


# -----------------------
# Helpers
# -----------------------

def write(tmp_path, data, name="schema.json"):
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return path


def task(**extra):
    body = {"type": "polled_task", "params": {}}
    body.update(extra)
    return body


def uids_by_path(root, prefix=""):
    found = {}
    for name, child in root.children.items():
        path = f"{prefix}{name}"
        if child.is_task:
            found[path] = child.uid
        else:
            found.update(uids_by_path(child, f"{path}."))
    return found


def schema_of(names):
    return {name: task() for name in names}


# -----------------------
# File format
# -----------------------

def test_missing_file_loads_empty(tmp_path):
    ledger = UidLedger.load(tmp_path / "nope.uids.json")
    assert ledger.uids == {}
    assert ledger.retired == {}
    assert ledger.uid_bytes is None


def test_roundtrip_is_sorted_and_versioned(tmp_path):
    path = tmp_path / "s.uids.json"
    ledger = UidLedger(uid_bytes=2, uids={"b": 2, "a": 1}, retired={"z": 9})
    ledger.save(path)

    data = json.loads(path.read_text())
    assert data["version"] == 1
    assert data["uid_bytes"] == 2
    assert list(data["uids"]) == ["a", "b"]        # sorted, for readable diffs
    assert data["retired"] == {"z": 9}

    again = UidLedger.load(path)
    assert again.uids == {"a": 1, "b": 2}
    assert again.retired == {"z": 9}
    assert again.uid_bytes == 2


def test_unknown_version_is_refused(tmp_path):
    path = tmp_path / "s.uids.json"
    path.write_text(json.dumps({"version": 99, "uids": {}}))
    with pytest.raises(ValueError, match="version 99"):
        UidLedger.load(path)


def test_non_integer_uid_is_refused(tmp_path):
    path = tmp_path / "s.uids.json"
    path.write_text(json.dumps({"version": 1, "uids": {"a": "1"}}))
    with pytest.raises(ValueError, match="integer uid"):
        UidLedger.load(path)


# -----------------------
# Stickiness
# -----------------------

def test_uids_survive_adding_a_task(tmp_path):
    ledger = UidLedger()
    first = Tree.build(write(tmp_path, schema_of(["a", "b"])), ledger)
    before = uids_by_path(first)

    second = Tree.build(write(tmp_path, schema_of(["a", "b", "c"])), ledger)
    after = uids_by_path(second)

    assert {k: after[k] for k in before} == before
    assert after["c"] not in before.values()


def test_uids_survive_crossing_a_byte_boundary(tmp_path):
    # The width jump is exactly the case that used to renumber the whole project:
    # 256 tasks fit one byte, 257 do not.
    ledger = UidLedger()
    small = Tree.build(write(tmp_path, schema_of([f"t{i}" for i in range(256)])), ledger)
    before = uids_by_path(small)
    assert small.uid_bytes == 1

    big = Tree.build(write(tmp_path, schema_of([f"t{i}" for i in range(257)])), ledger)
    after = uids_by_path(big)

    assert big.uid_bytes == 2
    assert {k: after[k] for k in before} == before  # every pre-existing uid held


def test_width_never_narrows_again(tmp_path):
    ledger = UidLedger()
    Tree.build(write(tmp_path, schema_of([f"t{i}" for i in range(257)])), ledger)
    shrunk = Tree.build(write(tmp_path, schema_of(["a", "b"])), ledger)
    assert shrunk.uid_bytes == 2


def test_removed_task_is_retired_and_its_uid_reserved(tmp_path):
    ledger = UidLedger()
    Tree.build(write(tmp_path, schema_of(["a", "b"])), ledger)
    retired_uid = ledger.uids["b"]

    Tree.build(write(tmp_path, schema_of(["a"])), ledger)
    assert ledger.retired == {"b": retired_uid}
    assert "b" not in ledger.uids

    # a brand-new task must not inherit the retired id
    root = Tree.build(write(tmp_path, schema_of(["a", "c", "d", "e"])), ledger)
    assert retired_uid not in uids_by_path(root).values()


def test_readding_a_removed_task_restores_its_uid(tmp_path):
    ledger = UidLedger()
    Tree.build(write(tmp_path, schema_of(["a", "b"])), ledger)
    original = ledger.uids["b"]

    Tree.build(write(tmp_path, schema_of(["a"])), ledger)
    root = Tree.build(write(tmp_path, schema_of(["a", "b"])), ledger)

    assert uids_by_path(root)["b"] == original
    assert ledger.retired == {}


def test_explicit_uid_wins_and_the_move_is_warned(tmp_path):
    ledger = UidLedger()
    Tree.build(write(tmp_path, schema_of(["a", "b"])), ledger)
    taken = ledger.uids["b"]

    root = Tree.build(
        write(tmp_path, {"a": task(uid=taken), "b": task()}),
        ledger,
    )

    after = uids_by_path(root)
    assert after["a"] == taken           # the schema's explicit uid stands
    assert after["b"] != taken           # b was pushed off its id
    assert any("uid" in w and "'b'" in w for w in ledger.warnings)


def test_no_warning_on_a_quiet_regeneration(tmp_path):
    ledger = UidLedger()
    schema = write(tmp_path, schema_of(["a", "b"]))
    Tree.build(schema, ledger)
    Tree.build(schema, ledger)
    assert ledger.warnings == []


def test_rekey_moves_a_task_and_its_subtree(tmp_path):
    ledger = UidLedger(uid_bytes=1, uids={"arm.move": 7, "arm.grip.close": 8, "leg.move": 9})
    assert ledger.rekey("arm", "wing")
    assert ledger.uids == {"wing.move": 7, "wing.grip.close": 8, "leg.move": 9}


def test_rekey_reports_when_nothing_matched():
    ledger = UidLedger(uids={"a": 1})
    assert not ledger.rekey("b", "c")


def test_renamed_task_keeps_its_uid_via_rekey(tmp_path):
    ledger = UidLedger()
    Tree.build(write(tmp_path, {"arm": {"type": "scope", "children": {"move": task()}}}), ledger)
    original = ledger.uids["arm.move"]

    ledger.rekey("arm.move", "arm.glide")
    root = Tree.build(
        write(tmp_path, {"arm": {"type": "scope", "children": {"glide": task()}}}), ledger
    )
    assert uids_by_path(root)["arm.glide"] == original


# -----------------------
# Order independence
# -----------------------

def test_uids_do_not_depend_on_sibling_order(tmp_path):
    forward = Tree.build(write(tmp_path, schema_of(["a", "b", "c", "d"])))
    backward = Tree.build(write(tmp_path, schema_of(["d", "c", "b", "a"])))
    assert uids_by_path(forward) == uids_by_path(backward)


def test_without_a_ledger_uids_are_still_pure(tmp_path):
    # No ledger == no stickiness guarantee, but two identical schemas must still
    # produce identical uids.
    schema = write(tmp_path, schema_of(["a", "b"]))
    assert uids_by_path(Tree.build(schema)) == uids_by_path(Tree.build(schema))
