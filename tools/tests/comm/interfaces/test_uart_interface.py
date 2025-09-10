import ctypes
import pytest
from typing import Tuple, Dict
from comm.interfaces import UARTInterface, InterfaceError
from comm.protocol import (
    BasicPacket, 
    FramedPacket, 
    CRC32,
    compute, 
    PacketHeader, 
    HeaderType, 
    HeaderFlags, 
    ETASK_BOARD_ID
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
def mk_uart(monkeypatch) -> Tuple[FakeStreamReader, FakeStreamWriter, Dict[str, int]]:
    """Monkeypatch serial_asyncio.open_serial_connection to fake reader/writer."""
    reader = FakeStreamReader()
    writer = FakeStreamWriter()
    calls = {"opens": 0}

    async def fake_open_serial_connection(url, baudrate) -> Tuple[FakeStreamReader, FakeStreamWriter]:
        calls["opens"] += 1
        return reader, writer

    monkeypatch.setattr("serial_asyncio.open_serial_connection", fake_open_serial_connection)
    return reader, writer, calls


@pytest.mark.asyncio
async def test_uart_send_and_receive_basic(mk_uart, header_ok) -> None:
    reader, writer, calls = mk_uart
    iface = UARTInterface("/dev/ttyFAKE", 115200)
    await iface.open()
    assert calls["opens"] == 1

    uid = ctypes.c_uint8
    pkt = BasicPacket(packet_size=16, uid_type=uid, header=header_ok, task_id=9, payload=b"X")
    await iface.send(pkt)
    assert bytes(writer.buffer) == bytes(pkt)

    # loopback read
    reader.feed_data(bytes(pkt))
    got = await iface.try_receive(BasicPacket, packet_size=16, uid_type=uid)
    assert got is not None
    assert bytes(got) == bytes(pkt)

    await iface.close()


@pytest.mark.asyncio
async def test_uart_send_seals_framed_crc32(mk_uart, header_ok) -> None:
    reader, writer, _ = mk_uart
    iface = UARTInterface("/dev/ttyFAKE", 115200)
    await iface.open()

    uid = ctypes.c_uint16
    pkt = FramedPacket(packet_size=32, uid_type=uid, policy=CRC32,
                       header=header_ok, task_id=0x1234, payload=b"UART!")
    end = pkt.packet_size - CRC32.size
    expected = compute(CRC32, bytes(pkt)[:end])

    await iface.send(pkt)
    assert pkt.fcs == expected
    assert bytes(writer.buffer) == bytes(pkt)

    await iface.close()


@pytest.mark.asyncio
async def test_uart_reopen_on_demand(mk_uart, header_ok) -> None:
    reader, writer, calls = mk_uart
    iface = UARTInterface("/dev/ttyFAKE", 115200)
    await iface.open()
    assert calls["opens"] == 1
    await iface.close()

    # next receive should reopen
    uid = ctypes.c_uint8
    pkt = BasicPacket(packet_size=16, uid_type=uid, header=header_ok, task_id=1, payload=b"")
    reader.feed_data(bytes(pkt))
    got = await iface.try_receive(BasicPacket, packet_size=16, uid_type=uid)
    assert got is not None
    assert calls["opens"] == 2
