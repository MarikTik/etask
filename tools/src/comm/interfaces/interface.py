# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Async base transport + unified async try_receive for BasicPacket / FramedPacket.

Key points
----------
- A single `try_receive(...)` accepts the target packet *type* and size/uid_type,
  and (optionally) policy for framed packets. It reads exactly one frame,
  decodes to a packet, filters by receiver_id, and runs Validator.is_valid.
- No timeouts; `try_receive` awaits until a full frame arrives or the task is cancelled.
- Persistent connection: concrete transports keep handles open; reconnect on demand.
"""

from __future__ import annotations
from abc import abstractmethod, ABC
import ctypes
from typing import Optional, Type, Union, cast

from ..protocol.packet_header import (
    ETASK_BOARD_ID,
    _PacketHeaderStructure,
    PacketHeader,
)
from comm.protocol import BasicPacket, FramedPacket, Checksum, Validator

Packet = BasicPacket | FramedPacket


# ---- layout helpers --------------------------------------------------------

def _basic_min(uid_type: Type[ctypes._SimpleCData]) -> int:
    return ctypes.sizeof(_PacketHeaderStructure) + 1 + ctypes.sizeof(uid_type)

def _framed_min(uid_type: Type[ctypes._SimpleCData], policy: Checksum) -> int:
    return ctypes.sizeof(_PacketHeaderStructure) + 1 + ctypes.sizeof(uid_type) + int(policy.size)


# ---- exact decode without parsing (overwrite ctypes struct with wire image) -

def _decode_basic_from_bytes(data: bytes, uid_type: Type[ctypes._SimpleCData]) -> BasicPacket:
    dummy_hdr = PacketHeader(raw_value=0, receiver_id=1)
    pkt = BasicPacket(
        packet_size=len(data),
        uid_type=uid_type,
        header=dummy_hdr,
        task_id=0,
        status_code=0,
        payload=b"",
    )
    ctypes.memmove(ctypes.addressof(pkt._c), data, len(data))
    return pkt

def _decode_framed_from_bytes(
    data: bytes,
    uid_type: Type[ctypes._SimpleCData],
    policy: Checksum,
) -> FramedPacket:
    dummy_hdr = PacketHeader(raw_value=0, receiver_id=1)
    pkt = FramedPacket(
        packet_size=len(data),
        uid_type=uid_type,
        policy=policy,
        header=dummy_hdr,
        task_id=0,
        status_code=0,
        payload=b"",
        fcs=0 if policy.size else None,
    )
    ctypes.memmove(ctypes.addressof(pkt._c), data, len(data))
    return pkt


# ---- async base ------------------------------------------------------------

class InterfaceError(Exception):
    """Transport-level error (connect/read/write)."""


class Interface(ABC):
    """
    Async base for persistent transports.

    Subclasses must implement:
        - async open()
        - async close()
        - is_open -> bool
        - async _send_bytes(data: bytes) -> None
        - async _recv_exact(n: int) -> bytes  # await until n bytes or raise

    Public API:
        - async send(packet) -> None  (seals FramedPacket via Validator)
        - async try_receive(packet_type, packet_size, uid_type, policy=None) -> Packet|None
    """

    def __init__(self) -> None:
        self._validator = Validator()

    # -- lifecycle -----------------------------------------------------------

    @abstractmethod
    async def open(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @property
    @abstractmethod
    def is_open(self) -> bool: ...

    # -- raw I/O -------------------------------------------------------------

    @abstractmethod
    async def _send_bytes(self, data: bytes) -> None: ...

    @abstractmethod
    async def _recv_exact(self, n: int) -> bytes:
        """
        Await exactly n bytes from the transport.
        Should raise InterfaceError on transport failure.
        No timeouts - rely on cancellation to abort.
        """

    # -- high-level ----------------------------------------------------------

    async def send(self, packet: Packet) -> None:
        """Seal framed packets and write to the transport."""
        if isinstance(packet, FramedPacket):
            self._validator.seal(packet)
        await self._send_bytes(bytes(packet))

    async def try_receive(
        self,
        packet_type: Type[Packet],
        packet_size: int,
        uid_type: Type[ctypes._SimpleCData],
        policy: Optional[Checksum] = None,
    ) -> Optional[Packet]:
        """
        Unified async receive:
          - reads exactly `packet_size` bytes (awaits indefinitely)
          - decodes to the given packet_type (BasicPacket or FramedPacket)
          - filters by receiver_id (must match ETASK_BOARD_ID)
          - validates via Validator (framed -> checksum, basic -> True)
        Returns None only if validation/board-id fails. Transport errors raise.
        """
        # Basic size sanity (mirror C++ static asserts)
        if packet_type is BasicPacket:
            if packet_size < _basic_min(uid_type):
                raise ValueError("packet_size smaller than minimum BasicPacket layout")
        elif packet_type is FramedPacket:
            if policy is None:
                raise ValueError("policy must be provided for FramedPacket")
            if packet_size < _framed_min(uid_type, policy):
                raise ValueError("packet_size smaller than minimum FramedPacket layout")
        else:
            raise TypeError(f"Unsupported packet type: {packet_type!r}")

        raw = await self._recv_exact(packet_size)

        # Decode into packet object without parsing fields
        if packet_type is BasicPacket:
            pkt = _decode_basic_from_bytes(raw, uid_type)
        else:  # FramedPacket
            pkt = _decode_framed_from_bytes(raw, uid_type, cast(Checksum, policy))

        # Board id filter
        if pkt.header.receiver_id != ETASK_BOARD_ID:
            return None

        # Validate via shared validator pipeline
        if not self._validator.is_valid(pkt):
            return None

        return pkt
