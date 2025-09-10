import asyncio
import ctypes
import pytest
from typing import Tuple, Dict
from comm.interfaces import WiFiInterface, InterfaceError
from comm.protocol import (
    BasicPacket, 
    FramedPacket, 
    CRC32,
    INTERNET16,
    compute, 
    PacketHeader, 
    HeaderType, 
    HeaderFlags, 
    ETASK_BOARD_ID,
    NONE
)

from fakes import FakeStreamReader, FakeStreamWriter


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
def mk_wifi(monkeypatch) -> Tuple[object, object, Dict]:
    calls = {"connects": 0}
    last = {"reader": None, "writer": None}

    class LastRef:
        """Proxy to always reflect the most-recent reader/writer."""
        def __init__(self, store: dict, key: str):
            self._store = store
            self._key = key

        def __getattr__(self, name):
            obj = self._store[self._key]
            if obj is None:
                raise RuntimeError(f"{self._key} not created yet")
            return getattr(obj, name)

        # If a test needs the underlying object explicitly:
        @property
        def _obj(self):
            return self._store[self._key]

    async def fake_open_connection(host, port):
        calls["connects"] += 1
        r, w = FakeStreamReader(), FakeStreamWriter()
        last["reader"], last["writer"] = r, w
        return r, w

    # Patch the actual function used by WiFiInterface
    monkeypatch.setattr(asyncio, "open_connection", fake_open_connection)

    # Return proxies (reader_proxy, writer_proxy) and the calls dict
    return LastRef(last, "reader"), LastRef(last, "writer"), calls

@pytest.mark.asyncio
async def test_wifi_send_seals_framed_crc32(mk_wifi, header_ok) -> None:
    reader, writer, calls = mk_wifi
    iface = WiFiInterface("127.0.0.1", 9999)
    await iface.open()
    assert calls["connects"] == 1

    uid = ctypes.c_uint8
    pkt = FramedPacket(packet_size=32, uid_type=uid, policy=CRC32,
                       header=header_ok, task_id=7, payload=b"HELLO")
    # Before sending, FCS not set to expected
    end = pkt.packet_size - CRC32.size
    expected = compute(CRC32, bytes(pkt)[:end])

    await iface.send(pkt)   # must seal + write
    # After send, FCS should match
    assert pkt.fcs == expected
    assert bytes(pkt) == bytes(writer.buffer)

    await iface.close()


@pytest.mark.asyncio
async def test_wifi_try_receive_basic_ok(mk_wifi, header_ok) -> None:
    reader, writer, calls = mk_wifi
    iface = WiFiInterface("127.0.0.1", 9999)
    await iface.open()

    uid = ctypes.c_uint8
    pkt = BasicPacket(packet_size=16, uid_type=uid, header=header_ok, task_id=3, payload=b"\xAA")
    # feed wire image
    reader.feed_data(bytes(pkt))

    got = await iface.try_receive(BasicPacket, packet_size=16, uid_type=uid)
    assert got is not None
    assert isinstance(got, BasicPacket)
    assert bytes(got) == bytes(pkt)

    await iface.close()


@pytest.mark.asyncio
async def test_wifi_try_receive_framed_invalid_checksum_returns_none(mk_wifi, header_ok) -> None:
    reader, writer, _ = mk_wifi
    iface = WiFiInterface("127.0.0.1", 9999)
    await iface.open()

    uid = ctypes.c_uint8
    good = FramedPacket(packet_size=24, uid_type=uid, policy=INTERNET16,
                        header=header_ok, task_id=9, payload=b"\x01\x02\x03")
    # Intentionally corrupt one byte in the payload after sealing to break FCS.
    # Seal by sending through validator via the interface (or compute directly):
    end = good.packet_size - INTERNET16.size
    good.fcs = compute(INTERNET16, bytes(good)[:end])

    raw = bytearray(bytes(good))
    # Flip a payload byte (header:4, status:1, task:1 => payload starts at 6)
    raw[6] ^= 0xFF

    reader.feed_data(bytes(raw))
    got = await iface.try_receive(FramedPacket, packet_size=24, uid_type=uid, policy=INTERNET16)
    assert got is None

    await iface.close()


@pytest.mark.asyncio
async def test_wifi_try_receive_framed_none_policy_skips_validation(mk_wifi, header_ok) -> None:
    reader, writer, _ = mk_wifi
    iface = WiFiInterface("127.0.0.1", 9999)
    await iface.open()

    uid = ctypes.c_uint16
    pkt = FramedPacket(packet_size=24, uid_type=uid, policy=NONE,
                       header=header_ok, task_id=55, payload=b"\x11\x22")
    # No FCS field; validator treats as always valid
    reader.feed_data(bytes(pkt))
    got = await iface.try_receive(FramedPacket, packet_size=24, uid_type=uid, policy=NONE)
    assert got is not None
    assert isinstance(got, FramedPacket)
    assert got.policy is NONE
    assert bytes(got) == bytes(pkt)

    await iface.close()


@pytest.mark.asyncio
async def test_wifi_board_filter_returns_none(mk_wifi) -> None:
    reader, writer, _ = mk_wifi
    iface = WiFiInterface("127.0.0.1", 9999)
    await iface.open()

    # Build header for another receiver
    hdr = PacketHeader.from_fields(
        type=HeaderType.DATA, encrypted=False, fragmented=False,
        priority=0, flags=HeaderFlags.NONE, validated=False, receiver_id=ETASK_BOARD_ID ^ 0x7F
    )
    pkt = BasicPacket(packet_size=16, uid_type=ctypes.c_uint8, header=hdr, task_id=1, payload=b"")

    reader.feed_data(bytes(pkt))
    got = await iface.try_receive(BasicPacket, packet_size=16, uid_type=ctypes.c_uint8)
    assert got is None

    await iface.close()


@pytest.mark.asyncio
async def test_wifi_reopen_on_next_call_after_close(mk_wifi, header_ok) -> None:
    reader, writer, calls = mk_wifi
    iface = WiFiInterface("127.0.0.1", 9999)
    await iface.open()
    assert calls["connects"] == 1
    await iface.close()

    pkt = BasicPacket(packet_size=16, uid_type=ctypes.c_uint8, header=header_ok, task_id=2, payload=b"")
    await iface.send(pkt)   # should trigger a second fresh connect
    assert calls["connects"] == 2