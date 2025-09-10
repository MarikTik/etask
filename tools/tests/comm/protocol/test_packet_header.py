# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Pytest unit tests for the PacketHeader class.

This file provides a comprehensive suite of tests to validate the functionality,
correctness, and edge cases of the PacketHeader implementation.
"""

import pytest
import struct

# Import the module to be tested
from comm.protocol.packet_header import (
    ETASK_BOARD_ID,
    ETASK_PROTOCOL_VERSION,
    HeaderFlags,
    HeaderType,
    PacketHeader,
)

# =============================================================================
# Tests for __init__ (Raw Value Constructor)
# =============================================================================

def test_init_from_raw_value_basic() -> None:
    """Tests basic initialization from a raw value and default receiver ID."""
    header = PacketHeader(raw_value=0, receiver_id=50)
    assert header.receiver_id == 50
    assert header.sender_id == ETASK_BOARD_ID
    assert header.version == ETASK_PROTOCOL_VERSION
    assert header.type == HeaderType.DATA
    assert header.priority == 0
    assert not header.encrypted

def test_init_from_raw_value_overwrites_version() -> None:
    """
    Ensures the constructor correctly overwrites the version bits in the
    provided raw_value with the global protocol version.
    """
    # 0xFFFF has all bits set, including version bits 11-10
    header = PacketHeader(raw_value=0xFFFF)
    # The version should be ETASK_PROTOCOL_VERSION, not 3 (0b11)
    assert header.version == ETASK_PROTOCOL_VERSION
    # Check that other fields are correctly interpreted from the raw value
    assert header.type == HeaderType.RESERVED_F
    assert header.priority == 7
    assert header.flags == HeaderFlags.ACK | HeaderFlags.ERROR | HeaderFlags.HEARTBEAT


# =============================================================================
# Tests for from_fields() Constructor
# =============================================================================

def test_from_fields_defaults() -> None:
    """Tests the from_fields constructor with default or 'zero' values."""
    header = PacketHeader.from_fields(
        type=HeaderType.DATA,
        encrypted=False,
        fragmented=False,
        priority=0,
        flags=HeaderFlags.NONE,
        validated=False
    )
    assert header.type == HeaderType.DATA
    assert not header.encrypted
    assert not header.fragmented
    assert header.priority == 0
    assert header.flags == HeaderFlags.NONE
    assert not header.validated
    assert not header.reserved
    assert header.version == ETASK_PROTOCOL_VERSION
    assert header.sender_id == ETASK_BOARD_ID
    assert header.receiver_id == 1  # Default receiver ID

def test_from_fields_all_set() -> None:
    """Tests the from_fields constructor with all boolean flags set and max values."""
    header = PacketHeader.from_fields(
        type=HeaderType.RESERVED_F,
        encrypted=True,
        fragmented=True,
        priority=7,
        flags=HeaderFlags.ACK | HeaderFlags.ERROR | HeaderFlags.HEARTBEAT,
        validated=True,
        reserved=True,
        receiver_id=255
    )
    assert header.type == HeaderType.RESERVED_F
    assert header.encrypted
    assert header.fragmented
    assert header.priority == 7
    # The flags field is 3 bits, so it can only hold values up to 7
    expected_flags = HeaderFlags.ACK | HeaderFlags.ERROR | HeaderFlags.HEARTBEAT
    assert header.flags == expected_flags
    assert header.validated
    assert header.reserved
    assert header.receiver_id == 255

def test_from_fields_field_isolation() -> None:
    """Tests that setting a single field affects only that field."""
    # Test Priority
    header_prio = PacketHeader.from_fields(
        type=HeaderType.DATA, encrypted=False, fragmented=False,
        priority=5, flags=HeaderFlags.NONE, validated=False
    )
    assert header_prio.priority == 5
    assert header_prio.type == HeaderType.DATA
    assert not header_prio.encrypted

    # Test Encrypted
    header_enc = PacketHeader.from_fields(
        type=HeaderType.DATA, encrypted=True, fragmented=False,
        priority=0, flags=HeaderFlags.NONE, validated=False
    )
    assert header_enc.encrypted
    assert header_enc.priority == 0
    assert not header_enc.fragmented

@pytest.mark.parametrize("priority_in, priority_out", [
    (0, 0),
    (7, 7),
    (8, 0),  # 8 is 0b1000, masked with 0b111 becomes 0
    (15, 7), # 15 is 0b1111, masked with 0b111 becomes 7
])
def test_from_fields_priority_masking(priority_in, priority_out) -> None:
    """Ensures priority values are correctly masked to 3 bits."""
    header = PacketHeader.from_fields(
        type=HeaderType.DATA, encrypted=False, fragmented=False,
        priority=priority_in, flags=HeaderFlags.NONE, validated=False
    )
    assert header.priority == priority_out

@pytest.mark.parametrize("flag", list(HeaderType))
def test_from_fields_all_header_types(flag) -> None:
    """Tests that all HeaderType enum values are handled correctly."""
    header = PacketHeader.from_fields(
        type=flag, encrypted=False, fragmented=False,
        priority=0, flags=HeaderFlags.NONE, validated=False
    )
    assert header.type == flag

# =============================================================================
# Tests for Properties and Setters
# =============================================================================

def test_receiver_id_setter_valid() -> None:
    """Tests setting the receiver_id with valid values."""
    header = PacketHeader(raw_value=0)
    assert header.receiver_id == 1  # default
    header.receiver_id = 123
    assert header.receiver_id == 123
    header.receiver_id = 0
    assert header.receiver_id == 0
    header.receiver_id = 255
    assert header.receiver_id == 255

def test_receiver_id_setter_invalid() -> None:
    """Tests that setting an out-of-range receiver_id raises a ValueError."""
    header = PacketHeader(raw_value=0)
    with pytest.raises(ValueError, match="receiver_id must be an 8-bit integer"):
        header.receiver_id = 256
    with pytest.raises(ValueError, match="receiver_id must be an 8-bit integer"):
        header.receiver_id = -1

def test_immutable_properties() -> None:
    """Ensures that immutable properties (sender_id, version) cannot be set."""
    header = PacketHeader(raw_value=0)
    with pytest.raises(AttributeError):
        header.sender_id = 99
    with pytest.raises(AttributeError):
        header.version = 2

# =============================================================================
# Tests for Utility Methods (to_bytes, __repr__)
# =============================================================================

def test_to_bytes() -> None:
    """
    Tests the to_bytes() method for correct length and content.
    Note: This test assumes a little-endian system, which is standard.
    """
    header = PacketHeader.from_fields(
        type=HeaderType.CONFIG,     # 1
        encrypted=True,             # 1
        fragmented=False,           # 0
        priority=5,                 # 5
        flags=HeaderFlags.ACK,      # 1
        validated=True,             # 1
        reserved=False,             # 0
        receiver_id=0xAA
    )

    # Calculate expected 'space' field value manually
    # type(1):      0001
    # version(1):       01
    # encrypted(1):        1
    # fragmented(0):         0
    # priority(5):          101
    # flags(1):                001
    # validated(1):                 1
    # reserved(0):                   0
    # Binary: 0001 0110 1010 0110
    # Hex:    0x16A6
    expected_space = 0x16A6
    assert header.data.space == expected_space

    # The final 4-byte packet should be:
    # space (2 bytes, little-endian), sender_id (1 byte), receiver_id (1 byte)
    expected_bytes = struct.pack(
        "<HBB", expected_space, ETASK_BOARD_ID, 0xAA
    )
    assert len(header.to_bytes()) == 4
    assert header.to_bytes() == expected_bytes

def test_repr() -> None:
    """Tests the __repr__ method for a meaningful representation."""
    header = PacketHeader(raw_value=0, receiver_id=42)
    rep_str = repr(header)

    assert isinstance(rep_str, str)
    assert "PacketHeader" in rep_str
    assert "type=DATA" in rep_str
    assert f"ver={ETASK_PROTOCOL_VERSION}" in rep_str
    assert "enc=False" in rep_str
    assert f"sender={ETASK_BOARD_ID}" in rep_str
    assert "receiver=42" in rep_str