# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
import asyncio
import ctypes
from typing import Optional, Tuple

import pytest

from comm.hub import Hub
from comm.interfaces.interface import Interface, InterfaceError
from comm.protocol import (
    BasicPacket,
    FramedPacket,
    Checksum,
    CRC32,
    INTERNET16,
    NONE,
    compute,
    PacketHeader,
    HeaderType,
    HeaderFlags,
    ETASK_BOARD_ID
)
from comm.protocol.packet_header import _PacketHeaderStructure

# -----------------------
# Helpers / fixtures
# -----------------------

WORD = ctypes.sizeof(ctypes.c_size_t)
HDR_SIZE = ctypes.sizeof(_PacketHeaderStructure)


def align_up(n: int, a: int) -> int:
    r = n % a
    return n if r == 0 else n + (a - r)


@pytest.fixture
def header_ok() -> PacketHeader:
    return PacketHeader.from_fields(
        type=HeaderType.DATA,
        encrypted=False,
        fragmented=False,
        priority=0,
        flags=HeaderFlags.NONE,
        validated=False,
        receiver_id=ETASK_BOARD_ID,
    )


@pytest.fixture
def header_other() -> PacketHeader:
    # Different receiver id => should be filtered out by Interface.try_receive
    return PacketHeader.from_fields(
        type=HeaderType.DATA,
        encrypted=False,
        fragmented=False,
        priority=0,
        flags=HeaderFlags.NONE,
        validated=False,
        receiver_id=(ETASK_BOARD_ID ^ 0x5A),
    )


# -----------------------
# Fake Interface
# -----------------------

class FakeInterface(Interface):
    """
    Minimal in-memory transport for testing Hub behavior.

    - Maintains an internal read buffer that `_recv_exact(n)` pulls from.
    - `feed_bytes(data, delay)` appends to the buffer (optionally after delay).
    - `_send_bytes` records last written bytes.
    - Opens on demand when read/write is requested.

    This *derives from Interface*, so it executes the real sealing/validation path.
    """

    def __init__(self, name: str = "fake") -> None:
        super().__init__()
        self.name = name
        self._open_flag = False
        self._read_buf = bytearray()
        self._read_event = asyncio.Event()

        self.open_calls = 0
        self.close_calls = 0
        self.send_calls = 0
        self.recv_calls = 0

        self.last_written: Optional[bytes] = None

    # lifecycle
    async def open(self) -> None:
        self.open_calls += 1
        self._open_flag = True

    async def close(self) -> None:
        self.close_calls += 1
        self._open_flag = False

    @property
    def is_open(self) -> bool:
        return self._open_flag

    # low-level IO
    async def _send_bytes(self, data: bytes) -> None:
        self.send_calls += 1
        if not self.is_open:
            await self.open()
        # emulate success
        self.last_written = bytes(data)

    async def _recv_exact(self, n: int) -> bytes:
        self.recv_calls += 1
        if not self.is_open:
            await self.open()

        # Await until we have >= n bytes
        while len(self._read_buf) < n:
            # reset+wait for producer
            self._read_event.clear()
            await self._read_event.wait()

        out = bytes(self._read_buf[:n])
        del self._read_buf[:n]
        return out

    # test control
    def feed_bytes(self, data: bytes) -> None:
        self._read_buf.extend(data)
        self._read_event.set()

    def feed_bytes_after(self, data: bytes, delay: float) -> None:
        async def _later():
            await asyncio.sleep(delay)
            self.feed_bytes(data)
        asyncio.create_task(_later())

    def clear_writes(self) -> None:
        self.last_written = None


# -----------------------
# Packet builders
# -----------------------

def make_basic(uid_type, header: PacketHeader, payload: bytes, extra: int = WORD) -> Tuple[BasicPacket, int]:
    min_size = HDR_SIZE + 1 + ctypes.sizeof(uid_type)
    pkt_size = align_up(min_size + len(payload) + extra, WORD)
    pkt = BasicPacket(packet_size=pkt_size, uid_type=uid_type, header=header, task_id=3, payload=payload)
    return pkt, pkt_size


def make_framed(uid_type, policy: Checksum, header: PacketHeader, payload: bytes, extra: int = WORD) -> Tuple[FramedPacket, int]:
    min_size = HDR_SIZE + 1 + ctypes.sizeof(uid_type) + policy.size
    pkt_size = align_up(min_size + len(payload) + extra, WORD)
    pkt = FramedPacket(packet_size=pkt_size, uid_type=uid_type, policy=policy,
                       header=header, task_id=7, payload=payload)
    return pkt, pkt_size


# -----------------------
# Tests
# -----------------------

@pytest.mark.asyncio
async def test_hub_open_close_all() -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])

    await hub.open_all()
    assert a.is_open and b.is_open
    assert a.open_calls == 1 and b.open_calls == 1

    await hub.close_all()
    assert not a.is_open and not b.is_open
    assert a.close_calls == 1 and b.close_calls == 1


@pytest.mark.asyncio
async def test_send_basic_to_all_enabled(header_ok) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    uid = ctypes.c_uint8
    pkt, _ = make_basic(uid, header_ok, b"X")

    await hub.send(pkt)
    assert a.last_written == bytes(pkt)
    assert b.last_written == bytes(pkt)
    assert a.send_calls == 1 and b.send_calls == 1

    await hub.close_all()


@pytest.mark.asyncio
async def test_disable_sender_excludes_that_interface(header_ok) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    hub.disable_sender(a)

    uid = ctypes.c_uint8
    pkt, _ = make_basic(uid, header_ok, b"Y")

    await hub.send(pkt)
    assert a.last_written is None
    assert b.last_written == bytes(pkt)
    assert a.send_calls == 0 and b.send_calls == 1

    await hub.close_all()


@pytest.mark.asyncio
async def test_send_framed_crc32_is_sealed_before_send(header_ok) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    uid = ctypes.c_uint8
    fp, _ = make_framed(uid, CRC32, header_ok, b"HELLO")
    # not sealed yet with expected CRC (we’ll compute expected)
    cut = fp.packet_size - CRC32.size
    expected = compute(CRC32, bytes(fp)[:cut])

    await hub.send(fp)  # should seal inside Interface.send/Validator
    assert fp.fcs == expected
    assert a.last_written == bytes(fp)
    assert b.last_written == bytes(fp)

    await hub.close_all()


@pytest.mark.asyncio
async def test_try_receive_basic_first_ready_wins(header_ok) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    uid = ctypes.c_uint8
    pkt_a, size_a = make_basic(uid, header_ok, b"A")
    pkt_b, size_b = make_basic(uid, header_ok, b"B")

    # Feed B later so A wins
    a.feed_bytes(bytes(pkt_a))
    b.feed_bytes_after(bytes(pkt_b), 0.05)

    got = await hub.try_receive(BasicPacket, packet_size=size_a, uid_type=uid)
    assert got is not None
    assert isinstance(got, BasicPacket)
    assert bytes(got) == bytes(pkt_a)

    await hub.close_all()


@pytest.mark.asyncio
async def test_try_receive_race_invalid_framed_vs_valid(header_ok) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    uid = ctypes.c_uint8
    # GOOD packet for B
    good, size = make_framed(uid, INTERNET16, header_ok, b"\x01\x02\x03")
    cut = good.packet_size - INTERNET16.size
    good.fcs = compute(INTERNET16, bytes(good)[:cut])

    # INVALID for A: copy and corrupt payload after sealing
    bad_raw = bytearray(bytes(good))
    # payload starts at HDR_SIZE + 1 + sizeof(uid) = 4 + 1 + 1 = 6 for uint8 uid
    bad_raw[HDR_SIZE + 1 + ctypes.sizeof(uid)] ^= 0xFF

    a.feed_bytes(bytes(bad_raw))
    b.feed_bytes_after(bytes(good), 0.01)

    got = await hub.try_receive(FramedPacket, packet_size=size, uid_type=uid, policy=INTERNET16)
    assert got is not None
    assert isinstance(got, FramedPacket)
    assert bytes(got) == bytes(good)

    await hub.close_all()


@pytest.mark.asyncio
async def test_try_receive_none_policy_skips_validation(header_ok) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    uid = ctypes.c_uint16
    fp, size = make_framed(uid, NONE, header_ok, b"\x10\x20")
    # No FCS field; validator treats as always valid
    a.feed_bytes(bytes(fp))

    got = await hub.try_receive(FramedPacket, packet_size=size, uid_type=uid, policy=NONE)
    assert got is not None
    assert isinstance(got, FramedPacket)
    assert got.policy is NONE
    assert bytes(got) == bytes(fp)

    await hub.close_all()


@pytest.mark.asyncio
async def test_board_filter_returns_none(header_other) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    uid = ctypes.c_uint8
    pkt, size = make_basic(uid, header_other, b"Z")
    a.feed_bytes(bytes(pkt))
    b.feed_bytes(bytes(pkt))

    got = await hub.try_receive(BasicPacket, packet_size=size, uid_type=uid)
    assert got is None

    await hub.close_all()


@pytest.mark.asyncio
async def test_enable_disable_receiver() -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")
    hub = Hub([a, b])
    await hub.open_all()

    # Only A is a receiver
    hub.disable_receiver(b)

    uid = ctypes.c_uint8
    # Valid for board
    hdr = PacketHeader.from_fields(
        type=HeaderType.DATA, encrypted=False, fragmented=False,
        priority=0, flags=HeaderFlags.NONE, validated=False, receiver_id=ETASK_BOARD_ID
    )
    pkt, size = make_basic(uid, hdr, b"RX")
    a.feed_bytes(bytes(pkt))

    got = await hub.try_receive(BasicPacket, packet_size=size, uid_type=uid)
    assert got is not None
    assert bytes(got) == bytes(pkt)

    await hub.close_all()


@pytest.mark.asyncio
async def test_context_manager_opens_and_closes(header_ok) -> None:
    a = FakeInterface("A")
    b = FakeInterface("B")

    async with Hub([a, b]) as hub:
        assert a.is_open and b.is_open
        uid = ctypes.c_uint8
        pkt, _ = make_basic(uid, header_ok, b"CM")
        await hub.send(pkt)
        assert a.last_written == bytes(pkt)
        assert b.last_written == bytes(pkt)

    # After exit, both closed
    assert not a.is_open and not b.is_open
