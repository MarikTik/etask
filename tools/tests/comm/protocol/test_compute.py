# tools/tests/comm/test_compute.py
# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-

import os
import binascii
import zlib
import random
import pytest

from comm.protocol.checksum import (
    Checksum,
    NONE, SUM8, SUM16, SUM32,
    CRC8, CRC16, CRC32, CRC64,
    FLETCHER16, FLETCHER32,
    ADLER32,
    INTERNET16,
)

from comm.protocol.compute import compute

# -----------------------------------------------------------------------------
# helpers
# -----------------------------------------------------------------------------

def concat(*chunks: bytes) -> bytes:
    return b"".join(chunks)

def randbytes(n: int) -> bytes:
    # python3.9 compatible
    return os.urandom(n)

ALL_POLICIES = [
    NONE, SUM8, SUM16, SUM32,
    CRC8, CRC16, CRC32, CRC64,
    FLETCHER16, FLETCHER32,
    ADLER32,
    INTERNET16,
]

# “123456789” is the canonical vector for many checksums.
CANON = b"123456789"

# -----------------------------------------------------------------------------
# known vectors (documented parameters in compute.py)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("policy,expected", [
    (SUM8,        0x00DD),             # sum of ASCII digits = 477 => 0x1DD -> 0xDD
    (SUM16,       0x01DD),
    (SUM32,       0x000001DD),

    # CRC-8/ATM: poly=0x07, init=0x00, xorout=0x00, non-reflected
    (CRC8,        0xF4),

    # CRC-16/CCITT (a.k.a. XMODEM): poly=0x1021, init=0x0000, xorout=0x0000, non-reflected
    (CRC16,       0x31C3),

    # CRC-32/IEEE (binascii.crc32): "123456789" -> 0xCBF43926
    (CRC32,       0xCBF43926),

    # CRC-64/ECMA-182: "123456789" -> 0x6C40DF5F0B497347
    (CRC64,       0x6C40DF5F0B497347),

    # Fletcher16 over bytes
    (FLETCHER16,  0x1EDE),

    # Fletcher32 over 16-bit big-endian words (pad last byte)
    (FLETCHER32,  0x09DF09D5),

    # Adler32 (zlib): "123456789" -> 0x091E01DE
    (ADLER32,     0x091E01DE),

    # Internet checksum (RFC 1071): "123456789" -> 0xF62A
    (INTERNET16,  0xF62A),
])
def test_known_vector_123456789(policy: Checksum, expected: int):
    assert compute(policy, CANON) == expected


# -----------------------------------------------------------------------------
# empty input behavior
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("policy,expected", [
    (NONE,        0),
    (SUM8,        0),
    (SUM16,       0),
    (SUM32,       0),
    (CRC8,        0),
    (CRC16,       0),
    (CRC32,       0),
    (CRC64,       0),
    (FLETCHER16,  0),
    (FLETCHER32,  0),
    (ADLER32,     1),       # Adler32 of empty buffer is 1
    (INTERNET16,  0xFFFF),  # one's complement of zero
])
def test_empty_input(policy: Checksum, expected: int) -> None:
    assert compute(policy, b"") == expected


# -----------------------------------------------------------------------------
# width fitting (result must fit in policy.size bytes)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("policy", ALL_POLICIES)
def test_result_fits_declared_size(policy: Checksum) -> None:
    data = randbytes(257)
    val = compute(policy, data)
    if policy.size == 0:
        assert val == 0
    else:
        mask = (1 << (8 * policy.size)) - 1
        assert 0 <= val <= mask, f"checksum {val:#x} exceeds {policy.size} bytes"


# -----------------------------------------------------------------------------
# streaming / chunking invariance
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("policy", ALL_POLICIES)
@pytest.mark.parametrize("split", [0, 1, 2, 3, 7, 8, 15, 16, 31])
def test_chunking_invariance(policy: Checksum, split: int) -> None:
    data = randbytes(64)
    a = compute(policy, data)
    b = compute(policy, data[:split], data[split:])
    c = compute(policy, memoryview(data[:split]), bytearray(data[split:]))
    assert a == b == c


# -----------------------------------------------------------------------------
# cross-check with stdlib where possible
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("length", [0, 1, 2, 7, 32, 257, 2048])
def test_crc32_matches_binascii(length: int) -> None:
    d = randbytes(length)
    assert compute(CRC32, d) == (binascii.crc32(d) & 0xFFFFFFFF)

@pytest.mark.parametrize("length", [0, 1, 2, 7, 32, 257, 2048])
def test_adler32_matches_zlib(length: int) -> None:
    d = randbytes(length)
    # recompute using a single blob to avoid zlib's internal state nuances
    assert compute(ADLER32, d) == (zlib.adler32(d) & 0xFFFFFFFF)


# -----------------------------------------------------------------------------
# additional algorithm-specific spot checks
# -----------------------------------------------------------------------------
def test_internet16_odd_length_and_carries() -> None:
    # odd length case
    assert compute(INTERNET16, b"A") == 0xBEFF  # ~0x4100
    # ensure carry folds properly (lots of 0xFF -> produces carries)
    buf = b"\xFF" * 101
    v = compute(INTERNET16, buf)
    assert 0 <= v <= 0xFFFF

def test_fletcher32_chunk_boundaries() -> None:
    # craft boundaries that force an odd trailing byte across chunks
    d1 = b"\x01\x02\x03"
    d2 = b"\x04"
    d3 = b"\x05\x06\x07"
    full = d1 + d2 + d3
    a = compute(FLETCHER32, full)
    b = compute(FLETCHER32, d1, d2, d3)
    c = compute(FLETCHER32, d1 + d2, d3)  # combine differently
    assert a == b == c

@pytest.mark.parametrize("policy", [CRC8, CRC16, CRC64])
def test_crc_polys_consistency_with_known_vectors(policy: Checksum) -> None:
    """
    Extra sanity: the canonical '123456789' vector further validates table params.
    (CRC32 is covered by stdlib cross-check above.)
    """
    expect = {
        CRC8.name:  0xF4,
        CRC16.name: 0x31C3,
        CRC64.name: 0x6C40DF5F0B497347,
    }[policy.name]
    assert compute(policy, CANON) == expect

@pytest.mark.parametrize("policy", [SUM8, SUM16, SUM32, FLETCHER16])
def test_small_manual_vectors(policy: Checksum) -> None:
    # For b"\x01\x02\x03":
    data = b"\x01\x02\x03"
    if policy is SUM8:
        assert compute(policy, data) == (1+2+3) & 0xFF
    elif policy is SUM16:
        assert compute(policy, data) == (1+2+3) & 0xFFFF
    elif policy is SUM32:
        assert compute(policy, data) == (1+2+3) & 0xFFFFFFFF
    elif policy is FLETCHER16:
        # step-by-step
        # s1: 1 -> 3 -> 6; s2: 1 -> 4 -> 10
        assert compute(policy, data) == ((10 << 8) | 6)

def test_none_policy_always_zero() -> None:
    for n in [0, 1, 2, 5, 33, 1000]:
        assert compute(NONE, randbytes(n)) == 0
    assert compute(NONE, b"abc", b"def") == 0
