# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
validator — packet sealing/validation for the etask protocol.

This mirrors the C++ template specializations:

    validator<basic_packet<...>>
    validator<framed_packet<...>>

Behavior:
- BasicPacket: no checksum; `is_valid()` -> True, `seal()` -> no-op.
- FramedPacket: compute checksum over header|status|task_id|payload
  (i.e., all bytes EXCEPT the trailing FCS field). Uses the policy
  specified by the packet (`packet.policy`) and writes/compares the
  integer value in the `fcs` field.

Design notes:
- Stateless; safe to reuse a single Validator instance.
- This module does NOT do any IO; only pure computation & field writes.
- Any wire-image is taken from `packet.to_bytes()`; slicing excludes FCS.
"""

from __future__ import annotations

from typing import Union, cast

from .basic_packet import BasicPacket
from .framed_packet import FramedPacket
from .checksum import Checksum, NONE
from .compute import compute


Packet = Union[BasicPacket, FramedPacket]


class Validator:
    """
    Stateless packet validator/sealer.

    Methods:
        - is_valid(packet): bool
        - seal(packet): None

    For FramedPacket, the checksum is computed over:
        bytes(packet)[: packet.packet_size - packet.policy.size]
    and compared/written according to the packet's `policy`.
    """

    # ---------------------------
    # Public API
    # ---------------------------

    def is_valid(self, packet: Packet) -> bool:
        """Return True if the packet is valid for transmission/consumption."""
        if isinstance(packet, BasicPacket):
            # No checksum in a basic packet.
            return True

        if isinstance(packet, FramedPacket):
            policy: Checksum = packet.policy
            if policy is NONE or policy.size == 0:
                # Layout has no FCS; treat as always valid (mirrors no-checksum case).
                return True

            wire = packet.to_bytes()
            end = packet.packet_size - policy.size
            expected = compute(policy, wire[:end])
            current = cast(int, packet.fcs)  # int (ctypes field defaults to 0 if not set)
            return int(current) == int(expected)

        raise TypeError(f"Unsupported packet type: {type(packet).__name__}")

    def seal(self, packet: Packet) -> None:
        """Finalize a packet before transmission (write FCS for framed packets)."""
        if isinstance(packet, BasicPacket):
            # Nothing to do.
            return

        if isinstance(packet, FramedPacket):
            policy: Checksum = packet.policy
            if policy is NONE or policy.size == 0:
                # No FCS field present; nothing to write.
                return

            wire = packet.to_bytes()
            end = packet.packet_size - policy.size
            value = compute(policy, wire[:end])
            packet.fcs = value  # range-checked by FramedPacket
            return

        raise TypeError(f"Unsupported packet type: {type(packet).__name__}")


# Optional convenience free functions (match the spirit of C++ callable specializations).
def is_packet_valid(packet: Packet) -> bool:
    """Convenience wrapper around Validator().is_valid(packet)."""
    return Validator().is_valid(packet)


def seal_packet(packet: Packet) -> None:
    """Convenience wrapper around Validator().seal(packet)."""
    Validator().seal(packet)
