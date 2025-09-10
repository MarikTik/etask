# tools/tests/comm/test_validator.py
# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-

import ctypes
import pytest

from comm.protocol.packet_header import PacketHeader, HeaderType, HeaderFlags
from comm.protocol.basic_packet import BasicPacket
from comm.protocol.framed_packet import FramedPacket
from comm.protocol.validator import Validator, is_packet_valid, seal_packet
from comm.protocol.checksum import (
    NONE, SUM8, SUM16, CRC8, CRC16, CRC32, CRC64,
    FLETCHER16, FLETCHER32, ADLER32, INTERNET16, Checksum
)
from comm.protocol.compute import compute


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

UID_CTYPES = [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint64]
POLICIES_ALL = [SUM8, SUM16, CRC8, CRC16, CRC32, CRC64, FLETCHER16, FLETCHER32, ADLER32, INTERNET16]
POLICIES_LIGHT = [CRC8, CRC16, CRC32, SUM8, INTERNET16]  # faster subset for some param tests

WORD = ctypes.sizeof(ctypes.c_size_t)
HEADER_SIZE = 4  # from _PacketHeaderStructure


def align_up(n: int, a: int) -> int:
    r = n % a
    return n if r == 0 else n + (a - r)


def min_basic_size_for(uid_ctype) -> int:
    return HEADER_SIZE + 1 + ctypes.sizeof(uid_ctype)


def min_framed_size_for(uid_ctype, policy: Checksum) -> int:
    return HEADER_SIZE + 1 + ctypes.sizeof(uid_ctype) + policy.size


def build_header(receiver_id: int = 1) -> PacketHeader:
    return PacketHeader.from_fields(
        type=HeaderType.DATA,
        encrypted=False,
        fragmented=False,
        priority=0,
        flags=HeaderFlags.NONE,
        validated=False,
        receiver_id=receiver_id,
    )


# ---------------------------------------------------------------------------
# BasicPacket tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_CTYPES)
def test_basicpacket_is_valid_always_true(uid_ctype) -> None:
    min_size = min_basic_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)  # ensure payload exists too
    hdr = build_header()

    payload_room = pkt_size - min_size
    payload = bytes(range(min(16, payload_room)))

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=7, payload=payload)
    v = Validator()

    assert v.is_valid(pkt) is True
    seal_packet(pkt)  # should be a no-op
    assert v.is_valid(pkt) is True

    # mutating should not change validity (no checksum)
    if pkt.payload_size:
        mv = pkt.payload
        mv[0] = (mv[0] + 1) % 256
        assert v.is_valid(pkt) is True


@pytest.mark.parametrize("uid_ctype", UID_CTYPES)
def test_basicpacket_seal_is_noop(uid_ctype) -> None:
    min_size = min_basic_size_for(uid_ctype)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    pkt = BasicPacket(pkt_size, uid_ctype, header=hdr, task_id=123, status_code=3, payload=b"abc")
    before = bytes(pkt)
    Validator().seal(pkt)
    after = bytes(pkt)
    assert after == before


# ---------------------------------------------------------------------------
# FramedPacket with NONE policy
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_CTYPES)
def test_framedpacket_none_policy_behaves_like_basic(uid_ctype) -> None:
    min_size = min_framed_size_for(uid_ctype, NONE)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    pkt = FramedPacket(pkt_size, uid_ctype, NONE, header=hdr, task_id=1, payload=b"xyz")
    v = Validator()

    assert pkt.policy is NONE
    assert pkt.fcs is None  # no field exists
    assert v.is_valid(pkt) is True

    before = bytes(pkt)
    v.seal(pkt)  # no-op
    after = bytes(pkt)
    assert before == after

    # fcs setter must fail in NONE
    with pytest.raises(ValueError):
        pkt.fcs = 0x1234


# ---------------------------------------------------------------------------
# FramedPacket with real policies — sealing & validating
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("uid_ctype", UID_CTYPES)
@pytest.mark.parametrize("policy", POLICIES_LIGHT)
def test_framedpacket_seal_and_validate(uid_ctype, policy) -> None:
    min_size = min_framed_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    payload_room = pkt_size - min_size
    payload = bytes(range(min(32, payload_room)))

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=77, status_code=9, payload=payload)
    v = Validator()

    # Before sealing, checksum likely mismatches (fcs default is 0)
    # We won't assert False here because some sums can coincidentally be 0.
    # But after sealing, it MUST be valid.
    v.seal(fp)
    assert fp.fcs is not None
    assert v.is_valid(fp) is True

    # Recompute manually and compare with stored field
    end = fp.packet_size - policy.size
    expected = compute(policy, bytes(fp)[:end])
    assert fp.fcs == expected

    # Mutate payload -> invalid
    if fp.payload_size:
        mv = fp.payload
        mv[-1] = (mv[-1] + 1) % 256
        assert v.is_valid(fp) is False

        # Reseal restores validity
        v.seal(fp)
        assert v.is_valid(fp) is True

 
@pytest.mark.parametrize("uid_ctype", UID_CTYPES)
@pytest.mark.parametrize("policy", [CRC32, CRC16, INTERNET16])
def test_framedpacket_field_mutations_affect_validity(uid_ctype, policy) -> None:
    min_size = min_framed_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header(receiver_id=42)

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=200, status_code=1, payload=b"\xAA\xBB\xCC")
    v = Validator()
    v.seal(fp)
    assert v.is_valid(fp) is True

    # Change status code -> invalid
    fp.status_code = (fp.status_code + 1) & 0xFF
    assert v.is_valid(fp) is False
    v.seal(fp)
    assert v.is_valid(fp) is True

    # Change task_id -> invalid
    fp.task_id = (fp.task_id + 1) & ((1 << (8 * fp.task_id_size)) - 1)
    assert v.is_valid(fp) is False
    v.seal(fp)
    assert v.is_valid(fp) is True

    # Change header receiver -> invalid
    # (We can't assign to header fields directly; re-copy bytes instead)
    new_hdr = build_header(receiver_id=99)
    hdr_bytes = new_hdr.to_bytes()
    mem = fp._c  # direct struct access (test-only)
    ctypes.memmove(ctypes.addressof(mem.header), hdr_bytes, fp.header_size)
    assert v.is_valid(fp) is False
    v.seal(fp)
    assert v.is_valid(fp) is True


@pytest.mark.parametrize("uid_ctype", UID_CTYPES)
@pytest.mark.parametrize("policy", POLICIES_LIGHT)
def test_framedpacket_zero_payload_size(uid_ctype, policy) -> None:
    """
    Choose the minimal aligned size so that payload_size can be zero and
    still be word-aligned. Then verify sealing and validity work.
    """
    min_size = min_framed_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size, WORD)  # smallest aligned frame
    hdr = build_header()
    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=1)
    v = Validator()

    assert fp.payload_size == pkt_size - min_size
    v.seal(fp)
    assert v.is_valid(fp) is True


@pytest.mark.parametrize("uid_ctype", UID_CTYPES)
@pytest.mark.parametrize("policy", POLICIES_LIGHT)
def test_framedpacket_fcs_mismatch_detected(uid_ctype, policy) -> None:
    min_size = min_framed_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=9, payload=b"abcdef")
    v = Validator()
    v.seal(fp)
    assert v.is_valid(fp) is True

    # Force a wrong FCS
    good = fp.fcs
    bad = (good + 1) & ((1 << (8 * policy.size)) - 1)
    fp.fcs = bad
    assert v.is_valid(fp) is False

    # Restore
    fp.fcs = good
    assert v.is_valid(fp) is True


def test_is_packet_valid_and_seal_packet_helpers() -> None:
    uid_ctype = ctypes.c_uint8
    policy = CRC32
    min_size = min_framed_size_for(uid_ctype, policy)
    pkt_size = align_up(min_size + WORD, WORD)
    hdr = build_header()

    fp = FramedPacket(pkt_size, uid_ctype, policy, header=hdr, task_id=22, payload=b"hello")
    assert is_packet_valid(fp) in (True, False)  # not sealed yet
    seal_packet(fp)
    assert is_packet_valid(fp) is True

    bp_min = min_basic_size_for(uid_ctype)
    bp_size = align_up(bp_min + WORD, WORD)
    bp = BasicPacket(bp_size, uid_ctype, header=hdr, task_id=3, payload=b"hi")
    assert is_packet_valid(bp) is True
    seal_packet(bp)  # no-op
    assert is_packet_valid(bp) is True
