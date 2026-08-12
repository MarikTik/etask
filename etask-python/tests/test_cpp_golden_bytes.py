# etask-python/tests/test_cpp_golden_bytes.py
# SPDX-License-Identifier: MIT
"""Frozen packets produced by the real C++ runtime, decoded here.

Two transcriptions of a wire format agreeing with *each other* proves nothing if
both drifted from the firmware. These byte strings were emitted by
``etask::core::channels::external_channel::complete`` compiled against this
repo's headers (32-byte packet, ``topology::network``, ``uint16_t`` uid), by a
harness that packed a task's ``outcome`` and dumped the sealed packet as hex::

    struct gps_fix : ec::task<task_uid> {
        ec::outcome on_complete(ec::completion_reason) override {
            return {12.5f, -3.25f, std::uint8_t{9}};
        }
    };
    struct gps_timeout : ec::task<task_uid> {
        ec::outcome on_complete(ec::completion_reason) override {
            return ec::outcome{std::uint32_t{5000}}
                .with_status(ec::status_code::task_timeout);
        }
    };

If a change to the C++ payload layout makes these fail, the fix is to re-emit
them from the new firmware - not to adjust the expectations by hand.
"""

import pytest
from ecomm.channels._decode import decode_validated_and_addressed
from ecomm.protocol.schema import PacketSchema
from ecomm.protocol.topology import Topology

from etask import codec
from etask.protocol import parse_reply
from etask.status_code import StatusCode

UID_BYTES = 2

#: A natural completion: no with_status, so the manager's task_finished stands.
FINISHED = bytes.fromhex("0001011d002000004841000050c0090000000000000000000000000000000000")

#: The same task choosing its own status, with a different result shape.
TIMEOUT = bytes.fromhex("0001011d00228813000000000000000000000000000000000000000000000000")


@pytest.fixture
def schema():
    # board_id 1 = this node, which is who the firmware addressed the replies to.
    return PacketSchema(packet_size=32, topology=Topology.NETWORK, board_id=1)


def test_a_real_completion_decodes(schema):
    reply = parse_reply(decode_validated_and_addressed(schema, FINISHED), uid_bytes=UID_BYTES)

    assert reply.uid == 29
    assert reply.status == StatusCode.TASK_FINISHED
    assert codec.unpack(("float", "float", "uint8"), reply.result) == (12.5, -3.25, 9)


def test_a_task_chosen_status_decodes(schema):
    # The whole point of status-keyed returns: the same task, a different status,
    # and therefore a different result shape.
    reply = parse_reply(decode_validated_and_addressed(schema, TIMEOUT), uid_bytes=UID_BYTES)

    assert reply.uid == 29
    assert reply.status == StatusCode.TASK_TIMEOUT
    assert codec.unpack(("uint32",), reply.result) == (5000,)


def test_the_two_replies_differ_only_where_they_should(schema):
    # Same uid, same header: the status byte is what discriminates the shape.
    finished = parse_reply(decode_validated_and_addressed(schema, FINISHED), uid_bytes=UID_BYTES)
    timeout = parse_reply(decode_validated_and_addressed(schema, TIMEOUT), uid_bytes=UID_BYTES)

    assert finished.uid == timeout.uid
    assert finished.status != timeout.status
