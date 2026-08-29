# tools/tests/test_preamble.py
# SPDX-License-Identifier: MIT

import pytest

from etask.preamble import (
    MAGIC,
    SIZE,
    VERSION,
    PreambleError,
    SchemaMismatch,
    decode,
    discardable,
    encode,
    find,
)

_FP = 0x71DD4EB1C4E0392D

#: The exact bytes `etask/core/protocol/preamble.hpp` produces for _FP, captured
#: from a compiled probe. This is the cross-language contract: if either side
#: moves, this test fails rather than the handshake failing in the field for a
#: reason nobody can see.
_CPP_BYTES = bytes([
    0x45, 0x54, 0x53, 0x4B,   # "ETSK"
    0x01,                     # version
    0x00,                     # reserved
    0x71, 0xDD, 0x4E, 0xB1, 0xC4, 0xE0, 0x39, 0x2D,   # fingerprint, big-endian
])


# ------------------------------------------------------- the wire contract

def test_matches_the_cpp_encoding_byte_for_byte():
    assert encode(_FP) == _CPP_BYTES


def test_is_fourteen_bytes():
    assert SIZE == 14
    assert len(encode(_FP)) == 14


def test_layout_is_where_the_header_says_it_is():
    raw = encode(_FP)
    assert raw[0:4] == MAGIC
    assert raw[4] == VERSION
    assert raw[5] == 0
    assert int.from_bytes(raw[6:14], "big") == _FP


def test_fingerprint_is_big_endian():
    # A hex dump must read the same as the digest, on either peer.
    raw = encode(0x0123456789ABCDEF)
    assert raw[6:14] == bytes([0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF])


@pytest.mark.parametrize("value", [0, 1, 0xFF, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF])
def test_round_trips_edge_values(value):
    error, peer = decode(encode(value), value)
    assert error is PreambleError.NONE
    assert peer == value


# ----------------------------------------------------------------- decoding

def test_accepts_a_matching_peer():
    error, peer = decode(encode(_FP), _FP)
    assert error is PreambleError.NONE
    assert peer == _FP


def test_rejects_a_different_schema_and_reports_it():
    error, peer = decode(encode(0xDEADBEEFCAFEBABE), _FP)
    assert error is PreambleError.FINGERPRINT_MISMATCH
    # The peer's value is the "actual" half of the log line.
    assert peer == 0xDEADBEEFCAFEBABE


def test_rejects_a_foreign_protocol():
    error, peer = decode(b"HTTP/1.1 200 " + bytes(8), _FP)
    assert error is PreambleError.BAD_MAGIC
    assert peer is None


def test_rejects_an_unknown_preamble_version():
    raw = bytearray(encode(_FP))
    raw[4] = 0xFF
    error, peer = decode(bytes(raw), _FP)
    assert error is PreambleError.BAD_VERSION
    assert peer is None


def test_does_not_report_a_fingerprint_it_could_not_trust():
    # Eight bytes read out of a non-preamble are a random number that reads like
    # a real schema id; reporting one sends an operator hunting for a schema
    # that never existed.
    for raw in (b"XXXX" + bytes(10), bytearray(encode(_FP))[:4] + b"\xFF" + bytes(9)):
        _, peer = decode(bytes(raw), _FP)
        assert peer is None


def test_rejects_a_short_read():
    error, _ = decode(encode(_FP)[:13], _FP)
    assert error is PreambleError.BAD_MAGIC


def test_ignores_the_reserved_byte():
    # A future version may use it; refusing a non-zero value here would make
    # this build reject a peer it could otherwise talk to.
    raw = bytearray(encode(_FP))
    raw[5] = 0x7F
    error, _ = decode(bytes(raw), _FP)
    assert error is PreambleError.NONE


# ------------------------------------------------------------ stream framing

def test_finds_a_preamble_at_the_start():
    assert find(encode(_FP)) == 0


def test_finds_a_preamble_after_leading_noise():
    # A peer may be mid-stream, or may predate the handshake and open with task
    # traffic; neither may desynchronise the reader permanently.
    assert find(b"\x00\x01noise" + encode(_FP)) == 7


def test_reports_no_preamble_until_it_is_complete():
    partial = encode(_FP)[:10]
    assert find(partial) == -1
    assert find(partial + encode(_FP)[10:]) == 0


def test_reports_no_preamble_in_unrelated_bytes():
    assert find(b"nothing to see here") == -1


def test_discards_bytes_that_cannot_begin_a_preamble():
    assert discardable(b"junk" + MAGIC) == 4
    assert discardable(b"junk") == 4


def test_keeps_a_partial_magic_the_next_read_might_complete():
    # "ET" could be the start of the magic; dropping it would lose the frame.
    assert discardable(b"junkET") == 4
    assert discardable(b"ETS") == 0


# -------------------------------------------------------------- the exception

def test_mismatch_error_names_both_fingerprints():
    err = SchemaMismatch(PreambleError.FINGERPRINT_MISMATCH, _FP, 0xDEADBEEFCAFEBABE)
    text = str(err)
    assert "71dd4eb1c4e0392d" in text
    assert "deadbeefcafebabe" in text
    assert "Regenerate" in text


def test_bad_magic_error_suggests_the_likely_cause():
    text = str(SchemaMismatch(PreambleError.BAD_MAGIC, _FP, None))
    assert "different protocol" in text or "older than the handshake" in text
