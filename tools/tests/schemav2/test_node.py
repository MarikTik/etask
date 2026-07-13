# tools/tests/schemav2/test_node.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import pytest

from schemav2.models.node import Node, Kind
from schemav2.models.param import Param
from schemav2.models.type_map import TypeMap


def test_kind_predicates():
    task = Node(name="t", kind=Kind.TASK)
    scope = Node(name="s", kind=Kind.SCOPE)
    abstract = Node(name="a", kind=Kind.ABSTRACT_SCOPE)
    root = Node(name="", kind=Kind.ROOT)
    assert task.is_task and not task.is_scope
    assert scope.is_scope and not scope.is_task
    assert abstract.is_abstract_scope
    assert root.is_root


def test_injected_scope_none_for_root_child():
    root = Node(name="", kind=Kind.ROOT)
    task = Node(name="t", kind=Kind.TASK, parent=root)
    assert task.injected_scope is None


def test_injected_scope_is_parent_scope():
    scope = Node(name="leg", kind=Kind.SCOPE)
    task = Node(name="calibrate", kind=Kind.TASK, parent=scope)
    assert task.injected_scope is scope


def test_param_cpp_type_and_wire_size():
    assert Param(type="uint8").cpp_type == "std::uint8_t"
    assert Param(type="uint8").wire_size == 1
    assert Param(type="float").cpp_type == "float"
    assert Param(type="string").wire_size is None


@pytest.mark.parametrize("schema_type", TypeMap.allowed())
def test_typemap_roundtrip(schema_type):
    assert TypeMap.is_valid(schema_type)
    assert isinstance(TypeMap.cpp_type(schema_type), str)


def test_typemap_rejects_unknown():
    assert not TypeMap.is_valid("int128")
