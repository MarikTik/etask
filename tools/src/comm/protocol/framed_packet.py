# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
FramedPacket — full protocol packet with a trailing Frame Check Sequence (FCS).

This mirrors the C++ template:

    template<std::size_t PacketSize, typename TaskID_t, typename Checksum>
    struct framed_packet;

Key runtime parameters:
- packet_size (int): total bytes including header, status, task_id, payload, and FCS.
- uid_type (ctypes type): task id field type (resolved from your schema.task_uid_type).
- policy (Checksum): layout-only description of the FCS field (size, ctype).

Layout (packed, byte-for-byte):
+-----------------------+---------------------+---------------------------+-----------------+------------------+
|      packet_header    |     status_code     |          task_id          |      payload    |       FCS        |
+-----------------------+---------------------+---------------------------+-----------------+------------------+
| sizeof(packet_header) |       1 byte        | sizeof(TaskID_t [ctype])  |   payload_size  | policy.size      |
+-----------------------+---------------------+---------------------------+-----------------+------------------+

Where:
    payload_size = packet_size - sizeof(packet_header) - 1 - sizeof(TaskID_t) - policy.size

Notes:
- This class does NOT validate frame correctness nor verify FCS. It only shapes
  the memory layout and enforces simple size/overflow constraints (akin to C++
  `static_assert`s for minimum size and alignment).
- FCS computation is intentionally left to a separate engine (analogous to C++ `compute.hpp`).

Author: Mark Tikhonov <mtik.philosopher@gmail.com>
"""

import ctypes
from typing import Optional, Type

from .packet_header import PacketHeader, _PacketHeaderStructure
from .checksum import Checksum, NONE


class FramedPacket:
    """
    Fixed-size, packed framed packet with trailing FCS field.

    Args:
        packet_size (int):
            Total packet size in bytes. Must be word-aligned (multiple of sizeof(size_t)).
        uid_type (Type[ctypes._SimpleCData]):
            Task ID field type (e.g., c_uint8 / c_uint16 / c_uint32 / c_uint64).
        policy (Checksum):
            Layout descriptor of the FCS field (size, ctype). Use checksum_policy.NONE for no FCS.
        header (PacketHeader):
            Packet header object (copied byte-for-byte).
        task_id (int):
            Task identifier value; must fit into uid_type.
        status_code (int, optional):
            Status/errno (0..255). Default: 0.
        payload (bytes/bytearray/memoryview, optional):
            Initial payload contents; length must be <= payload_size.
        fcs (int | bytes | None, optional):
            Initial FCS value. If policy.size==0, this is ignored. If bytes, must match
            policy.size. If int, must fit in the policy ctype.

    Raises:
        ValueError on size/alignment/overflow issues.
    """

    __slots__ = (
        "packet_size", "task_id_ctype", "header_size",
        "task_id_size", "payload_size", "policy",
        "_Structure", "_c"
    )

    def __init__(
        self,
        packet_size: int,
        uid_type: Type[ctypes._SimpleCData],
        policy: Checksum,
        *,
        header: PacketHeader,
        task_id: int,
        status_code: int = 0,
        payload: bytes | bytearray | memoryview | None = None,
        fcs: int | bytes | None = None,
    ) -> None:
        # --- Sizes, alignment (C++ static_assert equivalents) ---
        hdr_size = ctypes.sizeof(_PacketHeaderStructure)  # 4 bytes (packed)
        tid_size = ctypes.sizeof(uid_type)
        fcs_size = int(policy.size)
        min_size = hdr_size + 1 + tid_size + fcs_size

        if packet_size < min_size:
            raise ValueError(
                f"packet_size={packet_size} too small; minimum is {min_size} "
                f"(header={hdr_size}, status=1, task_id={tid_size}, fcs={fcs_size})."
            )

        word = ctypes.sizeof(ctypes.c_size_t)
        if packet_size % word != 0:
            raise ValueError(
                f"packet_size must be word-aligned (multiple of {word}); got {packet_size}."
            )

        pl_size = packet_size - min_size

        # --- Store "constexpr" fields ---
        self.packet_size = int(packet_size)
        self.task_id_ctype = uid_type
        self.header_size = hdr_size
        self.task_id_size = tid_size
        self.payload_size = pl_size
        self.policy = policy

        # --- Build packed structure for THIS instantiation ---
        fields = [
            ("header", _PacketHeaderStructure),
            ("status_code", ctypes.c_uint8),
            ("task_id", uid_type),
            ("payload", ctypes.c_ubyte * pl_size),
        ]
        if fcs_size > 0:
            fields.append(("fcs", policy.ctype))

        self._Structure = type(
            "_FramedPacket_struct",
            (ctypes.Structure,),
            {"_pack_": 1, "_fields_": fields},
        )

        # --- Construct object ---
        self._c = self._Structure()

        # header
        hdr_bytes = header.to_bytes()
        if len(hdr_bytes) != self.header_size:
            raise ValueError("Invalid header byte length.")
        ctypes.memmove(ctypes.addressof(self._c.header), hdr_bytes, self.header_size)

        # status_code
        if not 0 <= int(status_code) <= 0xFF:
            raise ValueError("status_code must be 0..255.")
        self._c.status_code = int(status_code)

        # task_id (narrow to uid_type)
        max_task_val = (1 << (8 * self.task_id_size)) - 1
        if not 0 <= int(task_id) <= max_task_val:
            raise ValueError(f"task_id must fit into {self.task_id_size} bytes unsigned.")
        self._c.task_id = int(task_id)

        # payload
        if payload is not None:
            data = bytes(payload)
            n = len(data)
            if n > self.payload_size:
                raise ValueError(f"payload too large ({n} > {self.payload_size}).")
            if n:
                ctypes.memmove(self._c.payload, data, n)

        # fcs (optional initialization)
        if fcs_size > 0 and fcs is not None:
            if isinstance(fcs, (bytes, bytearray, memoryview)):
                b = bytes(fcs)
                if len(b) != fcs_size:
                    raise ValueError(f"fcs byte length must be exactly {fcs_size}.")
                # Interpret as little-endian integer consistently
                self._set_fcs_int(int.from_bytes(b, "little"))
            else:
                self._set_fcs_int(int(fcs))

    # --- Properties (struct-like) ---

    @property
    def header(self) -> PacketHeader:
        return PacketHeader(raw_value=self._c.header.space, receiver_id=self._c.header.receiver_id)

    @property
    def status_code(self) -> int:
        return int(self._c.status_code)

    @status_code.setter
    def status_code(self, v: int) -> None:
        if not 0 <= int(v) <= 0xFF:
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

    @property
    def fcs(self) -> Optional[int]:
        """Return current FCS as int (None if policy.size==0)."""
        if self.policy.size == 0:
            return None
        # self._c has attribute 'fcs' only when size > 0
        f = getattr(self._c, "fcs", None)
        if f is None:
            return None
        return int(f.value) if hasattr(f, "value") else int(f)

    @fcs.setter
    def fcs(self, value: int | bytes | bytearray | memoryview) -> None:
        if self.policy.size == 0:
            raise ValueError("Checksum policy is NONE; no FCS field to set.")
        if isinstance(value, (bytes, bytearray, memoryview)):
            b = bytes(value)
            if len(b) != self.policy.size:
                raise ValueError(f"fcs byte length must be exactly {self.policy.size}.")
            self._set_fcs_int(int.from_bytes(b, "little"))
        else:
            self._set_fcs_int(int(value))

    def _set_fcs_int(self, v: int) -> None:
        """Internal: write integer FCS respecting the policy ctype width."""
        if self.policy.size == 0:
            return
        max_val = (1 << (8 * self.policy.size)) - 1
        if not 0 <= v <= max_val:
            raise ValueError(f"fcs must fit into {self.policy.size} bytes unsigned.")
        setattr(self._c, "fcs", v)

    # --- Bytes & repr ---

    def to_bytes(self) -> bytes:
        """Exact wire image of the whole frame (packet_size bytes)."""
        return bytes(self._c)

    def __bytes__(self) -> bytes:
        return self.to_bytes()

    def __repr__(self) -> str:
        return (
            f"FramedPacket(packet_size={self.packet_size}, "
            f"task_id_ctype={self.task_id_ctype.__name__}, "
            f"policy={self.policy.name}, header={self.header!r}, "
            f"status_code={self.status_code}, task_id={self.task_id}, "
            f"payload_size={self.payload_size}, fcs={self.fcs})"
        )
