# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Immutable packet packet_header definition for etask communication protocol.

This module provides a Python implementation of the C++ etask communication
protocol packet header, designed for interoperability. It uses the ctypes
library to ensure that the memory layout is identical to the C++ struct.

The packet header occupies 32 bits (4 bytes) and encodes metadata required
for packet routing, processing, and control.

Changelog:
- 2025-09-02
    - Initial Python implementation mirroring the C++ version.
"""

import ctypes
from enum import IntEnum, IntFlag

# =============================================================================
# Configuration Constants
# =============================================================================
# These values should be configured to match the settings in your C++ project's
# `config.hpp` file to ensure protocol compatibility.

#: Protocol version is locked to ensure consistency. 
#TODO: Move it to a global file definition via CMakeLists version control. 
ETASK_PROTOCOL_VERSION = 1

#: Sender ID is locked to ensure a consistent board ID.
ETASK_BOARD_ID = 10


# =============================================================================
# Enumerations
# =============================================================================

class HeaderType(IntEnum):
    """Enumerates the different types of packet headers used in the protocol."""
    DATA       = 0x0  #: Generic application data packet
    CONFIG     = 0x1  #: Configuration or parameter change
    CONTROL    = 0x2  #: Protocol-level commands
    ROUTING    = 0x3  #: Routing or discovery
    TIME_SYNC  = 0x4  #: Time synchronization message
    AUTH       = 0x5  #: Authentication or login data
    SESSION    = 0x6  #: Session initiation/teardown
    STATUS     = 0x7  #: Device status or health info
    LOG        = 0x8  #: Log or diagnostic data
    DEBUG      = 0x9  #: Debug-specific packets
    FIRMWARE   = 0xA  #: Firmware updates or related payloads
    RESERVED_B = 0xB  #: Reserved for future use
    RESERVED_C = 0xC  #: Reserved for future use
    RESERVED_D = 0xD  #: Reserved for future use
    RESERVED_E = 0xE  #: Reserved for future use
    RESERVED_F = 0xF  #: Reserved for future use


class HeaderFlags(IntFlag):
    """Control flags that may be embedded inside the packet packet_header."""
    NONE       = 0       #: No flags
    ACK        = 1 << 0  #: Acknowledgment packet
    ERROR      = 1 << 1  #: Error indication
    HEARTBEAT  = 1 << 2  #: Heartbeat signal
    ABORT      = 1 << 3  #: Abort signal
    PAUSE      = 1 << 4  #: Pause signal
    RESUME     = 1 << 5  #: Resume signal
    RESERVED_A = 1 << 6  #: Reserved for future use
    RESERVED_B = 1 << 7  #: Reserved for future use


# =============================================================================
# Ctypes Structure Definition
# =============================================================================

class _PacketHeaderStructure(ctypes.Structure):
    """
    Internal ctypes Structure to define the exact 4-byte memory layout
    of the packet header, matching the C++ `#pragma pack(1)` behavior.
    """
    _pack_ = 1  # Ensure 1-byte packing alignment.
    _fields_ = [
        ("space", ctypes.c_uint16),
        ("sender_id", ctypes.c_uint8),
        ("receiver_id", ctypes.c_uint8),
    ]


# =============================================================================
# Main Packet Header Class
# =============================================================================

class PacketHeader:
    """
    Compact 32-bit protocol packet_header for packet metadata transmission.

    This class provides a Pythonic interface to construct and interpret a
    4-byte packet header, ensuring byte-for-byte compatibility with the
    corresponding C++ implementation.

    #### Overall Packet Structure (4 bytes):
    ```
    Bytes 0-1 (16 bits)   | Byte 2 (8 bits)    | Byte 3 (8 bits)
    +---------------------+--------------------+-----------------+
    |        space        |    sender_id (I)   |   receiver_id   |
    +---------------------+--------------------+-----------------+
    ```

    #### `space` Field (16 bits) Layout:
    ```
    +-------------+-------+-----+------+--------+-------+----------+----------+
    | 15 14 13 12 | 11 10 | 9   | 8    | 7 6 5  | 4 3 2 | 1        | 0        |
    +-------------+-------+-----+------+--------+-------+----------+----------+
    |    type     |ver (I)| enc | frag |priority| flags | checksum | reserved |
    +-------------+-------+-----+------+--------+-------+----------+----------+
    ```
    Note: (I) stands for "Immutable" fields that are set at the protocol level.
    """

    def __init__(self, raw_value: int, receiver_id: int = 1):
        """
        Construct a PacketHeader directly from a raw 16-bit value for the first
        2 bytes and a receiver ID.

        Args:
            raw_value (int): The raw 16-bit value for the 'space' field. The
                             version bits within this value will be overwritten
                             by the global ETASK_PROTOCOL_VERSION.
            receiver_id (int): The 8-bit receiver ID. Defaults to 1.
        """
        self.data = _PacketHeaderStructure()
        # Overwrite version bits (11-10) with the locked protocol version.
        self.data.space = (raw_value & ~(0x3 << 10)) | \
                            ((ETASK_PROTOCOL_VERSION & 0x3) << 10)
        self.data.sender_id = ETASK_BOARD_ID
        self.data.receiver_id = receiver_id

    @staticmethod
    def from_fields(
        type: HeaderType,
        encrypted: bool,
        fragmented: bool,
        priority: int,
        flags: HeaderFlags,
        validated: bool,
        reserved: bool = False,
        receiver_id: int = 1
    ):
        """
        Constructs a PacketHeader with all bit fields specified.

        Args:
            type (HeaderType): Packet type (4 bits).
            encrypted (bool): Whether the packet is encrypted (1 bit).
            fragmented (bool): Whether the packet is fragmented (1 bit).
            priority (int): Packet priority (3 bits, 0=none, 7=highest).
            flags (HeaderFlags): Control flags (3 bits).
            validated (bool): Whether the packet has a checksum (1 bit).
            reserved (bool): Reserved bit (1 bit). Defaults to False.
            receiver_id (int): The 8-bit receiver ID. Defaults to 1.

        Returns:
            PacketHeader: A new instance of the PacketHeader.
        """
        space = (
            ((int(type) & 0xF) << 12) |
            ((ETASK_PROTOCOL_VERSION & 0x3) << 10) |
            ((int(encrypted) & 0x1) << 9) |
            ((int(fragmented) & 0x1) << 8) |
            ((priority & 0x7) << 5) |
            ((int(flags) & 0x7) << 2) |
            ((int(validated) & 0x1) << 1) |
            (int(reserved) & 0x1)
        )
        # Create an instance by calling the main constructor.
        return PacketHeader(raw_value=space, receiver_id=receiver_id)

    def to_bytes(self) -> bytes:
        """
        Returns the raw byte representation of the packet header.

        This is the data that should be sent over the wire.

        Returns:
            bytes: A 4-byte string representing the header data.
        """
        return bytes(self.data)

    def __repr__(self) -> str:
        """Provides a detailed string representation for debugging."""
        return (
            f"PacketHeader(type={self.type.name}, ver={self.version}, "
            f"enc={self.encrypted}, frag={self.fragmented}, prio={self.priority}, "
            f"flags={self.flags}, valid={self.validated}, res={self.reserved}, "
            f"sender={self.sender_id}, receiver={self.receiver_id})"
        )

    # ------------------ Properties for Field Access ------------------

    @property
    def type(self) -> HeaderType:
        """The packet type (bits 15-12 of space)."""
        return HeaderType((self.data.space >> 12) & 0xF)

    @property
    def version(self) -> int:
        """The protocol version (bits 11-10 of space). Immutable."""
        return (self.data.space >> 10) & 0x3

    @property
    def encrypted(self) -> bool:
        """The encrypted flag (bit 9 of space)."""
        return (self.data.space & 0x0200) != 0

    @property
    def fragmented(self) -> bool:
        """The fragmentation flag (bit 8 of space)."""
        return (self.data.space & 0x0100) != 0

    @property
    def priority(self) -> int:
        """The priority level (bits 7-5 of space)."""
        return (self.data.space >> 5) & 0x7

    @property
    def flags(self) -> HeaderFlags:
        """The control flags (bits 4-2 of space)."""
        return HeaderFlags((self.data.space >> 2) & 0x7)

    @property
    def validated(self) -> bool:
        """The validation (checksum) presence flag (bit 1 of space)."""
        return (self.data.space & 0x0002) != 0

    @property
    def reserved(self) -> bool:
        """The reserved bit (bit 0 of space)."""
        return (self.data.space & 0x0001) != 0

    @property
    def sender_id(self) -> int:
        """The 8-bit sender ID. Immutable."""
        return self.data.sender_id

    @property
    def receiver_id(self) -> int:
        """The 8-bit receiver ID."""
        return self.data.receiver_id

    @receiver_id.setter
    def receiver_id(self, value: int):
        """Sets the 8-bit receiver ID."""
        if not 0 <= value <= 255:
            raise ValueError("receiver_id must be an 8-bit integer (0-255).")
        self.data.receiver_id = value