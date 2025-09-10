# SPDX-License-Identifier: BSL-1.1
# Copyright (c) 2025 Mark Tikhonov
# Business Source License 1.1 (BSL 1.1)
# Free for non-commercial use. Commercial use requires a separate license.
# See LICENSE file for details.

"""utils.py
====================

Utilities for argument parsing, validation, and payload encoding for the etask
protocol CLI tools.

This module centralizes helpers used by the CLI parser:
- Range/shape validators for numeric args and IDs
- Transport validation (UART/TCP)
- Packet sizing and alignment derivation
- Header flag parsing
- Multiple payload source readers (list, hex, file)
- **Schema-based payload encoding** with little-endian, fixed-size, NUL-terminated
  strings by default (C-strings), arrays, padding, and raw `struct` blobs.

Design Principles
-----------------
- **Little endian only**: all multi-byte scalars encode with '<' endianness.
- **No implicit alignment**: the on-wire layout is the exact concatenation
  of encoded fields; any padding must be explicit: ``pad[N]``.
- **Strings are C-strings by default**: ``string[N]`` / ``cstring[N]`` encodes
  a UTF-8 string, appends a single ``0x00`` terminator, then zero-pads to N,
  truncating content to **N-1** bytes when necessary.
- **Arrays**: ``type[M]`` encodes M items back-to-back.
- **Raw struct**: ``struct`` accepts a bytes object (or is injected from
  ``--struct-hex`` / ``--struct-file`` when the user passes a sentinel).

Example
-------
Schema: ``"uint16, uint32, float, string[4]"``
Values: ``(17, 123456, 23.75, "TEMP")``

Encodes equivalent to ``struct.pack("<HIf4s")`` but with C-string semantics
for ``string[4]`` (result: ``b'TEMP'`` is exactly 4 bytes; if the string
were shorter, it would include a NUL terminator and pad; if longer than 3,
content would be truncated to 3 then NUL).

"""

from __future__ import annotations

import argparse
import ast
import ipaddress
import os
import re
import struct
from typing import Iterable, List, Tuple, Union, Optional, Dict, Any

# -----------------------------
# Public constants / lookups
# -----------------------------

HEADER_TYPES = {
    "data":        0x0,
    "config":      0x1,
    "control":     0x2,
    "routing":     0x3,
    "time_sync":   0x4,
    "auth":        0x5,
    "session":     0x6,
    "status":      0x7,
    "log":         0x8,
    "debug":       0x9,
    "firmware":    0xA,
    "reserved_b":  0xB,
    "reserved_c":  0xC,
    "reserved_d":  0xD,
    "reserved_e":  0xE,
    "reserved_f":  0xF,
}

HEADER_FLAGS = {
    "none":        0,
    "ack":         1 << 0,
    "error":       1 << 1,
    "heartbeat":   1 << 2,
    "abort":       1 << 3,
    "pause":       1 << 4,
    "resume":      1 << 5,
    "reserved_a":  1 << 6,
    "reserved_b":  1 << 7,
}

CHECKSUM_POLICIES = {
    "none":  (0,  "No trailing checksum (use with framed to force no-FCS)."),
    "sum16": (2,  "16-bit additive checksum."),
    "crc32": (4,  "CRC-32 (IEEE 802.3 style)."),
}

TASK_ID_TYPES = {
    "u8":   1,
    "u16":  2,
    "u32":  4,
}

DEFAULTS = {
    "word_bytes": 4,
    "sender_min": 1,     # 0 reserved for MCU unless firmware changes
    "sender_max": 255,
    "id_min": 0,
    "id_max": 255,
}

# -----------------------------
# Basic validators / helpers
# -----------------------------

def int_in_range(value: str, lo: int, hi: int, name: str) -> int:
    """Parse an integer (base auto) and validate closed interval [lo, hi]."""
    try:
        iv = int(value, 0)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"{name}: invalid integer '{value}'") from e
    if not (lo <= iv <= hi):
        raise argparse.ArgumentTypeError(f"{name}: {iv} out of range [{lo}, {hi}]")
    return iv


def positive_int(value: str, name: str) -> int:
    """Parse a strictly positive integer."""
    try:
        iv = int(value, 0)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"{name}: invalid integer '{value}'") from e
    if iv <= 0:
        raise argparse.ArgumentTypeError(f"{name}: must be > 0 (got {iv})")
    return iv


def nonneg_int(value: str, name: str) -> int:
    """Parse a non-negative integer."""
    try:
        iv = int(value, 0)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"{name}: invalid integer '{value}'") from e
    if iv < 0:
        raise argparse.ArgumentTypeError(f"{name}: must be >= 0 (got {iv})")
    return iv


def parse_flags(csv_or_multi: List[str]) -> int:
    """Accumulate a bitmask from flag tokens (repeatable or comma-separated)."""
    bitmask = 0
    for token in csv_or_multi or []:
        parts = [p.strip() for p in token.split(",")] if "," in token else [token.strip()]
        for name in parts:
            if not name:
                continue
            if name not in HEADER_FLAGS:
                raise argparse.ArgumentTypeError(
                    f"Unknown flag '{name}'. Valid: {', '.join(HEADER_FLAGS.keys())}"
                )
            bitmask |= HEADER_FLAGS[name]
    return bitmask


def parse_payload_list(text: str) -> List[int]:
    """Parse a list of byte values from comma/space-separated tokens (0x.., 0b.., decimal)."""
    tokens = text.replace(",", " ").split()
    out: List[int] = []
    for tok in tokens:
        try:
            v = int(tok, 0)
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"payload: invalid integer '{tok}'") from e
        if not (0 <= v <= 255):
            raise argparse.ArgumentTypeError(f"payload byte out of range [0,255]: {v}")
        out.append(v)
    return out


def parse_payload_hex(text: str) -> List[int]:
    """Parse contiguous hex (spaces allowed) into bytes."""
    s = "".join(text.split())
    if len(s) % 2 != 0:
        raise argparse.ArgumentTypeError("payload-hex: hex string must have even length")
    try:
        data = bytes.fromhex(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError("payload-hex: invalid hex") from e
    return list(data)


def read_payload_file(path: str) -> List[int]:
    """Read raw bytes from a file."""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"payload-file: path not found: {path}")
    with open(path, "rb") as f:
        data = f.read()
    return list(data)


def require_one_payload_source(*vals) -> None:
    """Ensure at most one payload source is provided."""
    provided = sum(v is not None for v in vals)
    if provided > 1:
        raise argparse.ArgumentTypeError(
            "Specify only one payload source among: "
            "--payload, --payload-hex, --payload-file, --payload-pack, --payload-schema."
        )


def derive_payload_size(packet_kind: str, packet_size: int, task_id_size: int,
                        checksum_name: str, word_bytes: int) -> Tuple[int, int]:
    """Compute payload size and checksum size. Enforce word alignment and minimal structure size.

    Returns:
        (payload_size, checksum_size)
    """
    if packet_size % word_bytes != 0:
        raise argparse.ArgumentTypeError(
            f"--packet-size must be word-aligned ({word_bytes} bytes). Got {packet_size}."
        )

    header_size = 3  # 24-bit header footprint
    status_size = 1  # status_code

    if packet_kind == "basic":
        checksum_size = 0
    elif packet_kind == "framed":
        if checksum_name not in CHECKSUM_POLICIES:
            raise argparse.ArgumentTypeError(f"Unknown checksum policy '{checksum_name}'.")
        checksum_size = CHECKSUM_POLICIES[checksum_name][0]
    else:
        raise argparse.ArgumentTypeError("--packet-kind must be 'basic' or 'framed'.")

    min_size = header_size + status_size + task_id_size + checksum_size
    if packet_size < (min_size + 1):
        raise argparse.ArgumentTypeError(
            f"--packet-size too small. Minimum is {min_size + 1} (got {packet_size})."
        )

    payload_size = packet_size - (header_size + status_size + task_id_size + checksum_size)
    return payload_size, checksum_size


def validate_transport(ns: argparse.Namespace) -> None:
    """Validate UART/TCP interface arguments."""
    if ns.iface == "uart":
        if not ns.uart_port:
            raise argparse.ArgumentTypeError("--uart-port is required when --iface uart.")
        if ns.parity not in {"N", "E", "O", "M", "S"}:
            raise argparse.ArgumentTypeError("--parity must be one of N,E,O,M,S.")
        if ns.stopbits not in {1, 1.5, 2}:
            raise argparse.ArgumentTypeError("--stopbits must be 1, 1.5, or 2.")
    elif ns.iface == "tcp":
        # allow hostnames or IPs
        try:
            ipaddress.ip_address(ns.host)
        except ValueError:
            pass
    else:
        raise argparse.ArgumentTypeError("--iface must be 'uart' or 'tcp'.")


def validate_ids(sender_id: int, receiver_id: int) -> None:
    """Validate sender/receiver ranges per protocol conventions."""
    if not (DEFAULTS["sender_min"] <= sender_id <= DEFAULTS["sender_max"]):
        raise argparse.ArgumentTypeError(
            f"--sender-id must be in [{DEFAULTS['sender_min']}, {DEFAULTS['sender_max']}]; 0 is reserved."
        )
    if not (DEFAULTS["id_min"] <= receiver_id <= DEFAULTS["id_max"]):
        raise argparse.ArgumentTypeError("--receiver-id must be in [0, 255].")


# -----------------------------
# Schema-based payload encoder
# -----------------------------

# Map schema scalar names to struct format codes (little-endian).
_STRUCT_MAP = {
    "int8":   "b",
    "uint8":  "B",
    "int16":  "h",
    "uint16": "H",
    "int32":  "i",
    "uint32": "I",
    "int64":  "q",
    "uint64": "Q",
    "float":  "f",
    "double": "d",
    "bool":   "?",  # encodes 1 byte 0x00/0x01
}

# Regex patterns for typed fields: string[N], bytes[N], pad[N], scalar[M]
_RE_STRING  = re.compile(r"^(?:string|cstring)\[(\d+)\]$")
_RE_BYTES   = re.compile(r"^bytes\[(\d+)\]$")
_RE_PAD     = re.compile(r"^pad\[(\d+)\]$")
_RE_ARRAY   = re.compile(r"^(int8|uint8|int16|uint16|int32|uint32|int64|uint64|float|double|bool)\[(\d+)\]$")


class SchemaField:
    """Parsed representation of a single schema item."""
    kind: str                 # 'scalar' | 'array' | 'string' | 'bytes' | 'pad' | 'struct'
    base: Optional[str]       # scalar base for 'scalar'/'array'
    count: int                # for arrays/pad; 0 otherwise
    size: int                 # for string/bytes: N; otherwise 0

    def __init__(self, kind: str, base: Optional[str] = None, count: int = 0, size: int = 0) -> None:
        self.kind = kind
        self.base = base
        self.count = count
        self.size = size

    def __repr__(self) -> str:
        if self.kind == "scalar":
            return f"<scalar {self.base}>"
        if self.kind == "array":
            return f"<array {self.base}[{self.count}]>"
        if self.kind in ("string", "bytes"):
            return f"<{self.kind}[{self.size}]>"
        if self.kind == "pad":
            return f"<pad[{self.count}]>"
        return "<struct>"


def parse_schema(schema_text: str) -> List[SchemaField]:
    """Parse a comma/space-separated schema string into SchemaField entries.

    Supported items:
      - Scalars: int8,uint8,int16,uint16,int32,uint32,int64,uint64,float,double,bool
      - Arrays:  <scalar>[M]
      - Strings: string[N] / cstring[N]  (NUL-terminated C-string semantics)
      - Bytes:   bytes[N]                 (raw bytes, no encoding)
      - Padding: pad[N]                   (N zero bytes)
      - Raw:     struct                   (expects `bytes` value)

    Args:
        schema_text: The schema string.

    Returns:
        A list of SchemaField items.

    Raises:
        argparse.ArgumentTypeError: For unknown or malformed items.
    """
    items = [part.strip() for part in schema_text.replace(",", " ").split() if part.strip()]
    if not items:
        raise argparse.ArgumentTypeError("--payload-schema: empty schema")
    fields: List[SchemaField] = []
    for item in items:
        if item == "struct":
            fields.append(SchemaField("struct"))
            continue
        m = _RE_STRING.match(item)
        if m:
            n = int(m.group(1))
            if n <= 0:
                raise argparse.ArgumentTypeError("string[N]: N must be > 0")
            fields.append(SchemaField("string", size=n))
            continue
        m = _RE_BYTES.match(item)
        if m:
            n = int(m.group(1))
            if n <= 0:
                raise argparse.ArgumentTypeError("bytes[N]: N must be > 0")
            fields.append(SchemaField("bytes", size=n))
            continue
        m = _RE_PAD.match(item)
        if m:
            n = int(m.group(1))
            if n < 0:
                raise argparse.ArgumentTypeError("pad[N]: N must be >= 0")
            fields.append(SchemaField("pad", count=n))
            continue
        m = _RE_ARRAY.match(item)
        if m:
            base = m.group(1)
            cnt = int(m.group(2))
            if cnt <= 0:
                raise argparse.ArgumentTypeError(f"{base}[M]: M must be > 0")
            fields.append(SchemaField("array", base=base, count=cnt))
            continue
        # scalar?
        if item in _STRUCT_MAP:
            fields.append(SchemaField("scalar", base=item))
            continue
        raise argparse.ArgumentTypeError(f"--payload-schema: unknown item '{item}'")
    return fields


def literal_tuple_or_list(expr: str, name: str) -> List[Any]:
    """Safely parse a Python literal tuple/list (used for --payload-values).

    Accepts nested tuples/lists, ints, floats, bools, None, str, bytes.
    """
    try:
        obj = ast.literal_eval(expr)
    except Exception as e:
        raise argparse.ArgumentTypeError(f"{name}: invalid Python literal: {e}") from e
    if not isinstance(obj, (tuple, list)):
        raise argparse.ArgumentTypeError(f"{name}: must be a tuple or list literal.")
    return list(obj)


def _pack_scalar(fmt: str, value: Any) -> bytes:
    try:
        return struct.pack("<" + fmt, value)
    except struct.error as e:
        raise argparse.ArgumentTypeError(f"scalar pack error ({fmt}): {e}") from e


def _pack_cstring_n(n: int, text: str, encoding: str) -> bytes:
    """Encode a C-string with max field size n (including the terminator).
    Truncate content to n-1, append NUL, then pad with zeros to n bytes.
    """
    raw = text.encode(encoding)
    content = raw[: max(0, n - 1)]
    out = content + b"\x00"
    if len(out) < n:
        out += b"\x00" * (n - len(out))
    return out[:n]


def _fit_exact_n(n: int, data: Union[bytes, bytearray]) -> bytes:
    """Ensure exactly n bytes: pad with zeros if short; truncate if long."""
    b = bytes(data)
    if len(b) == n:
        return b
    if len(b) < n:
        return b + b"\x00" * (n - len(b))
    return b[:n]


def pack_schema(fields: List[SchemaField],
                values: List[Any],
                *,
                string_encoding: str = "utf-8",
                struct_blob: Optional[bytes] = None,
                struct_sentinel: str = "__STRUCT__") -> bytes:
    """Pack values according to parsed schema into a single payload blob.

    Args:
        fields: Parsed schema (from parse_schema()).
        values: Python values matching the schema, 1:1 with data-yielding fields.
                For arrays, supply a list/tuple of the right length.
                For 'struct', supply a bytes object *or* the sentinel string to
                substitute `struct_blob`.
        string_encoding: Encoding for string[...] fields (default utf-8).
        struct_blob: If provided and a 'struct' field's value equals the sentinel,
                     this raw blob is inserted.
        struct_sentinel: Magic string used as a placeholder in values for 'struct'.

    Returns:
        Bytes of encoded payload.

    Raises:
        argparse.ArgumentTypeError: If a mismatch or packing error occurs.
    """
    # Determine how many value slots are required by the schema.
    # pad[...] contributes no value; struct contributes one; arrays contribute one.
    required_slots = 0
    for f in fields:
        if f.kind == "pad":
            continue
        required_slots += 1

    if len(values) != required_slots:
        raise argparse.ArgumentTypeError(
            f"--payload-values count mismatch: schema requires {required_slots} value(s), "
            f"but got {len(values)}."
        )

    out = bytearray()
    vi = 0  # index into values

    for f in fields:
        if f.kind == "pad":
            out += b"\x00" * f.count
            continue

        if f.kind == "scalar":
            fmt = _STRUCT_MAP[f.base]  # type: ignore[index]
            out += _pack_scalar(fmt, values[vi])
            vi += 1
            continue

        if f.kind == "array":
            fmt = _STRUCT_MAP[f.base]  # type: ignore[index]
            items = values[vi]
            vi += 1
            if not isinstance(items, (list, tuple)) or len(items) != f.count:
                raise argparse.ArgumentTypeError(
                    f"array {f.base}[{f.count}] expects a list/tuple of length {f.count}"
                )
            for item in items:
                out += _pack_scalar(fmt, item)
            continue

        if f.kind == "string":
            text = values[vi]
            vi += 1
            if not isinstance(text, str):
                raise argparse.ArgumentTypeError("string[N] expects a Python str")
            out += _pack_cstring_n(f.size, text, string_encoding)
            continue

        if f.kind == "bytes":
            blob = values[vi]
            vi += 1
            if isinstance(blob, str):
                # allow hex-ish strings like "DE AD BE EF"
                try:
                    blob = bytes.fromhex("".join(blob.split()))
                except ValueError:
                    raise argparse.ArgumentTypeError("bytes[N] expects bytes or hex-like string")
            if not isinstance(blob, (bytes, bytearray)):
                raise argparse.ArgumentTypeError("bytes[N] expects bytes/bytearray (or hex string)")
            out += _fit_exact_n(f.size, blob)
            continue

        if f.kind == "struct":
            blob = values[vi]
            vi += 1
            if isinstance(blob, str) and blob == struct_sentinel:
                if struct_blob is None:
                    raise argparse.ArgumentTypeError(
                        "struct value used sentinel but no --struct-hex/--struct-file provided"
                    )
                blob = struct_blob
            if not isinstance(blob, (bytes, bytearray)):
                raise argparse.ArgumentTypeError("struct expects bytes/bytearray (or sentinel)")
            out += bytes(blob)
            continue

        raise argparse.ArgumentTypeError(f"Unsupported schema field: {f}")

    return bytes(out)
