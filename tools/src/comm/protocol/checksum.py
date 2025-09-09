# SPDX-License-Identifier: BSL-1.1
# -*- coding: utf-8 -*-
"""
Checksum policy descriptors for FramedPacket layout (layout-only, no computation).

These mirror the C++ checksum.hpp policies:
 - Each policy exposes:
     * ctype: ctypes unsigned integer type for the FCS field (or None for none)
     * size:  number of bytes occupied by the FCS field

Computation is intentionally out-of-scope here (match C++ separation with compute.hpp).
"""

import ctypes
from dataclasses import dataclass
from typing import Optional, Type


@dataclass(frozen=True)
class Checksum:
    """Layout-only description of an FCS field."""
    name: str
    ctype: Optional[Type[ctypes._SimpleCData]]
    size: int


# None (no checksum)
NONE = Checksum("none", None, 0)

# Simple sums
SUM8  = Checksum("sum8",  ctypes.c_uint8,  ctypes.sizeof(ctypes.c_uint8))
SUM16 = Checksum("sum16", ctypes.c_uint16, ctypes.sizeof(ctypes.c_uint16))
SUM32 = Checksum("sum32", ctypes.c_uint32, ctypes.sizeof(ctypes.c_uint32))

# CRC family
CRC8  = Checksum("crc8",  ctypes.c_uint8,  ctypes.sizeof(ctypes.c_uint8))
CRC16 = Checksum("crc16", ctypes.c_uint16, ctypes.sizeof(ctypes.c_uint16))
CRC32 = Checksum("crc32", ctypes.c_uint32, ctypes.sizeof(ctypes.c_uint32))
CRC64 = Checksum("crc64", ctypes.c_uint64, ctypes.sizeof(ctypes.c_uint64))

# Fletcher
FLETCHER16 = Checksum("fletcher16", ctypes.c_uint16, ctypes.sizeof(ctypes.c_uint16))
FLETCHER32 = Checksum("fletcher32", ctypes.c_uint32, ctypes.sizeof(ctypes.c_uint32))

# Adler
ADLER32 = Checksum("adler32", ctypes.c_uint32, ctypes.sizeof(ctypes.c_uint32))

# Internet 1's complement
INTERNET16 = Checksum("internet16", ctypes.c_uint16, ctypes.sizeof(ctypes.c_uint16))
