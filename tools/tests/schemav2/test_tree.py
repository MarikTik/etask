# tools/tests/schemav2/test_tree.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import json

import pytest

from schemav2.tree import Tree
from schemav2.models.node import Kind
from schemav2.errors import (
    DuplicateUidError,
    InvalidIdentifierError,
    UnknownTypeError,
    SchemaShapeError,
    AbstractInstanceError,
)


# -----------------------
# Helpers
# -----------------------

def write(tmp_path, data, suffix=".json"):
    path = tmp_path / f"schema{suffix}"
    path.write_text(json.dumps(data))
    return path


def build(tmp_path, data):
    return Tree.build(write(tmp_path, data))


def tasks(node):
    found = [node] if node.is_task else []
    for child in node.children.values():
        found.extend(tasks(child))
    return found


def find(node, dotted):
    current = node
    for part in dotted.split("."):
        current = current.children[part]
    return current


# -----------------------
# Parsing / structure
# -----------------------

def test_scope_and_task_kinds(tmp_path):
    root = build(tmp_path, {
        "arm": {"type": "scope", "children": {
            "grab": {"type": "task", "params": {"force": "uint8"}}
        }}
    })
    arm = find(root, "arm")
    grab = find(root, "arm.grab")
    assert arm.kind is Kind.SCOPE
    assert grab.kind is Kind.TASK
    assert [(p.name, p.type) for p in grab.params] == [("force", "uint8")]


def test_param_order_preserved(tmp_path):
    root = build(tmp_path, {
        "t": {"type": "task", "params": {"a": "int", "b": "float", "c": "uint8"}}
    })
    assert [p.name for p in find(root, "t").params] == ["a", "b", "c"]


def test_returns_positional_list(tmp_path):
    root = build(tmp_path, {
        "t": {"type": "task", "returns": ["float", "float", "int"]}
    })
    shapes = find(root, "t").returns
    # A plain `returns:` is one shape, carried by an ordinary completion.
    assert [(s.key, s.name, s.code) for s in shapes] == [("finished", "task_finished", 0x20)]
    assert [(p.name, p.type) for p in shapes[0].values] == [
        (None, "float"), (None, "float"), (None, "int")
    ]


def test_injected_scope_is_parent(tmp_path):
    root = build(tmp_path, {
        "leg": {"type": "scope", "children": {
            "calibrate": {"type": "task", "params": {}}
        }},
        "reboot": {"type": "task", "params": {}}
    })
    assert find(root, "leg.calibrate").injected_scope is find(root, "leg")
    # root-level task receives the document root (the system scope)
    assert find(root, "reboot").injected_scope is root


# -----------------------
# Abstract expansion
# -----------------------

def test_abstract_scope_expands_per_instance(tmp_path):
    root = build(tmp_path, {
        "motor": {"type": "abstract_scope", "instances": ["m1", "m2", "m3"], "children": {
            "on": {"type": "task", "params": {"intensity": "uint8"}}
        }}
    })
    # abstract node replaced by concrete instances
    assert set(root.children) == {"m1", "m2", "m3"}
    assert all(root.children[n].kind is Kind.SCOPE for n in ("m1", "m2", "m3"))
    assert len(tasks(root)) == 3


def test_nested_abstract_scopes_expand(tmp_path):
    root = build(tmp_path, {
        "muscle": {"type": "abstract_scope", "instances": ["hip", "knee"], "children": {
            "motor": {"type": "abstract_scope", "instances": ["m1", "m2"], "children": {
                "on": {"type": "task", "params": {}},
                "off": {"type": "task", "params": {}}
            }}
        }}
    })
    # 2 muscles * 2 motors * 2 tasks
    assert len(tasks(root)) == 8
    assert find(root, "hip.m1.on").kind is Kind.TASK


def test_instance_name_collision_with_sibling(tmp_path):
    with pytest.raises(AbstractInstanceError):
        build(tmp_path, {
            "grp": {"type": "scope", "children": {
                "m1": {"type": "task", "params": {}},
                "motor": {"type": "abstract_scope", "instances": ["m1"], "children": {
                    "on": {"type": "task", "params": {}}
                }}
            }}
        })


# -----------------------
# UID assignment
# -----------------------

def test_generated_uids_are_distinct(tmp_path):
    root = build(tmp_path, {
        "motor": {"type": "abstract_scope", "instances": [f"m{i}" for i in range(50)], "children": {
            "on": {"type": "task", "params": {}},
            "off": {"type": "task", "params": {}}
        }}
    })
    uids = [t.uid for t in tasks(root)]
    assert len(uids) == 100
    assert len(set(uids)) == 100


def test_generated_uids_are_deterministic(tmp_path):
    data = {"a": {"type": "scope", "children": {"t": {"type": "task", "params": {}}}}}
    first = build(tmp_path, data)
    second = build(tmp_path, data)
    assert find(first, "a.t").uid == find(second, "a.t").uid


def test_explicit_uid_preserved(tmp_path):
    root = build(tmp_path, {"t": {"type": "task", "uid": 42, "params": {}}})
    assert find(root, "t").uid == 42


def test_uid_width_grows_with_task_count(tmp_path):
    small = build(tmp_path, {
        "m": {"type": "abstract_scope", "instances": [f"m{i}" for i in range(5)], "children": {
            "t": {"type": "task", "params": {}}
        }}
    })
    assert small.uid_bytes == 1

    big = build(tmp_path, {
        "m": {"type": "abstract_scope", "instances": [f"m{i}" for i in range(300)], "children": {
            "t": {"type": "task", "params": {}}
        }}
    })
    assert big.uid_bytes == 2


def test_uid_width_grows_with_explicit_uid(tmp_path):
    root = build(tmp_path, {
        "a": {"type": "task", "uid": 500, "params": {}},
        "b": {"type": "task", "params": {}}
    })
    assert root.uid_bytes == 2


def test_duplicate_explicit_uid_raises(tmp_path):
    with pytest.raises(DuplicateUidError):
        build(tmp_path, {
            "a": {"type": "task", "uid": 1, "params": {}},
            "b": {"type": "task", "uid": 1, "params": {}}
        })


def test_generated_uid_avoids_explicit(tmp_path):
    # Many generated uids alongside a fixed explicit one; explicit must be unique.
    root = build(tmp_path, {
        "fixed": {"type": "task", "uid": 7, "params": {}},
        "motor": {"type": "abstract_scope", "instances": [f"m{i}" for i in range(40)], "children": {
            "on": {"type": "task", "params": {}}
        }}
    })
    uids = [t.uid for t in tasks(root)]
    assert len(uids) == len(set(uids))
    assert find(root, "fixed").uid == 7


# -----------------------
# Validation boundaries
# -----------------------

def test_bad_identifier_raises(tmp_path):
    with pytest.raises(InvalidIdentifierError):
        build(tmp_path, {"2bad": {"type": "task", "params": {}}})


def test_reserved_keyword_identifier_raises(tmp_path):
    with pytest.raises(InvalidIdentifierError):
        build(tmp_path, {"class": {"type": "task", "params": {}}})


def test_unknown_type_raises(tmp_path):
    with pytest.raises(UnknownTypeError):
        build(tmp_path, {"t": {"type": "task", "params": {"x": "int128"}}})


def test_string_type_rejected_in_params_and_returns(tmp_path):
    # `string` is not a valid wire type (no fixed size in the flat codec); it is
    # gated out so it can't silently generate uncompilable C++.
    with pytest.raises(UnknownTypeError):
        build(tmp_path, {"t": {"type": "task", "params": {"name": "string"}}})
    with pytest.raises(UnknownTypeError):
        build(tmp_path, {"t": {"type": "task", "returns": {"label": "string"}}})


def test_missing_type_raises(tmp_path):
    with pytest.raises(SchemaShapeError):
        build(tmp_path, {"t": {"params": {}}})


def test_task_with_children_raises(tmp_path):
    with pytest.raises(SchemaShapeError):
        build(tmp_path, {
            "t": {"type": "task", "params": {}, "children": {
                "x": {"type": "task", "params": {}}
            }}
        })


def test_scope_with_params_raises(tmp_path):
    with pytest.raises(SchemaShapeError):
        build(tmp_path, {"s": {"type": "scope", "params": {"x": "int"}, "children": {}}})


def test_explicit_uid_in_abstract_scope_raises(tmp_path):
    with pytest.raises(SchemaShapeError):
        build(tmp_path, {
            "motor": {"type": "abstract_scope", "instances": ["m1"], "children": {
                "on": {"type": "task", "uid": 3, "params": {}}
            }}
        })


def test_empty_instances_raises(tmp_path):
    with pytest.raises(AbstractInstanceError):
        build(tmp_path, {
            "motor": {"type": "abstract_scope", "instances": [], "children": {
                "on": {"type": "task", "params": {}}
            }}
        })


def test_duplicate_instance_names_raises(tmp_path):
    with pytest.raises(AbstractInstanceError):
        build(tmp_path, {
            "motor": {"type": "abstract_scope", "instances": ["m1", "m1"], "children": {
                "on": {"type": "task", "params": {}}
            }}
        })


def test_top_level_must_be_mapping(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(["not", "a", "map"]))
    with pytest.raises(SchemaShapeError):
        Tree.build(path)


# -----------------------
# YAML vs JSON equivalence + real example
# -----------------------

def test_yaml_json_examples_equivalent():
    root = "/home/mark/Desktop/projects/elib/etask/schema"

    def sig(node):
        return (node.name, node.kind.value, node.uid,
                tuple((p.name, p.type) for p in (node.params or [])),
                tuple((s.name, s.code, tuple((p.name, p.type) for p in s.values))
                      for s in (node.returns or [])),
                tuple(sig(c) for c in node.children.values()))

    y = Tree.build(f"{root}/schema.yaml")
    j = Tree.build(f"{root}/schema.json")
    assert sig(y) == sig(j)
    assert y.uid_bytes == 1
    # 4 legs * (1 calibrate + 2 muscles * 2 motors * 2 tasks) + 1 reboot
    assert len(tasks(y)) == 37
    assert len({t.uid for t in tasks(y)}) == 37


def test_on_off_not_coerced_to_bool_in_yaml(tmp_path):
    # The YAML-1.2 loader must keep on/off/yes/no as strings, not booleans.
    path = tmp_path / "schema.yaml"
    path.write_text(
        "motor:\n"
        "  type: scope\n"
        "  children:\n"
        "    on:\n"
        "      type: task\n"
        "      params: {}\n"
        "    off:\n"
        "      type: task\n"
        "      params: {}\n"
    )
    root = Tree.build(path)
    assert set(root.children["motor"].children) == {"on", "off"}


def test_concurrency_parsed_onto_task():
    import tempfile, pathlib
    y = "mover:\n  type: task\n  concurrency: 4\nsolo:\n  type: task\n"
    p = pathlib.Path(tempfile.mktemp(suffix=".yaml")); p.write_text(y)
    root = Tree.build(p)
    assert root.children["mover"].concurrency == 4
    assert root.children["solo"].concurrency is None   # default


def test_concurrency_must_be_positive_int():
    import tempfile, pathlib, pytest
    from schemav2.errors.schema_shape_error import SchemaShapeError
    for bad in ("0", "-1", "true", "1.5"):
        p = pathlib.Path(tempfile.mktemp(suffix=".yaml"))
        p.write_text(f"t:\n  type: task\n  concurrency: {bad}\n")
        with pytest.raises(SchemaShapeError):
            Tree.build(p)


def test_concurrency_rejected_on_scope():
    import tempfile, pathlib, pytest
    from schemav2.errors.schema_shape_error import SchemaShapeError
    p = pathlib.Path(tempfile.mktemp(suffix=".yaml"))
    p.write_text("s:\n  type: scope\n  concurrency: 2\n  children: {}\n")
    with pytest.raises(SchemaShapeError):
        Tree.build(p)


def test_concurrency_copied_to_abstract_instances():
    import tempfile, pathlib
    y = ("joint:\n  type: abstract_scope\n  instances: [base, elbow]\n  children:\n"
         "    move:\n      type: task\n      concurrency: 2\n")
    p = pathlib.Path(tempfile.mktemp(suffix=".yaml")); p.write_text(y)
    root = Tree.build(p)
    assert root.children["base"].children["move"].concurrency == 2
    assert root.children["elbow"].children["move"].concurrency == 2
