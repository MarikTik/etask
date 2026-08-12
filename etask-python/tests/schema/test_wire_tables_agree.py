# tools/tests/etask.schema/test_wire_tables_agree.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""The three transcriptions of the wire contract must agree.

The status codes and value sizes exist in three places: the C++ header (the
source of truth, since it is what the firmware compiles), the schema generator's
table (which validates schemas and emits C++), and the Python client's enum
(which decodes replies). Nothing keeps them in step but these tests, so they
parse the header itself rather than comparing the two copies to each other.
"""

import re
from pathlib import Path

import pytest

from etask.schema.models.status_code import StatusCode as SchemaStatus
from etask.schema.models.type_map import TypeMap

_HEADER = Path(__file__).resolve().parents[3] / "etask" / "core" / "status_code.hpp"
_ENUMERATOR = re.compile(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*(0x[0-9A-Fa-f]+)\s*,", re.MULTILINE)


def header_codes() -> dict:
    """Every ``name = 0xNN`` in status_code.hpp."""
    text = _HEADER.read_text()
    body = text[text.index("enum status_code"):]
    return {name: int(value, 16) for name, value in _ENUMERATOR.findall(body)}


def test_the_header_is_where_we_think_it_is():
    assert _HEADER.exists(), f"status_code.hpp not found at {_HEADER}"
    assert len(header_codes()) > 20


def test_the_generator_table_matches_the_cpp_header():
    codes = header_codes()
    codes.pop("custom_error_start", None)  # a range marker, not a status
    missing = {name: value for name, value in codes.items()
               if SchemaStatus.resolve(name) != (name, value)}
    assert not missing, (
        f"etask.schema.models.status_code is out of step with status_code.hpp: {missing}"
    )


def test_the_python_client_enum_matches_the_cpp_header():
    etask_status = pytest.importorskip("etask.status_code", reason="etask-python not installed")
    codes = header_codes()
    mismatched = {}
    for name, value in codes.items():
        member = getattr(etask_status.StatusCode, name.upper(), None)
        if member is None or int(member) != value:
            mismatched[name] = (value, None if member is None else int(member))
    assert not mismatched, (
        f"etask.status_code is out of step with status_code.hpp: {mismatched}"
    )


def test_every_schema_type_has_the_same_size_on_both_sides():
    codec = pytest.importorskip("etask.codec", reason="etask-python not installed")
    mismatched = {
        name: (TypeMap.wire_size(name), codec.wire_size((name,)))
        for name in TypeMap.allowed()
        if TypeMap.wire_size(name) != codec.wire_size((name,))
    }
    assert not mismatched, f"TypeMap and etask.codec disagree on wire sizes: {mismatched}"


def test_neither_side_knows_a_type_the_other_does_not():
    codec = pytest.importorskip("etask.codec", reason="etask-python not installed")
    assert sorted(TypeMap.allowed()) == sorted(codec.known_types())
