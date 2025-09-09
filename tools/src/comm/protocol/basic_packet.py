# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Fixed-size BasicPacket (C++-faithful) for the etask communication protocol.

This Python implementation mirrors the C++ template:

    template<std::size_t PacketSize, typename TaskID_t>
    struct basic_packet;

Key points:
- `PacketSize` (int) is given at construction time.
- `uid_type` (ctypes type: c_uint8, c_uint16, c_uint32, or c_uint64) must
  be provided. This is resolved once from the active schema implementation
  (`schema.task_uid_type`) and then reused when creating packets.
- Payload size is automatically deduced:
      payload_size = PacketSize - sizeof(packet_header) - sizeof(uint8_t status_code) - sizeof(TaskID_t)
- Layout is byte-for-byte identical to the C++ struct with `#pragma pack(1)`.

Packet layout:
+-----------------------+---------------------+---------------------------+-----------------+
|      packet_header    |     status_code     |          task_id          |      payload    |
+-----------------------+---------------------+---------------------------+-----------------+
| sizeof(packet_header) |       1 byte        | sizeof(TaskID_t [ctype])  |   payload_size  |
+-----------------------+---------------------+---------------------------+-----------------+

Constructor overloads (mirroring C++):
1) BasicPacket(packet_size, uid_type, header, task_id, status_code=0)
2) BasicPacket(packet_size, uid_type, header, task_id, status_code=0, payload=b"...")

Author: Mark Tikhonov <mtik.philosopher@gmail.com>
"""

import ctypes
from typing import Type

from .packet_header import (
    PacketHeader,
    _PacketHeaderStructure,
)


class BasicPacket:
    """
    Core fixed-size packet structure without checksum framing.

    Args:
        packet_size (int):
            Total packet size in bytes. Must be word-aligned (multiple of sizeof(size_t)).
        uid_type (Type[ctypes._SimpleCData]):
            The TaskID type resolved from schema.task_uid_type
            (c_uint8, c_uint16, c_uint32, or c_uint64).
        header (PacketHeader):
            A PacketHeader object with routing/metadata.
        task_id (int):
            Task identifier (must fit in uid_type's range).
        status_code (int, optional):
            Status or error code. Default = 0.
        payload (bytes/bytearray/memoryview, optional):
            Initial payload contents. Must not exceed payload_size.

    Raises:
        ValueError if packet_size is too small, not aligned, or if fields are out of range.
    """

    __slots__ = ("packet_size", "task_id_ctype", "header_size",
                 "task_id_size", "payload_size", "_Structure", "_c")

    def __init__(
        self,
        packet_size: int,
        uid_type: Type[ctypes._SimpleCData],
        *,
        header: PacketHeader,
        task_id: int,
        status_code: int = 0,
        payload: bytes | bytearray | memoryview | None = None,
    ) -> None:
        # ---- Compute & validate sizes (equivalent to C++ static_asserts) ----
        hdr_size = ctypes.sizeof(_PacketHeaderStructure)  # 4 bytes packed
        tid_size = ctypes.sizeof(uid_type)
        min_size = hdr_size + 1 + tid_size

        if packet_size < min_size:
            raise ValueError(
                f"packet_size={packet_size} too small; minimum is {min_size} "
                f"(header={hdr_size}, status=1, task_id={tid_size})."
            )

        word = ctypes.sizeof(ctypes.c_size_t)
        if packet_size % word != 0:
            raise ValueError(
                f"packet_size must be word-aligned (multiple of {word}); got {packet_size}."
            )

        pl_size = packet_size - min_size

        # ---- Store constants ----
        self.packet_size = int(packet_size)
        self.task_id_ctype = uid_type
        self.header_size = hdr_size
        self.task_id_size = tid_size
        self.payload_size = pl_size

        # ---- Define exact packed layout for THIS instantiation ----
        self._Structure = type(
            "_BasicPacket_struct",
            (ctypes.Structure,),
            {
                "_pack_": 1,
                "_fields_": [
                    ("header", _PacketHeaderStructure),
                    ("status_code", ctypes.c_uint8),
                    ("task_id", uid_type),
                    ("payload", ctypes.c_ubyte * pl_size),
                ],
            },
        )

        # ---- Construct (covers both C++ ctors) ----
        self._c = self._Structure()

        # Header
        hdr_bytes = header.to_bytes()
        if len(hdr_bytes) != self.header_size:
            raise ValueError("Invalid header byte length.")
        ctypes.memmove(ctypes.addressof(self._c.header), hdr_bytes, self.header_size)

        # Status
        if not 0 <= int(status_code) <= 0xFF:
            raise ValueError("status_code must be 0..255.")
        self._c.status_code = int(status_code)

        # Task ID
        max_task_val = (1 << (8 * self.task_id_size)) - 1
        if not 0 <= int(task_id) <= max_task_val:
            raise ValueError(f"task_id must fit into {self.task_id_size} bytes unsigned.")
        self._c.task_id = int(task_id)

        # Payload
        if payload is not None:
            data = bytes(payload)
            n = len(data)
            if n > self.payload_size:
                raise ValueError(f"payload too large ({n} > {self.payload_size}).")
            if n:
                ctypes.memmove(self._c.payload, data, n)

    # ---- struct-like field access ----

    @property
    def header(self) -> PacketHeader:
        return PacketHeader(raw_value=self._c.header.space, receiver_id=self._c.header.receiver_id)

    @property
    def status_code(self) -> int:
        return int(self._c.status_code)

    @status_code.setter
    def status_code(self, v: int) -> None:
        if not 0 <= int(v) <= 0xff:
            raise ValueError("status_code must be 0..255.")
        self._c.status_code = int(v)

    @property
    def task_id(self) -> int:
        return int(self._c.task_id)

    @task_id.setter
    def task_id(self, v: int) -> None:
        max_task_val = (1 << (8 * self.task_id_size)) - 1
        if not 0 <= int(v) <= max_task_val:
            raise ValueError(f"task_id must fit into {self.task_id_size} bytes unsigned.")
        self._c.task_id = int(v)

    @property
    def payload(self) -> memoryview:
        """Zero-copy mutable view of payload region (cast to 'B' for writable byte view)."""
        mv = memoryview(self._c.payload)
        if mv.format != "B":  # ctypes may export '<B'
            mv = mv.cast("B")
        return mv

    # ---- bytes & repr ----

    def to_bytes(self) -> bytes:
        """Return the raw wire representation (PacketSize bytes)."""
        return bytes(self._c)

    def __bytes__(self) -> bytes:
        return self.to_bytes()

    def __repr__(self) -> str:
        return (f"BasicPacket(packet_size={self.packet_size}, task_id_ctype={self.task_id_ctype.__name__}, "
                f"header={self.header!r}, status_code={self.status_code}, task_id={self.task_id}, "
                f"payload_size={self.payload_size})")
