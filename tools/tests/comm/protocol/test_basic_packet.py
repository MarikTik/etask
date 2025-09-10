# tests/test_basic_packet.py
# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-

import ctypes
import itertools
import re
import pytest

from comm.protocol.basic_packet import BasicPacket
from comm.protocol.packet_header import (
    PacketHeader,
    HeaderType,
    HeaderFlags,
    _PacketHeaderStructure,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

UID_TYPES = [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint64]
WORD = ctypes.sizeof(ctypes.c_size_t)
HDR_SIZE = ctypes.sizeof(_PacketHeaderStructure)  # should be 4 (packed)

def min_packet_size_for(uid_ctype: type) -> int:
    """Minimum legal packet size (no payload), *without alignment* applied."""
    tid = ctypes.sizeof(uid_ctype)
    return HDR_SIZE + 1 + tid  # header + status + task_id

def align_up(n: int, align: int) -> int:
    """Round n up to the nearest multiple of align."""
    return (n + (align - 1)) // align * align

def build_header(
    *,
    type_: HeaderType = HeaderType.CONTROL,
    encrypted: bool = False,
    fragmented: bool = False,
    priority: int = 0,
    flags: HeaderFlags = HeaderFlags.ACK,
    validated: bool = False,
    receiver_id: int = 1,
) -> PacketHeader:
    return PacketHeader.from_fields(
        type=type_,
        encrypted=encrypted,
        fragmented=fragmented,
        priority=priority,
        flags=flags,
        validated=validated,
        receiver_id=receiver_id,
    )

# ---------------------------------------------------------------------------
# Size / layout tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_member_sizes_and_payload_deduction_minimal(uid_ctype) -> None:
    """
    For each uid_type, the payload size must satisfy:
    payload = packet_size - sizeof(header) - 1 (status) - sizeof(uid)
    using the minimal aligned packet size (i.e., zero payload).
    """
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size, WORD)  # minimal aligned size ⇒ payload==pkt_size-min_size

    hdr = build_header()
    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=0)

    assert pkt.packet_size == pkt_size
    assert pkt.header_size == HDR_SIZE
    assert pkt.task_id_size == ctypes.sizeof(uid_ctype)
    assert pkt.payload_size == pkt_size - min_size
    assert len(bytes(pkt)) == pkt_size
    assert len(pkt.payload) == pkt.payload_size

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_member_sizes_and_payload_deduction_nonzero(uid_ctype) -> None:
    """
    Use a larger, aligned packet size to ensure payload > 0 and the formula still holds.
    """
    min_size = min_packet_size_for(uid_ctype)
    base = align_up(min_size, WORD)
    # Add one alignment quantum to guarantee nonzero payload
    pkt_size = base + WORD

    hdr = build_header()
    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=0)

    assert pkt.payload_size == pkt_size - min_size
    assert pkt.payload_size > 0
    assert len(bytes(pkt)) == pkt_size
    assert len(pkt.payload) == pkt.payload_size

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_packet_size_too_small_raises(uid_ctype) -> None:
    min_size = min_packet_size_for(uid_ctype)
    too_small = max(0, min_size - 1)

    hdr = build_header()
    with pytest.raises(ValueError, match=r"too small; minimum"):
        BasicPacket(too_small, uid_ctype, header=hdr, task_id=0)

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_packet_size_not_aligned_raises(uid_ctype) -> None:
    min_size = min_packet_size_for(uid_ctype)
    # Choose a size >= min and *not* word-aligned
    base = max(min_size, WORD)  # ensure >= WORD
    not_aligned = base if base % WORD else base + 1

    hdr = build_header()
    with pytest.raises(ValueError, match=r"word-aligned"):
        BasicPacket(not_aligned, uid_ctype, header=hdr, task_id=0)

# ---------------------------------------------------------------------------
# Header tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("type_", [HeaderType.DATA, HeaderType.CONTROL, HeaderType.STATUS])
@pytest.mark.parametrize("encrypted", [False, True])
@pytest.mark.parametrize("fragmented", [False, True])
@pytest.mark.parametrize("priority", [0, 7])
@pytest.mark.parametrize("flags", [HeaderFlags.ACK, HeaderFlags.ERROR, HeaderFlags.HEARTBEAT])
@pytest.mark.parametrize("validated", [False, True])
@pytest.mark.parametrize("receiver_id", [0, 1, 255])
def test_header_roundtrip_fields(type_, encrypted, fragmented, priority, flags, validated, receiver_id) -> None:
    uid_ctype = ctypes.c_uint16
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)  # nonzero payload

    hdr = build_header(
        type_=type_,
        encrypted=encrypted,
        fragmented=fragmented,
        priority=priority,
        flags=flags,
        validated=validated,
        receiver_id=receiver_id,
    )
    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=123, status_code=5)

    # Compare relevant fields after BasicPacket → bytes → PacketHeader (property) wrap
    h = pkt.header
    assert h.type == type_
    assert h.encrypted == encrypted
    assert h.fragmented == fragmented
    assert h.priority == priority
    # HeaderFlags only stores 3 bits (bits 4–2); using ACK/ERROR/HEARTBEAT keeps us within these bits
    assert h.flags == flags
    assert h.validated == validated
    assert h.receiver_id == receiver_id

# ---------------------------------------------------------------------------
# Status code / Task ID tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype,max_ok", [
    (ctypes.c_uint8,  0xFF),
    (ctypes.c_uint16, 0xFFFF),
    (ctypes.c_uint32, 0xFFFFFFFF),
    (ctypes.c_uint64, 0xFFFFFFFFFFFFFFFF),
])
def test_task_id_bounds_and_setter(uid_ctype, max_ok) -> None:
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    # Lower bound
    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=0)
    assert pkt.task_id == 0
    pkt.task_id = 1
    assert pkt.task_id == 1

    # Upper bound
    pkt.task_id = max_ok
    assert pkt.task_id == max_ok

    # Out of range (too big)
    with pytest.raises(ValueError, match=r"must fit into .* bytes unsigned"):
        pkt.task_id = max_ok + 1

    # Negative
    with pytest.raises(ValueError):
        pkt.task_id = -1

def test_status_code_bounds_and_setter() -> None:
    uid_ctype = ctypes.c_uint8
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size, WORD)
    hdr = build_header()

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=0, status_code=0)
    assert pkt.status_code == 0

    pkt.status_code = 255
    assert pkt.status_code == 255

    with pytest.raises(ValueError):
        pkt.status_code = 256
    with pytest.raises(ValueError):
        pkt.status_code = -1

# ---------------------------------------------------------------------------
# Payload tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_payload_default_zero_filled(uid_ctype) -> None:
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)  # ensure nonzero payload
    hdr = build_header()

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=0)
    payload_slice = bytes(pkt)[HDR_SIZE + 1 + pkt.task_id_size :]
    assert payload_slice == b"\x00" * pkt.payload_size

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_payload_copy_and_bounds(uid_ctype) -> None:
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)  # ensure space
    hdr = build_header()

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=7, payload=b"abc")
    assert pkt.payload.tobytes()[:3] == b"abc"
    assert len(pkt.payload) == pkt.payload_size

    # Fit exactly to end
    exact = b"x" * pkt.payload_size
    pkt2 = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=7, payload=exact)
    assert pkt2.payload.tobytes() == exact

    # Too large → error
    too_big = b"y" * (pkt.payload_size + 1)
    with pytest.raises(ValueError, match=r"payload too large"):
        BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=7, payload=too_big)

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_payload_memoryview_mutation_reflects(uid_ctype) -> None:
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=99)
    if pkt.payload_size == 0:
        pytest.skip("No payload region to mutate for this combination")
    mv = pkt.payload.cast("B")
    mv[:3] = b"DEF"[: min(3, pkt.payload_size)]
    bts = bytes(pkt)
    # Check that bytes at payload start reflect "DEF"
    start = HDR_SIZE + 1 + pkt.task_id_size
    expect = b"DEF"[: min(3, pkt.payload_size)]
    assert bts[start : start + len(expect)] == expect

# ---------------------------------------------------------------------------
# Bytes / repr tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_bytes_length_and_equivalence(uid_ctype) -> None:
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=1, payload=b"\xAA")
    assert len(pkt.to_bytes()) == pkt_size
    assert bytes(pkt) == pkt.to_bytes()

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_repr_contains_key_fields(uid_ctype) -> None:
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header(flags=HeaderFlags.ERROR, receiver_id=200)

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=123, status_code=7, payload=b"hi")
    s = repr(pkt)
    # A quick sanity check that repr mentions key fields (don’t overfit to exact formatting)
    assert f"packet_size={pkt_size}" in s
    assert re.search(r"task_id_ctype=\w+", s)
    assert "status_code=7" in s
    assert "task_id=123" in s

# ---------------------------------------------------------------------------
# Cross-type comparison tests
# ---------------------------------------------------------------------------

def test_uid_type_influences_payload_size() -> None:
    """
    For the same packet_size, a larger uid_type must yield a smaller payload_size.
    """
    pkt_size = align_up(min_packet_size_for(ctypes.c_uint64) + WORD, WORD)
    hdr = build_header()

    p8  = BasicPacket(pkt_size, ctypes.c_uint8,  header=hdr, task_id=0)
    p16 = BasicPacket(pkt_size, ctypes.c_uint16, header=hdr, task_id=0)
    p32 = BasicPacket(pkt_size, ctypes.c_uint32, header=hdr, task_id=0)
    p64 = BasicPacket(pkt_size, ctypes.c_uint64, header=hdr, task_id=0)

    assert p8.payload_size  > p16.payload_size  > p32.payload_size  > p64.payload_size
    # Check exact differences match sizeof(uid_type) deltas
    assert (p8.payload_size - p16.payload_size) == (ctypes.sizeof(ctypes.c_uint16) - ctypes.sizeof(ctypes.c_uint8))
    assert (p16.payload_size - p32.payload_size) == (ctypes.sizeof(ctypes.c_uint32) - ctypes.sizeof(ctypes.c_uint16))
    assert (p32.payload_size - p64.payload_size) == (ctypes.sizeof(ctypes.c_uint64) - ctypes.sizeof(ctypes.c_uint32))

# ---------------------------------------------------------------------------
# Defensive tests (edge error paths)
# ---------------------------------------------------------------------------

def test_header_bytes_length_mismatch_raises(monkeypatch) -> None:
    """
    Simulate a header.to_bytes() of wrong length to ensure the guard triggers.
    """
    uid_ctype = ctypes.c_uint8
    min_size = min_packet_size_for(uid_ctype)
    pkt_size = align_up(min_size, WORD)

    hdr = build_header()
    # Monkeypatch to_bytes to return wrong size
    monkeypatch.setattr(hdr, "to_bytes", lambda: b"\x00\x01")  # too short
    with pytest.raises(ValueError, match=r"Invalid header byte length"):
        BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=0)
