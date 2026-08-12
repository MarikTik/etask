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


def test_meta_schema_is_valid(validator):
    assert validator is not None


def test_example_json_validates(validator):
    data = json.load(open(f"{_SCHEMA_DIR}/schema.json"))
    assert list(validator.iter_errors(data)) == []


def test_example_yaml_validates(validator):
    data = yaml.load(open(f"{_SCHEMA_DIR}/schema.yaml").read(), Loader=_SchemaLoader)
    assert list(validator.iter_errors(data)) == []


def test_meta_rejects_bad_type(validator):
    data = {"t": {"type": "widget", "params": {}}}
    assert list(validator.iter_errors(data)) != []


def test_meta_rejects_bad_identifier(validator):
    data = {"2bad": {"type": "task", "params": {}}}
    assert list(validator.iter_errors(data)) != []


def test_meta_rejects_unknown_param_type(validator):
    data = {"t": {"type": "task", "params": {"x": "int128"}}}
    assert list(validator.iter_errors(data)) != []


def test_meta_rejects_abstract_without_instances(validator):
    data = {"m": {"type": "abstract_scope", "children": {"on": {"type": "task", "params": {}}}}}
    assert list(validator.iter_errors(data)) != []


# -----------------------
# Status-keyed returns
# -----------------------

def test_meta_accepts_status_keyed_returns(validator):
    validator.validate({
        "fix": {
            "type": "task",
            "returns": {
                "finished": {"lat": "float"},
                "task_timeout": {"waited_ms": "uint32"},
                "aborted": {},
                "custom(0x71)": ["uint8"],
            },
        }
    })


def test_meta_still_accepts_a_single_shape(validator):
    validator.validate({"fix": {"type": "task", "returns": {"lat": "float"}}})
    validator.validate({"fix": {"type": "task", "returns": ["float", "uint8"]}})


def test_meta_rejects_a_manager_status_as_a_key(validator):
    # `ok` is the "task chose no status" sentinel; it never reaches the wire.
    with pytest.raises(jsonschema.ValidationError):
        validator.validate({"fix": {"type": "task", "returns": {"ok": {"lat": "float"}}}})


def test_meta_rejects_a_custom_code_outside_its_range(validator):
    with pytest.raises(jsonschema.ValidationError):
        validator.validate({"fix": {"type": "task", "returns": {"custom(0x30)": ["uint8"]}}})
