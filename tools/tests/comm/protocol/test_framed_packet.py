# tests/test_framed_packet.py
# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-

import ctypes
import re
import pytest

from comm.protocol.framed_packet import FramedPacket
from comm.protocol.packet_header import (
    PacketHeader,
    HeaderType,
    HeaderFlags,
    _PacketHeaderStructure,
)
from comm.protocol.checksum import (
    Checksum,
    NONE, SUM8, SUM16, SUM32,
    CRC8, CRC16, CRC32, CRC64,
    FLETCHER16, FLETCHER32,
    ADLER32,
    INTERNET16,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

UID_TYPES = [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint64]
POLICIES  = [NONE, SUM8, SUM16, SUM32, CRC8, CRC16, CRC32, CRC64, FLETCHER16, FLETCHER32, ADLER32, INTERNET16]

WORD     = ctypes.sizeof(ctypes.c_size_t)
HDR_SIZE = ctypes.sizeof(_PacketHeaderStructure)  # should be 4 (packed)

def align_up(n: int, align: int) -> int:
    return (n + (align - 1)) // align * align

def min_frame_size_for(uid_ctype: type, policy: Checksum) -> int:
    """Minimal legal framed-packet size (no payload) — *without* alignment."""
    tid = ctypes.sizeof(uid_ctype)
    return HDR_SIZE + 1 + tid + policy.size  # header + status + task_id + fcs

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

# Compute offsets for byte-slicing inspections
def offsets(pkt: FramedPacket):
    off_status  = HDR_SIZE
    off_task_id = off_status + 1
    off_payload = off_task_id + pkt.task_id_size
    off_fcs     = off_payload + pkt.payload_size  # may equal packet_size if policy.size==0
    return off_status, off_task_id, off_payload, off_fcs

# ---------------------------------------------------------------------------
# Layout / size tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
@pytest.mark.parametrize("policy", [NONE, CRC16, CRC32, CRC64])
def test_member_sizes_and_payload_deduction(uid_ctype, policy) -> None:
    """
    payload_size must satisfy:
        payload = packet_size - sizeof(header) - 1 - sizeof(uid) - policy.size
    """
    min_size = min_frame_size_for(uid_ctype, policy)
    # choose an aligned size with room for payload
    pkt_size = align_up(min_size + WORD, WORD)

    hdr = build_header()
    pkt = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=0)

    assert pkt.packet_size == pkt_size
    assert pkt.header_size == HDR_SIZE
    assert pkt.task_id_size == ctypes.sizeof(uid_ctype)
    assert pkt.payload_size == pkt_size - min_size
    assert len(bytes(pkt)) == pkt_size
    assert len(pkt.payload) == pkt.payload_size

    # Offsets sanity
    off_status, off_task, off_payload, off_fcs = offsets(pkt)
    assert off_status  == HDR_SIZE
    assert off_task    == HDR_SIZE + 1
    assert off_payload == HDR_SIZE + 1 + pkt.task_id_size
    assert off_fcs     == pkt.packet_size - policy.size

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
@pytest.mark.parametrize("policy", POLICIES)
def test_packet_size_too_small_raises(uid_ctype, policy) -> None:
    min_size = min_frame_size_for(uid_ctype, policy)
    too_small = max(0, min_size - 1)
    hdr = build_header()
    with pytest.raises(ValueError, match=r"too small; minimum"):
        FramedPacket(too_small, uid_ctype, policy, header=hdr, task_id=0)

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
@pytest.mark.parametrize("policy", POLICIES)
def test_packet_size_not_aligned_raises(uid_ctype, policy) -> None:
    min_size = min_frame_size_for(uid_ctype, policy)
    base = max(min_size, WORD)
    not_aligned = base if base % WORD else base + 1
    hdr = build_header()
    with pytest.raises(ValueError, match=r"word-aligned"):
        FramedPacket(not_aligned, uid_ctype, policy, header=hdr, task_id=0)

# ---------------------------------------------------------------------------
# Policy impact tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_policy_influences_payload_size(uid_ctype) -> None:
    """
    For the same packet_size and uid_ctype, larger policy.size ⇒ smaller payload.
    Differences must equal differences in policy.size.
    """
    policies = [NONE, SUM8, CRC16, CRC32, CRC64]
    # choose a pkt_size large enough for all
    min_size_for_all = max(min_frame_size_for(uid_ctype, p) for p in policies)
    pkt_size = align_up(min_size_for_all + WORD, WORD)
    hdr = build_header()

    frames = [FramedPacket(pkt_size, uid_ctype, p, header=hdr, task_id=0) for p in policies]
    payloads = [f.payload_size for f in frames]

    # Payload should be strictly decreasing as policy.size grows
    for i in range(1, len(frames)):
        assert payloads[i-1] - payloads[i] == (policies[i].size - policies[i-1].size)

@pytest.mark.parametrize("policy", [NONE, CRC16, CRC32, CRC64])
def test_uid_type_influences_payload_size(policy) -> None:
    """
    For the same packet_size and policy, larger uid_type ⇒ smaller payload.
    Differences must equal sizeof(uid_type) deltas.
    """
    types = [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint64]
    min_size_for_all = max(min_frame_size_for(t, policy) for t in types)
    pkt_size = align_up(min_size_for_all + WORD, WORD)
    hdr = build_header()

    frames = [FramedPacket(pkt_size, t, policy, header=hdr, task_id=0) for t in types]
    payloads = [f.payload_size for f in frames]
    sizes = [ctypes.sizeof(t) for t in types]

    for i in range(1, len(frames)):
        assert payloads[i-1] - payloads[i] == (sizes[i] - sizes[i-1])

# ---------------------------------------------------------------------------
# Header tests (round-trip of fields)
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
    policy = CRC32
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)

    hdr = build_header(
        type_=type_,
        encrypted=encrypted,
        fragmented=fragmented,
        priority=priority,
        flags=flags,
        validated=validated,
        receiver_id=receiver_id,
    )
    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=123, status_code=5)

    h = fp.header
    assert h.type == type_
    assert h.encrypted == encrypted
    assert h.fragmented == fragmented
    assert h.priority == priority
    assert h.flags == flags
    assert h.validated == validated
    assert h.receiver_id == receiver_id

# ---------------------------------------------------------------------------
# Status / Task ID tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype,max_ok", [
    (ctypes.c_uint8,  0xFF),
    (ctypes.c_uint16, 0xFFFF),
    (ctypes.c_uint32, 0xFFFFFFFF),
    (ctypes.c_uint64, 0xFFFFFFFFFFFFFFFF),
])
def test_task_id_bounds_and_setter(uid_ctype, max_ok) -> None:
    policy = NONE
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=0)
    assert fp.task_id == 0
    fp.task_id = 1
    assert fp.task_id == 1

    fp.task_id = max_ok
    assert fp.task_id == max_ok

    with pytest.raises(ValueError):
        fp.task_id = max_ok + 1
    with pytest.raises(ValueError):
        fp.task_id = -1

def test_status_code_bounds_and_setter() -> None:
    uid_ctype = ctypes.c_uint8
    policy = CRC16
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=0, status_code=0)
    assert fp.status_code == 0
    fp.status_code = 255
    assert fp.status_code == 255

    with pytest.raises(ValueError):
        fp.status_code = 256
    with pytest.raises(ValueError):
        fp.status_code = -1

# ---------------------------------------------------------------------------
# Payload behavior
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
@pytest.mark.parametrize("policy", [NONE, CRC16])
def test_payload_default_zero_and_copy(uid_ctype, policy) -> None:
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=7)
    off_status, off_task, off_payload, off_fcs = offsets(fp)

    # Default zero
    wire = bytes(fp)
    assert wire[off_payload:off_payload + fp.payload_size] == b"\x00" * fp.payload_size

    # Copy payload
    data = b"abc"
    fp2 = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=7, payload=data)
    wire2 = bytes(fp2)
    assert wire2[off_payload:off_payload + len(data)] == data

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_payload_memoryview_mutation_reflects(uid_ctype) -> None:
    policy = CRC32
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=99)
    if fp.payload_size == 0:
        pytest.skip("No payload region to mutate for this combination")

    mv = fp.payload  # class returns 'B'-casted memoryview
    mv[:3] = b"DEF"[: min(3, fp.payload_size)]
    wire = bytes(fp)

    _, _, off_payload, _ = offsets(fp)
    expect = b"DEF"[: min(3, fp.payload_size)]
    assert wire[off_payload:off_payload + len(expect)] == expect

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_payload_too_large_raises(uid_ctype) -> None:
    policy = NONE
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=1)
    too_big = b"x" * (fp.payload_size + 1)
    with pytest.raises(ValueError, match=r"payload too large"):
        FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=1, payload=too_big)

# ---------------------------------------------------------------------------
# FCS field behavior (presence/size/endian)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
def test_none_policy_has_no_fcs(uid_ctype) -> None:
    policy = NONE
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=0)
    assert fp.fcs is None
    with pytest.raises(ValueError, match="Checksum policy is NONE"):
        fp.fcs = 1  # cannot set

    # End of frame is payload end; no trailing FCS bytes
    off_status, off_task, off_payload, off_fcs = offsets(fp)
    assert off_fcs == fp.packet_size  # no fcs region

@pytest.mark.parametrize("policy, size", [(CRC16, 2), (CRC32, 4), (CRC64, 8), (SUM8, 1)])
def test_fcs_set_and_bytes_reflect(policy, size) -> None:
    uid_ctype = ctypes.c_uint16
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=0)

    # initial fcs should be zero
    assert fp.fcs == 0

    # set via int (max boundary)
    max_val = (1 << (8 * size)) - 1
    fp.fcs = max_val
    assert fp.fcs == max_val

    # bytes at end are little-endian fcs
    wire = bytes(fp)
    _, _, _, off_fcs = offsets(fp)
    assert wire[off_fcs:off_fcs + size] == max_val.to_bytes(size, "little")

    # set via bytes (exact length)
    val2 = 0xA5 if size == 1 else 0xA5_5A if size == 2 else 0xA5_5A_FA_C3 & max_val
    fp.fcs = val2.to_bytes(size, "little")
    assert fp.fcs == val2

    # wrong bytes length
    with pytest.raises(ValueError, match=r"fcs byte length must be exactly"):
        fp.fcs = b"\x00" * (size + 1)

def test_fcs_value_out_of_range_raises() -> None:
    uid_ctype = ctypes.c_uint8
    policy = CRC16
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=0)

    with pytest.raises(ValueError, match=r"fcs must fit into 2 bytes unsigned"):
        fp.fcs = 0x1_0000  # 16-bit overflow
    with pytest.raises(ValueError):
        fp.fcs = -1

@pytest.mark.parametrize("policy", [CRC16, CRC32])
def test_constructor_accepts_fcs_bytes_and_int(policy) -> None:
    uid_ctype = ctypes.c_uint16
    size = policy.size
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    # via int
    v = (1 << (8 * size)) - 1
    fp1 = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=1, fcs=v)
    assert fp1.fcs == v

    # via bytes
    v2 = 0x1234_5678 & ((1 << (8 * size)) - 1)
    fp2 = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=1, fcs=v2.to_bytes(size, "little"))
    assert fp2.fcs == v2

    # wrong byte length
    with pytest.raises(ValueError, match="fcs byte length must be exactly"):
        FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=1, fcs=b"\x00" * (size + 1))

# ---------------------------------------------------------------------------
# Bytes / repr tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_TYPES)
@pytest.mark.parametrize("policy", [NONE, CRC32])
def test_bytes_length_and_equivalence(uid_ctype, policy) -> None:
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=1, payload=b"\xAA")
    assert len(fp.to_bytes()) == pkt_size
    assert bytes(fp) == fp.to_bytes()

@pytest.mark.parametrize("policy", [NONE, CRC32])
def test_repr_contains_key_fields(policy) -> None:
    uid_ctype = ctypes.c_uint32
    min_size = min_frame_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header(flags=HeaderFlags.ERROR, receiver_id=200)

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=123, status_code=7, payload=b"hi")
    s = repr(fp)
    assert f"packet_size={pkt_size}" in s
    assert re.search(r"task_id_ctype=\w+", s)
    assert f"policy={policy.name}" in s
    assert "status_code=7" in s
    assert "task_id=123" in s
