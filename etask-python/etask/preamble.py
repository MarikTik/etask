"""The handshake preamble, byte-exact with ``etask/core/protocol/preamble.hpp``.

Two peers built from different schemas may disagree about *header layout* - one
puts a frame's payload at offset 3, the other at offset 8. Every field then
misparses, and the checksum cannot help because the two ends disagree about
where the checksum is. So the message that says "we disagree" cannot itself ride
in the frame whose shape is in question.

Hence a preamble whose layout is frozen forever, independent of any schema:
fourteen bytes, sent raw before any framing, carrying the eight-byte fingerprint
of the sender's wire contract. Both peers send theirs on connect and compare.

There is no checksum on the preamble. The fingerprint *is* the integrity check:
corrupted bytes fail the comparison and are reported as a mismatch, which is the
right answer anyway - a link that cannot deliver fourteen clean bytes has no
business carrying task traffic.
"""

from enum import Enum
from typing import Optional, Tuple


#: Marks the start of a preamble, and lets a reader resynchronise: a peer may be
#: mid-stream, or may predate the handshake and open with task traffic, and
#: neither should desynchronise the reader permanently.
MAGIC = b"ETSK"

#: Preamble format version - this frame's shape, not the schema's contract.
#: Bumped only if the fourteen bytes below are ever rearranged.
VERSION = 1

#: Written zero. Deliberately **not** validated on receipt: rejecting a value a
#: future version might put here would make this build refuse a peer it could
#: otherwise talk to.
RESERVED = 0

_MAGIC_AT = 0
_VERSION_AT = 4
_RESERVED_AT = 5
_FINGERPRINT_AT = 6
_FINGERPRINT_SIZE = 8

#: Total wire size. Fixed forever.
SIZE = _FINGERPRINT_AT + _FINGERPRINT_SIZE


class PreambleError(Enum):
    """Why a peer's preamble was not accepted.

    Three distinct diagnoses, kept apart because they send an operator to three
    different places: the wrong protocol entirely, a peer built against a newer
    framework, or two builds of the same framework from different schemas.
    """

    NONE = "none"
    BAD_MAGIC = "bad_magic"
    BAD_VERSION = "bad_version"
    FINGERPRINT_MISMATCH = "fingerprint_mismatch"


class SchemaMismatch(RuntimeError):
    """Raised when a peer's wire contract is not the one this client speaks.

    Carries both fingerprints, because the useful question after a mismatch is
    always "which side is stale", and that is answered by comparing the values
    against what each end was generated from.
    """

    def __init__(self, error: PreambleError, expected: int, actual: Optional[int]):
        self.error = error
        self.expected = expected
        self.actual = actual

        if error is PreambleError.BAD_MAGIC:
            detail = (
                "the peer did not send an etask preamble - it may be speaking a "
                "different protocol, or a build older than the handshake"
            )
        elif error is PreambleError.BAD_VERSION:
            detail = (
                "the peer's preamble format is a version this client does not "
                "know - upgrade the client"
            )
        else:
            detail = (
                f"the peer was generated from a different schema: it speaks "
                f"{actual:016x}, this client speaks {expected:016x}. Regenerate "
                f"one side against the other's schema.yaml"
            )

        super().__init__(f"schema handshake failed ({error.value}): {detail}")


def encode(fingerprint: int) -> bytes:
    """Builds this peer's preamble.

    @param fingerprint The eight-byte schema fingerprint, as an unsigned int.
    @return The fourteen bytes to write to the transport, before any framing.
    """
    return (
        MAGIC
        + bytes((VERSION, RESERVED))
        + fingerprint.to_bytes(_FINGERPRINT_SIZE, "big")
    )


def decode(raw: bytes, expected: int) -> Tuple[PreambleError, Optional[int]]:
    """Checks a peer's preamble against the contract this client speaks.

    Checks run in order - magic, then version, then fingerprint - and stop at
    the first failure. The peer's fingerprint is returned **only** once the
    magic and version are known good: eight bytes read out of something that is
    not a preamble are a random number that reads like a real schema id, and
    reporting one sends an operator hunting for a schema that never existed.

    @param raw At least :data:`SIZE` bytes, starting at the magic.
    @param expected This client's own fingerprint.
    @return The diagnosis, and the peer's fingerprint when it could be trusted.
    """
    if len(raw) < SIZE or raw[_MAGIC_AT:_MAGIC_AT + len(MAGIC)] != MAGIC:
        return PreambleError.BAD_MAGIC, None

    if raw[_VERSION_AT] != VERSION:
        return PreambleError.BAD_VERSION, None

    peer = int.from_bytes(raw[_FINGERPRINT_AT:_FINGERPRINT_AT + _FINGERPRINT_SIZE], "big")
    if peer != expected:
        return PreambleError.FINGERPRINT_MISMATCH, peer

    return PreambleError.NONE, peer


def find(buffer: bytes) -> int:
    """Locates a preamble in a byte stream.

    The reader cannot assume the preamble is the first thing to arrive, which is
    what the magic is for. Returns the offset of a *complete* preamble only, so
    a caller can keep reading rather than parsing a partial one.

    @param buffer Bytes received so far.
    @return Offset of the first complete preamble, or -1 if none is present yet.
    """
    start = buffer.find(MAGIC)
    if start < 0 or len(buffer) - start < SIZE:
        return -1
    return start


def discardable(buffer: bytes) -> int:
    """How many leading bytes cannot begin a preamble, and may be dropped.

    Keeps a reader's buffer from growing without bound while it waits for a peer
    that may never speak, without discarding a partial magic that the next read
    would complete.

    @param buffer Bytes received so far.
    @return The number of leading bytes safe to discard.
    """
    start = buffer.find(MAGIC)
    if start >= 0:
        return start

    # No magic yet: everything but a possible partial prefix of it is dead.
    for keep in range(len(MAGIC) - 1, 0, -1):
        if buffer.endswith(MAGIC[:keep]):
            return len(buffer) - keep
    return len(buffer)
