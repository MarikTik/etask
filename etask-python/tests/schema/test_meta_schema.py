# tools/tests/etask.schema/test_meta_schema.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from etask.schema.tree import _SchemaLoader

# Repo-relative: tests must not depend on where the checkout lives.
_SCHEMA_DIR = str(Path(__file__).resolve().parents[3] / "schema")
_META = f"{_SCHEMA_DIR}/meta/etask.schema.json"


@pytest.fixture(scope="module")
def validator():
    meta = json.load(open(_META))
    jsonschema.Draft202012Validator.check_schema(meta)
    return jsonschema.Draft202012Validator(meta)


def system(nodes: dict, **sections) -> dict:
    """Wraps a node mapping in the schema's required `system:` section.

    Every node-level case below is about a node, not about the top-level shape,
    so they say what they mean and let this supply the framing.
    """
    return {"system": nodes, **sections}


def test_meta_schema_is_valid(validator):
    assert validator is not None


def test_example_json_validates(validator):
    data = json.load(open(f"{_SCHEMA_DIR}/schema.json"))
    assert list(validator.iter_errors(data)) == []


def test_example_yaml_validates(validator):
    data = yaml.load(open(f"{_SCHEMA_DIR}/schema.yaml").read(), Loader=_SchemaLoader)
    assert list(validator.iter_errors(data)) == []


def test_meta_rejects_bad_type(validator):
    data = system({"t": {"type": "widget", "params": {}}})
    assert list(validator.iter_errors(data)) != []


def test_meta_rejects_bad_identifier(validator):
    data = system({"2bad": {"type": "polled_task", "params": {}}})
    assert list(validator.iter_errors(data)) != []


def test_meta_rejects_unknown_param_type(validator):
    data = system({"t": {"type": "polled_task", "params": {"x": "int128"}}})
    assert list(validator.iter_errors(data)) != []


def test_meta_rejects_abstract_without_instances(validator):
    data = system({"m": {"type": "abstract_scope", "children": {"on": {"type": "polled_task", "params": {}}}}})
    assert list(validator.iter_errors(data)) != []


# -----------------------
# Status-keyed returns
# -----------------------

def test_meta_accepts_status_keyed_returns(validator):
    validator.validate(system({
        "fix": {
            "type": "polled_task",
            "returns": {
                "finished": {"lat": "float"},
                "task_timeout": {"waited_ms": "uint32"},
                "aborted": {},
                "custom(0x71)": ["uint8"],
            },
        }
    }))


def test_meta_still_accepts_a_single_shape(validator):
    validator.validate(system({"fix": {"type": "polled_task", "returns": {"lat": "float"}}}))
    validator.validate(system({"fix": {"type": "polled_task", "returns": ["float", "uint8"]}}))


def test_meta_rejects_a_manager_status_as_a_key(validator):
    # `ok` is the "task chose no status" sentinel; it never reaches the wire.
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(system({"fix": {"type": "polled_task", "returns": {"ok": {"lat": "float"}}}}))


def test_meta_rejects_a_custom_code_outside_its_range(validator):
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(system({"fix": {"type": "polled_task", "returns": {"custom(0x30)": ["uint8"]}}}))


# -----------------------
# Top-level sections
# -----------------------

def test_meta_requires_the_system_section(validator):
    # A flat node mapping is the pre-sections shape; it must no longer validate.
    assert list(validator.iter_errors({"led": {"type": "polled_task"}})) != []


def test_meta_rejects_a_node_beside_the_sections(validator):
    # Scopes and tasks live under `system:`, never at the top level.
    data = system({"led": {"type": "polled_task"}})
    data["legs"] = {"type": "scope", "children": {}}
    assert list(validator.iter_errors(data)) != []


def test_meta_accepts_an_omitted_budget(validator):
    # `budget:` is optional - without it every tier assumes its worst case.
    validator.validate(system({"led": {"type": "polled_task"}}))


def test_meta_accepts_a_budget(validator):
    validator.validate(system({"led": {"type": "polled_task"}}, budget={"polled": 4}))
    validator.validate(
        system({"led": {"type": "polled_task"}}, budget={"polled": 4, "stateful": 2})
    )


def test_meta_rejects_an_unknown_budget_tier(validator):
    # An instant_task occupies no storage, so it takes no budget.
    data = system({"led": {"type": "polled_task"}}, budget={"instant": 4})
    assert list(validator.iter_errors(data)) != []


def test_meta_rejects_a_non_positive_budget(validator):
    # A tier that may hold no live task cannot run one.
    assert list(validator.iter_errors(
        system({"led": {"type": "polled_task"}}, budget={"polled": 0}))) != []


def test_meta_rejects_a_fractional_budget(validator):
    assert list(validator.iter_errors(
        system({"led": {"type": "polled_task"}}, budget={"polled": 1.5}))) != []
