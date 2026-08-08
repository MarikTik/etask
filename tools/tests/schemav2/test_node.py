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


def test_injected_scope_of_root_child_is_the_root():
    # a root-level task receives the document root (the `system` scope) as its
    # context, so system-level tasks can reach the whole tree.
    root = Node(name="", kind=Kind.ROOT)
    task = Node(name="t", kind=Kind.TASK, parent=root)
    assert task.injected_scope is root


def test_injected_scope_is_parent_scope():
    scope = Node(name="leg", kind=Kind.SCOPE)
    task = Node(name="calibrate", kind=Kind.TASK, parent=scope)
    assert task.injected_scope is scope


def test_param_cpp_type_and_wire_size():
    assert Param(type="uint8").cpp_type == "std::uint8_t"
    assert Param(type="uint8").wire_size == 1
    assert Param(type="float").cpp_type == "float"
    # every allowed type has a fixed wire size (the flat codec needs it)
    assert all(TypeMap.wire_size(t) is not None for t in TypeMap.allowed())


@pytest.mark.parametrize("schema_type", TypeMap.allowed())
def test_typemap_roundtrip(schema_type):
    assert TypeMap.is_valid(schema_type)
    assert isinstance(TypeMap.cpp_type(schema_type), str)


def test_typemap_rejects_unknown():
    assert not TypeMap.is_valid("int128")


def test_string_is_gated_out_no_fixed_wire_size():
    # `string` has no fixed wire size in the flat codec (eser static_asserts on
    # const char*), so it must NOT be an accepted schema type - accepting it would
    # only generate C++ that fails to compile. See the audit report.
    assert not TypeMap.is_valid("string")
    assert "string" not in TypeMap.allowed()


def test_doc_brief_prefers_brief_then_description():
    both = Node(name="t", kind=Kind.TASK, brief="short", description="long detail")
    only_desc = Node(name="t", kind=Kind.TASK, description="just a description")
    bare = Node(name="t", kind=Kind.TASK)
    assert both.doc_brief == "short"
    assert only_desc.doc_brief == "just a description"
    assert bare.doc_brief is None


def test_doc_detail_only_when_brief_and_description_both_present():
    both = Node(name="t", kind=Kind.TASK, brief="short", description="long detail")
    only_desc = Node(name="t", kind=Kind.TASK, description="just a description")
    only_brief = Node(name="t", kind=Kind.TASK, brief="short")
    assert both.doc_detail == "long detail"
    assert only_desc.doc_detail is None   # promoted to brief, not repeated
    assert only_brief.doc_detail is None


def test_doc_text_is_stripped():
    n = Node(name="t", kind=Kind.TASK, brief="s", description="line one\nline two\n")
    assert n.doc_detail == "line one\nline two"
