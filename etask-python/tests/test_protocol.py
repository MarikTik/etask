# etask-python/tests/test_protocol.py
# SPDX-License-Identifier: MIT
"""The wire layer, checked against the layouts the C++ headers document."""

import struct

import pytest
from ecomm.protocol.schema import PacketSchema
from ecomm.protocol.topology import Topology
from ecomm.protocol.header_options import HeaderOptions
from ecomm.protocol.header_type import HeaderType
from ecomm.protocol.packet import Packet

from etask import codec
from etask.directive import CompletionReason, Directive, Operation
from etask.protocol import PayloadTooSmall, build_request, parse_reply
from etask.status_code import StatusCode, status_name


@pytest.fixture
def schema():
    return PacketSchema(packet_size=32, topology=Topology.NETWORK, board_id=2)


# -----------------------
# directive.hpp: command in the high 2 bits, reason in the low 6
# -----------------------

def test_directive_packs_command_high_and_reason_low():
    assert Directive(Operation.REGISTER_TASK).raw == 0b00_000000
    assert Directive(Operation.PAUSE_TASK).raw == 0b01_000000
    assert Directive(Operation.RESUME_TASK).raw == 0b10_000000
    assert Directive(Operation.COMPLETE_TASK).raw == 0b11_000000
    assert Directive(Operation.COMPLETE_TASK, CompletionReason.ABORTED).raw == 0b11_000001


def test_directive_roundtrips():
    for command in Operation:
        for reason in (0, 1, 0x10, 0x3F):
            packed = Directive(command, reason)
            assert Directive.unpack(packed.raw) == packed


def test_reason_wider_than_six_bits_is_refused():
    # completion_reason is capped at 0x3F precisely so it shares the byte.
    with pytest.raises(ValueError, match="6 bits"):
        Directive(Operation.COMPLETE_TASK, 0x40)


# -----------------------
# request.hpp: [directive][uid][args]
# -----------------------

def test_request_layout(schema):
    args = codec.pack(("float", "uint8"), (1.5, 7))
    packet = build_request(
        schema, uid=0x1234, uid_bytes=2,
        operation=Operation.REGISTER_TASK, args=args, receiver_id=5,
    )
    assert packet.payload[0] == 0  # register_task, reason 0
    assert bytes(packet.payload[1:3]) == (0x1234).to_bytes(2, "little")
    assert bytes(packet.payload[3:8]) == args
    assert packet.header.receiver_id == 5
    # An etask request is never an ecomm *error envelope*.
    assert packet.header.options == HeaderOptions.NONE
    assert packet.header.type == HeaderType.DATA


def test_complete_request_carries_its_reason(schema):
    packet = build_request(
        schema, uid=1, uid_bytes=1,
        operation=Operation.COMPLETE_TASK, reason=CompletionReason.ABORTED,
    )
    parsed = Directive.unpack(packet.payload[0])
    assert parsed.command is Operation.COMPLETE_TASK
    assert parsed.reason == CompletionReason.ABORTED


def test_request_that_cannot_fit_is_refused(schema):
    with pytest.raises(PayloadTooSmall, match="enlarge packet_size"):
        build_request(schema, uid=1, uid_bytes=1,
                      operation=Operation.REGISTER_TASK, args=b"x" * 64)


# -----------------------
# reply.hpp: [uid][status][result]
# -----------------------

def make_reply(schema, uid: int, uid_bytes: int, status: int, result: bytes = b"") -> Packet:
    packet = Packet(schema, HeaderType.DATA, HeaderOptions.NONE)
    packet.payload[0:uid_bytes] = uid.to_bytes(uid_bytes, "little")
    packet.payload[uid_bytes] = status
    if result:
        packet.payload[uid_bytes + 1:uid_bytes + 1 + len(result)] = result
    return packet


def test_reply_parses_uid_status_and_result(schema):
    result = codec.pack(("float", "float"), (1.0, 2.0))
    packet = make_reply(schema, uid=42, uid_bytes=2, status=StatusCode.TASK_FINISHED, result=result)
    reply = parse_reply(packet, uid_bytes=2)

    assert reply.uid == 42
    assert reply.status == StatusCode.TASK_FINISHED
    assert reply.is_finished and not reply.is_rejection
    assert codec.unpack(("float", "float"), reply.result) == (1.0, 2.0)


def test_manager_status_reads_as_a_rejection(schema):
    packet = make_reply(schema, uid=7, uid_bytes=1, status=StatusCode.TASK_UNKNOWN)
    reply = parse_reply(packet, uid_bytes=1)
    assert reply.is_rejection
    assert reply.status_name == "task_unknown"


def test_result_too_large_arrives_as_a_task_status(schema):
    # The firmware sends it with an empty result region; it is a completion, not
    # a manager rejection.
    packet = make_reply(schema, uid=7, uid_bytes=1, status=StatusCode.RESULT_TOO_LARGE)
    reply = parse_reply(packet, uid_bytes=1)
    assert not reply.is_rejection
    assert reply.status_name == "result_too_large"


def test_unlisted_custom_status_still_gets_a_name():
    assert status_name(0x7A) == "custom(0x7A)"
    assert status_name(0x1E) == "unknown(0x1E)"


# -----------------------
# codec: flat, little-endian, in declaration order
# -----------------------

def test_values_are_packed_flat_and_little_endian():
    packed = codec.pack(("uint16", "uint32"), (0x0102, 0x03040506))
    assert packed == struct.pack("<HI", 0x0102, 0x03040506)
    assert packed == b"\x02\x01\x06\x05\x04\x03"


def test_wire_sizes_match_the_cpp_types():
    assert codec.wire_size(("bool", "int8", "int16", "int32", "int64")) == 1 + 1 + 2 + 4 + 8
    assert codec.wire_size(("float", "double")) == 4 + 8


def test_unpack_ignores_the_zero_padding_after_the_values():
    data = codec.pack(("uint8",), (9,)) + b"\x00" * 20
    assert codec.unpack(("uint8",), data) == (9,)


def test_unpack_refuses_a_short_result():
    with pytest.raises(ValueError, match="need 4 byte"):
        codec.unpack(("uint32",), b"\x01\x02")


def test_unknown_type_is_named_in_the_error():
    with pytest.raises(codec.UnknownWireType, match="string"):
        codec.pack(("string",), ("hi",))
