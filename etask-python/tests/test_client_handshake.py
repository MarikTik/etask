# tools/tests/test_client_handshake.py
# SPDX-License-Identifier: MIT

import asyncio

import pytest

from etask.client import Client
from etask.preamble import PreambleError, SchemaMismatch, encode

_FP = 0x71DD4EB1C4E0392D


class RawChannel:
    """A transport with the optional raw byte hooks the handshake needs."""

    def __init__(self, to_send: bytes = b"", *, chunk: int = 64):
        self.sent = bytearray()
        self._inbox = bytearray(to_send)
        self._chunk = chunk

    def send_raw(self, data: bytes) -> None:
        self.sent.extend(data)

    def read_raw(self, max_bytes: int) -> bytes:
        take = min(max_bytes, self._chunk, len(self._inbox))
        out = bytes(self._inbox[:take])
        del self._inbox[:take]
        return out

    def unread_raw(self, data: bytes) -> None:
        """Returns bytes the handshake over-read; a stream transport must."""
        self._inbox[:0] = data


class AsyncRawChannel(RawChannel):
    """The same, with coroutine hooks - both shapes must work."""

    async def send_raw(self, data: bytes) -> None:  # type: ignore[override]
        super().send_raw(data)

    async def read_raw(self, max_bytes: int) -> bytes:  # type: ignore[override]
        return super().read_raw(max_bytes)


class PacketOnlyChannel:
    """A transport predating the handshake: no raw path at all."""


def run(coro):
    """Drives a coroutine, matching test_client.py's no-pytest-asyncio style."""
    return asyncio.run(coro)


def client(channel, **kwargs):
    return Client(channel, uid_bytes=1, fingerprint=_FP, **kwargs)


# ------------------------------------------------------------------- success

def test_matching_device_completes_the_handshake():
    channel = RawChannel(encode(_FP))
    assert run(client(channel).handshake()) is True
    # Our own preamble went out first, unframed.
    assert bytes(channel.sent) == encode(_FP)


def test_works_with_async_transport_hooks():
    assert run(client(AsyncRawChannel(encode(_FP))).handshake()) is True


def test_finds_the_preamble_after_leading_noise():
    # A device may be mid-stream, or may open with traffic from a previous run.
    channel = RawChannel(b"\x00\xff garbage " + encode(_FP))
    assert run(client(channel).handshake()) is True


def test_reassembles_a_preamble_split_across_reads():
    # A byte-oriented link has no obligation to deliver fourteen bytes at once.
    channel = RawChannel(encode(_FP), chunk=3)
    assert run(client(channel).handshake()) is True


# ------------------------------------------------------------------ failure

def test_rejects_a_device_built_from_another_schema():
    other = 0xDEADBEEFCAFEBABE
    with pytest.raises(SchemaMismatch) as caught:
        run(client(RawChannel(encode(other))).handshake())

    assert caught.value.error is PreambleError.FINGERPRINT_MISMATCH
    assert caught.value.expected == _FP
    assert caught.value.actual == other
    # The message must name both, since the question is always which side is stale.
    assert f"{other:016x}" in str(caught.value)


def test_times_out_on_a_silent_device():
    with pytest.raises(SchemaMismatch) as caught:
        run(client(RawChannel(b"")).handshake(timeout=0.05))
    assert caught.value.error is PreambleError.BAD_MAGIC


def test_times_out_on_a_device_that_never_sends_a_preamble():
    # Bytes arriving that are not, and never become, a preamble.
    with pytest.raises(SchemaMismatch):
        run(client(RawChannel(b"noise" * 100)).handshake(timeout=0.05))


# ------------------------------------------------------------------- opt-out

def test_skips_when_no_fingerprint_was_given():
    channel = RawChannel(encode(_FP))
    unfingerprinted = Client(channel, uid_bytes=1)
    assert run(unfingerprinted.handshake()) is False
    assert bytes(channel.sent) == b""


def test_warns_and_skips_on_a_transport_without_raw_hooks():
    # An older transport must keep working rather than breaking on upgrade -
    # but silently losing the check would be worse, so it warns.
    with pytest.warns(RuntimeWarning, match="handshake skipped"):
        assert run(client(PacketOnlyChannel()).handshake()) is False


def test_does_not_consume_bytes_after_the_preamble():
    # Whatever follows the preamble is task traffic and belongs to the reader.
    trailing = b"\xAA\xBB\xCC"
    channel = RawChannel(encode(_FP) + trailing)
    run(client(channel).handshake())
    assert channel.read_raw(64) == trailing


class NoPushbackChannel(RawChannel):
    """A raw transport that cannot take bytes back."""

    unread_raw = None


def test_buffers_over_read_bytes_when_the_transport_cannot_take_them_back():
    # Without somewhere to put them these bytes would be silently dropped, and
    # on a stream transport they are the start of a real frame.
    trailing = b"\xAA\xBB\xCC"
    channel = NoPushbackChannel(encode(_FP) + trailing)
    c = client(channel)
    run(c.handshake())
    assert c._pending_raw == trailing
