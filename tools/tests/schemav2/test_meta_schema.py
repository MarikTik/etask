# tools/tests/schemav2/test_meta_schema.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import json

import jsonschema
import pytest
import yaml

from schemav2.tree import _SchemaLoader

_SCHEMA_DIR = "/home/mark/Desktop/projects/elib/etask/schema"
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
