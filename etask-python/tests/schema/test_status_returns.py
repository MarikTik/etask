# tools/tests/etask.schema/test_status_returns.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import json

import pytest

from etask.schema.tree import Tree
from etask.schema.errors import SchemaShapeError, UnknownStatusError


def build(tmp_path, data):
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(data))
    return Tree.build(path)


def task(**extra):
    body = {"type": "polled_task"}
    body.update(extra)
    return body


def shapes_of(root, name="t"):
    return root.children[name].returns


# -----------------------
# The single-shape form is unchanged
# -----------------------

def test_plain_returns_is_one_finished_shape(tmp_path):
    root = build(tmp_path, {"t": task(returns={"ax": "float", "ay": "float"})})
    shapes = shapes_of(root)
    assert len(shapes) == 1
    assert (shapes[0].key, shapes[0].name, shapes[0].code) == ("finished", "task_finished", 0x20)
    assert [(p.name, p.type) for p in shapes[0].values] == [("ax", "float"), ("ay", "float")]
    assert shapes[0].is_default


def test_no_returns_declares_no_shape(tmp_path):
    root = build(tmp_path, {"t": task(params={})})
    assert shapes_of(root) == []


def test_empty_returns_declares_no_shape(tmp_path):
    root = build(tmp_path, {"t": task(returns={})})
    assert shapes_of(root) == []


def test_a_value_named_like_a_status_is_still_a_value(tmp_path):
    # Detection is by the *value* (a type string vs a nested shape), never by the
    # key, so a result field may be called `finished` without becoming a status.
    root = build(tmp_path, {"t": task(returns={"finished": "bool", "aborted": "uint8"})})
    shapes = shapes_of(root)
    assert len(shapes) == 1 and shapes[0].name == "task_finished"
    assert [(p.name, p.type) for p in shapes[0].values] == [
        ("finished", "bool"), ("aborted", "uint8")
    ]


# -----------------------
# Status-keyed shapes
# -----------------------

def test_status_keyed_shapes_resolve_to_codes(tmp_path):
    root = build(tmp_path, {"t": task(returns={
        "finished": {"ax": "float"},
        "task_io_error": {"sensor": "uint8"},
    })})
    shapes = shapes_of(root)
    assert [(s.key, s.name, s.code) for s in shapes] == [
        ("finished", "task_finished", 0x20),
        ("task_io_error", "task_io_error", 0x23),
    ]


def test_shapes_are_ordered_by_code_not_by_schema_order(tmp_path):
    root = build(tmp_path, {"t": task(returns={
        "task_busy": {"retry_ms": "uint16"},
        "finished": {"ax": "float"},
        "aborted": {"partial": "uint16"},
    })})
    assert [s.code for s in shapes_of(root)] == [0x20, 0x21, 0x26]


def test_positional_values_inside_a_status_shape(tmp_path):
    root = build(tmp_path, {"t": task(returns={"finished": ["uint8", "float"]})})
    values = shapes_of(root)[0].values
    assert [(p.name, p.type) for p in values] == [(None, "uint8"), (None, "float")]


def test_a_shape_may_carry_no_values(tmp_path):
    root = build(tmp_path, {"t": task(returns={
        "finished": {"ax": "float"},
        "aborted": {},
    })})
    shapes = shapes_of(root)
    assert shapes[1].name == "task_aborted"
    assert shapes[1].values == []


def test_custom_status_is_accepted(tmp_path):
    root = build(tmp_path, {"t": task(returns={
        "finished": {"ax": "float"},
        "custom(0x71)": {"detail": "uint8"},
    })})
    custom = shapes_of(root)[1]
    assert (custom.name, custom.code) == ("custom(0x71)", 0x71)
    assert "static_cast<etask::core::status_code>(0x71)" == custom.cpp_enumerator


def test_wire_size_is_the_sum_of_its_values(tmp_path):
    root = build(tmp_path, {"t": task(returns={"finished": {"a": "float", "b": "uint16"}})})
    assert shapes_of(root)[0].wire_size == 6


def test_finished_shape_is_reachable_by_name(tmp_path):
    root = build(tmp_path, {"t": task(returns={
        "task_timeout": {"waited_ms": "uint32"},
        "finished": {"ax": "float"},
    })})
    finished = root.children["t"].finished_shape
    assert finished is not None and finished.code == 0x20
    assert [p.name for p in finished.values] == ["ax"]


def test_a_task_may_declare_only_a_non_finished_shape(tmp_path):
    # Unusual but coherent: the task reports data only when it times out.
    root = build(tmp_path, {"t": task(returns={"task_timeout": {"waited_ms": "uint32"}})})
    assert root.children["t"].finished_shape is None
    assert shapes_of(root)[0].code == 0x22


# -----------------------
# Rejections
# -----------------------

def test_mixing_the_two_forms_is_rejected(tmp_path):
    with pytest.raises(SchemaShapeError, match="never both"):
        build(tmp_path, {"t": task(returns={
            "finished": {"ax": "float"},
            "stray": "uint8",
        })})


def test_manager_status_cannot_key_a_shape(tmp_path):
    # `ok` is the sentinel meaning "the task chose no status" - it never reaches
    # the wire on a completion, so a shape for it could never arrive.
    with pytest.raises(UnknownStatusError, match="manager/API status"):
        build(tmp_path, {"t": task(returns={"ok": {"ax": "float"}})})


def test_other_manager_statuses_are_rejected_too(tmp_path):
    with pytest.raises(UnknownStatusError, match="manager/API status"):
        build(tmp_path, {"t": task(returns={"task_unknown": {"ax": "float"}})})


def test_result_too_large_is_reserved(tmp_path):
    with pytest.raises(UnknownStatusError, match="reserved by the framework"):
        build(tmp_path, {"t": task(returns={"result_too_large": {"ax": "float"}})})


def test_unknown_status_name_is_rejected(tmp_path):
    with pytest.raises(UnknownStatusError, match="not a known status_code"):
        build(tmp_path, {"t": task(returns={"task_exploded": {"ax": "float"}})})


def test_custom_code_outside_the_custom_range_is_rejected(tmp_path):
    with pytest.raises(UnknownStatusError):
        build(tmp_path, {"t": task(returns={"custom(0x30)": {"ax": "float"}})})


def test_the_same_code_twice_is_rejected(tmp_path):
    with pytest.raises(SchemaShapeError, match="same status code"):
        build(tmp_path, {"t": task(returns={
            "finished": {"ax": "float"},
            "task_finished": {"ay": "float"},
        })})


def test_a_shape_body_must_be_a_mapping_or_list(tmp_path):
    with pytest.raises(SchemaShapeError):
        build(tmp_path, {"t": task(returns={"finished": {"ax": "float"}, "aborted": 7})})
