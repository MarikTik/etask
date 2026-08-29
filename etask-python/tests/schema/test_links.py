# tools/tests/etask.schema/test_links.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import json

import pytest

from etask.schema.tree import Tree
from etask.schema.models.link import Checksum, Topology, Transport
from etask.schema.errors import InvalidIdentifierError, SchemaShapeError


# -----------------------
# Helpers
# -----------------------

def write(tmp_path, data, suffix=".json"):
    path = tmp_path / f"schema{suffix}"
    path.write_text(json.dumps(data))
    return path


def build(tmp_path, links, system=None):
    """`links` is the `links:` section; the system beside it is incidental here."""
    data = {"system": system or {"led": {"type": "polled_task"}}}
    if links is not None:
        data["links"] = links
    return Tree.build(write(tmp_path, data))


def one(tmp_path, body, name="serial"):
    """Builds a single link and hands it back."""
    return build(tmp_path, {name: body}).links.get(name)


# -----------------------
# Presence and shape
# -----------------------

def test_links_is_optional(tmp_path):
    # No `links:` at all: internal channel only, which most systems are.
    root = build(tmp_path, None)
    assert root.links is not None
    assert not root.links
    assert len(root.links) == 0
    assert root.links.names == []


def test_links_must_be_a_mapping(tmp_path):
    path = write(tmp_path, {"system": {"led": {"type": "polled_task"}}, "links": ["uart"]})
    with pytest.raises(SchemaShapeError, match="links"):
        Tree.build(path)


def test_a_link_body_must_be_a_mapping(tmp_path):
    with pytest.raises(SchemaShapeError, match="serial"):
        one(tmp_path, "uart")


def test_transport_is_required(tmp_path):
    with pytest.raises(SchemaShapeError, match="transport"):
        one(tmp_path, {"topology": "network"})


def test_multiple_links_keep_declaration_order(tmp_path):
    root = build(tmp_path, {
        "serial": {"transport": "uart"},
        "net": {"transport": "tcp"},
        "radio": {"transport": "wifi"},
    })
    assert root.links.names == ["serial", "net", "radio"]
    assert [link.transport for link in root.links] == [
        Transport.UART, Transport.TCP, Transport.WIFI
    ]
    assert len(root.links) == 3
    assert root.links


def test_an_unknown_link_key_is_rejected(tmp_path):
    # Which port the transport uses is a wiring question, not a schema one.
    with pytest.raises(SchemaShapeError, match="baud"):
        one(tmp_path, {"transport": "uart", "baud": 115200})


# -----------------------
# Defaults, per transport
# -----------------------

@pytest.mark.parametrize("transport,topology,checksum,reliable", [
    ("uart", Topology.POINT_TO_POINT, Checksum.CRC16, True),
    ("i2c", Topology.POINT_TO_POINT, Checksum.CRC16, True),
    ("wifi", Topology.NETWORK, Checksum.CRC16, True),
    ("custom", Topology.POINT_TO_POINT, Checksum.CRC16, True),
    ("tcp", Topology.NETWORK, Checksum.NONE, False),
])
def test_defaults_follow_the_transport(tmp_path, transport, topology, checksum, reliable):
    link = one(tmp_path, {"transport": transport})
    assert link.topology is topology
    assert link.checksum is checksum
    assert link.reliable is reliable


def test_reliable_defaults_carry_a_retry_policy(tmp_path):
    link = one(tmp_path, {"transport": "uart"})
    assert (link.retries, link.buffer_depth) == (3, 4)


def test_a_non_reliable_link_has_no_retry_policy(tmp_path):
    link = one(tmp_path, {"transport": "tcp"})
    assert link.retries is None
    assert link.buffer_depth is None


def test_declared_values_beat_the_defaults(tmp_path):
    link = one(tmp_path, {
        "transport": "uart",
        "topology": "network",
        "checksum": "crc32_reflected",
        "reliable": True,
        "retries": 7,
        "buffer_depth": 2,
    })
    assert link.topology is Topology.NETWORK
    assert link.checksum is Checksum.CRC32_REFLECTED
    assert (link.retries, link.buffer_depth) == (7, 2)


def test_reliable_may_be_turned_off_on_a_raw_link(tmp_path):
    link = one(tmp_path, {"transport": "uart", "reliable": False})
    assert link.reliable is False
    assert link.retries is None


# -----------------------
# Enforcement 1: tcp + a checksum
# -----------------------

def test_tcp_rejects_a_checksum(tmp_path):
    with pytest.raises(SchemaShapeError, match="already checksums"):
        one(tmp_path, {"transport": "tcp", "checksum": "crc16"})


def test_tcp_accepts_an_explicit_none_checksum(tmp_path):
    # Stating the default is not an error; it is only paying twice that is.
    link = one(tmp_path, {"transport": "tcp", "checksum": "none"})
    assert link.checksum is Checksum.NONE


# -----------------------
# Enforcement 2: tcp + reliable
# -----------------------

def test_tcp_rejects_reliable_true(tmp_path):
    with pytest.raises(SchemaShapeError, match="already delivers"):
        one(tmp_path, {"transport": "tcp", "reliable": True})


def test_tcp_accepts_an_explicit_reliable_false(tmp_path):
    link = one(tmp_path, {"transport": "tcp", "reliable": False})
    assert link.reliable is False


# -----------------------
# Enforcement 3: retry policy on a non-reliable link
# -----------------------

@pytest.mark.parametrize("key", ["retries", "buffer_depth"])
def test_retry_policy_rejected_when_not_reliable(tmp_path, key):
    with pytest.raises(SchemaShapeError, match=key):
        one(tmp_path, {"transport": "uart", "reliable": False, key: 2})


def test_retry_policy_rejected_on_tcp(tmp_path):
    # tcp is never reliable, so the keys are meaningless there by construction.
    with pytest.raises(SchemaShapeError, match="retries"):
        one(tmp_path, {"transport": "tcp", "retries": 2})


@pytest.mark.parametrize("value", [0, -1, "three", 1.5, True])
def test_retry_counts_must_be_positive_integers(tmp_path, value):
    with pytest.raises(SchemaShapeError, match="retries"):
        one(tmp_path, {"transport": "uart", "retries": value})


def test_reliable_must_be_a_boolean(tmp_path):
    with pytest.raises(SchemaShapeError, match="reliable"):
        one(tmp_path, {"transport": "uart", "reliable": "yes"})


# -----------------------
# Enforcement 4: reliable implies sequenced
# -----------------------

def test_reliable_implies_sequenced(tmp_path):
    # `sequenced` is derived, never declared: reliable_channel static_asserts on
    # a sequence number, so the user has no freedom to withhold it.
    assert one(tmp_path, {"transport": "uart"}).sequenced is True


def test_a_non_reliable_link_is_not_sequenced(tmp_path):
    assert one(tmp_path, {"transport": "tcp"}).sequenced is False
    assert one(tmp_path, {"transport": "uart", "reliable": False}).sequenced is False


def test_sequenced_is_not_a_schema_key(tmp_path):
    with pytest.raises(SchemaShapeError, match="sequenced"):
        one(tmp_path, {"transport": "uart", "sequenced": True})


# -----------------------
# Enforcement 5: link names
# -----------------------

def test_a_link_name_must_be_an_identifier(tmp_path):
    with pytest.raises(InvalidIdentifierError, match="2wire"):
        one(tmp_path, {"transport": "uart"}, name="2wire")


def test_a_link_name_may_not_be_a_cpp_keyword(tmp_path):
    # The name becomes a namespace, so `class` would not compile.
    with pytest.raises(InvalidIdentifierError, match="class"):
        one(tmp_path, {"transport": "uart"}, name="class")


def test_link_names_are_distinct(tmp_path):
    # A YAML/JSON mapping cannot repeat a key, so distinctness is structural -
    # what matters is that a second link never quietly replaces the first.
    root = build(tmp_path, {"a": {"transport": "uart"}, "b": {"transport": "uart"}})
    assert root.links.names == ["a", "b"]
    assert root.links.get("a") is not root.links.get("b")


def test_an_unknown_link_is_none(tmp_path):
    assert build(tmp_path, {"serial": {"transport": "uart"}}).links.get("nope") is None


# -----------------------
# Enforcement 6: unknown values
# -----------------------

def test_an_unknown_transport_lists_the_valid_set(tmp_path):
    with pytest.raises(SchemaShapeError, match="uart, wifi, i2c, tcp, custom"):
        one(tmp_path, {"transport": "carrier_pigeon"})


def test_an_unknown_topology_is_rejected(tmp_path):
    with pytest.raises(SchemaShapeError, match="point_to_point"):
        one(tmp_path, {"transport": "uart", "topology": "mesh"})


def test_an_unknown_checksum_is_rejected(tmp_path):
    with pytest.raises(SchemaShapeError, match="crc16"):
        one(tmp_path, {"transport": "uart", "checksum": "md5"})


@pytest.mark.parametrize("name", [
    "none", "sum8", "sum16", "sum32",
    "crc8", "crc16", "crc32", "crc64",
    "crc8_reflected", "crc16_reflected", "crc32_reflected",
    "fletcher16", "fletcher32", "adler32", "internet16",
])
def test_every_checksum_name_matches_an_ecomm_policy(tmp_path, name):
    # The value is the C++ struct name verbatim, so the emitter can spell
    # `ecomm::protocol::<value>` without a second table to keep in step.
    link = one(tmp_path, {"transport": "uart", "checksum": name})
    assert link.checksum.value == name
