# tools/tests/etask.schema/test_fingerprint.py
# SPDX-License-Identifier: MIT

import copy
import json

import pytest
import yaml

from etask.schema.fingerprint import Fingerprint
from etask.schema.tree import Tree


def write(tmp_path, data, name="schema.yaml"):
    path = tmp_path / name
    path.write_text(yaml.dump(data))
    return path


def fingerprint(tmp_path, data, name="schema.yaml"):
    return Fingerprint.hex(Tree.build(write(tmp_path, data, name)))


#: A contract with one of everything the fingerprint is supposed to cover.
_BASE = {
    "system": {
        "spin": {"type": "polled_task", "params": {"duty": "uint8"}},
        "read": {"type": "oneshot_task", "returns": {"value": "float"}},
    },
    "links": {"serial": {"transport": "uart"}},
}


def mutated(**changes):
    """A deep copy of _BASE with `changes` applied by a callable."""
    data = copy.deepcopy(_BASE)
    for mutate in changes.values():
        mutate(data)
    return data


# ------------------------------------------------------------------ stability

def test_is_stable_across_runs(tmp_path):
    # Nothing in the hash may depend on iteration order or on a random seed.
    first = fingerprint(tmp_path, _BASE, "a.yaml")
    second = fingerprint(tmp_path, _BASE, "b.yaml")
    assert first == second


def test_is_stable_when_siblings_are_reordered(tmp_path):
    # The same contract written in a different order is the same contract; a
    # peer must not be locked out because someone tidied the YAML.
    reordered = {
        "system": dict(reversed(list(_BASE["system"].items()))),
        "links": _BASE["links"],
    }
    assert fingerprint(tmp_path, reordered) == fingerprint(tmp_path, _BASE)


def test_is_stable_across_yaml_and_json(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(_BASE))
    assert Fingerprint.hex(Tree.build(path)) == fingerprint(tmp_path, _BASE)


def test_is_sixteen_hex_digits(tmp_path):
    value = fingerprint(tmp_path, _BASE)
    assert len(value) == 16
    assert int(value, 16) == Fingerprint.compute(Tree.build(write(tmp_path, _BASE)))


# --------------------------------------------------------------- sensitivity

@pytest.mark.parametrize("label,mutate", [
    ("param type",     lambda d: d["system"]["spin"]["params"].update({"duty": "uint16"})),
    ("param name",     lambda d: d["system"]["spin"].__setitem__("params", {"level": "uint8"})),
    ("param added",    lambda d: d["system"]["spin"]["params"].update({"ramp": "float"})),
    ("param order",    lambda d: d["system"]["spin"].__setitem__(
                            "params", {"ramp": "float", "duty": "uint8"})),
    ("task name",      lambda d: d["system"].__setitem__("spin2", d["system"].pop("spin"))),
    ("tier",           lambda d: d["system"]["spin"].__setitem__("type", "stateful_task")),
    ("return type",    lambda d: d["system"]["read"].__setitem__("returns", {"value": "double"})),
    ("return added",   lambda d: d["system"]["read"].__setitem__(
                            "returns", {"value": "float", "ok": "bool"})),
    # Uids are assigned by the generator, so a uid change is reached by adding a
    # task: every later uid shifts, and the width itself grows past 256.
    ("uid",            lambda d: d["system"].__setitem__(
                            "aaa_first", {"type": "instant_task"})),
    ("uid width",      lambda d: d["system"].__setitem__(
                            "bank", {"type": "abstract_scope",
                                     "instances": [f"i{n}" for n in range(300)],
                                     "children": {"t": {"type": "instant_task"}}})),
    ("link checksum",  lambda d: d["links"]["serial"].update({"checksum": "crc32"})),
    ("link topology",  lambda d: d["links"]["serial"].update({"topology": "network"})),
    ("link reliable",  lambda d: d["links"]["serial"].update({"reliable": False})),
    ("link name",      lambda d: d["links"].__setitem__("bench", d["links"].pop("serial"))),
    ("link added",     lambda d: d["links"].update({"net": {"transport": "tcp"}})),
])
def test_changes_when_the_contract_changes(tmp_path, label, mutate):
    """Every one of these changes what a peer must understand to talk to us."""
    changed = copy.deepcopy(_BASE)
    mutate(changed)
    assert fingerprint(tmp_path, changed) != fingerprint(tmp_path, _BASE), label


def test_a_scope_rename_changes_it(tmp_path):
    # A task's dotted path is part of the contract: the generated client's call
    # site moves, so a peer built before the rename is out of date.
    nested = {"system": {"motor": {"type": "scope", "children": {
        "spin": {"type": "polled_task"}}}}}
    renamed = {"system": {"engine": {"type": "scope", "children": {
        "spin": {"type": "polled_task"}}}}}
    assert fingerprint(tmp_path, nested) != fingerprint(tmp_path, renamed)


# ------------------------------------------------------------------ canonical

def test_canonical_is_diffable(tmp_path):
    # The string exists so a mismatch can be diffed rather than guessed at, and
    # so the two language implementations have something exact to agree on.
    text = Fingerprint.canonical(Tree.build(write(tmp_path, _BASE)))
    assert text.startswith("etask-fingerprint-v1\n")
    assert "uid_bytes=1" in text
    assert "link serial point_to_point sequenced crc16" in text
    assert "task 1 spin polled_task" in text
    assert "  param duty uint8" in text
    assert "  return task_finished value float" in text
    assert text.endswith("\n")


def test_canonical_orders_tasks_by_uid_not_by_declaration(tmp_path):
    # Uids are handed out lowest-first in path order, so `early` takes 0 and
    # `late` takes 1 whichever way round the schema declares them.
    data = {"system": {
        "late": {"type": "polled_task"},
        "early": {"type": "polled_task"},
    }}
    text = Fingerprint.canonical(Tree.build(write(tmp_path, data)))
    assert text.index("task 0 early") < text.index("task 1 late")


def test_canonical_orders_links_by_name(tmp_path):
    data = {"system": {"a": {"type": "polled_task"}},
            "links": {"zeta": {"transport": "uart"}, "alpha": {"transport": "uart"}}}
    text = Fingerprint.canonical(Tree.build(write(tmp_path, data)))
    assert text.index("link alpha") < text.index("link zeta")


def test_schema_without_links_still_fingerprints(tmp_path):
    # An internal-only project has no handshake to perform, but the constant is
    # still emitted, so computing it must not depend on a link existing.
    value = fingerprint(tmp_path, {"system": {"a": {"type": "polled_task"}}})
    assert len(value) == 16
