# SPDX-License-Identifier: BSL-1.1
# Copyright (c) 2025 Mark Tikhonov
# Business Source License 1.1 (BSL 1.1)
# Free for non-commercial use. Commercial use requires a separate license.
# See LICENSE file for details.

"""parser.py
============

High-level CLI parser for building **etask** packets and selecting a transport
(UART or TCP). This parser exposes explicit controls for:

- Packet kind: **basic** vs **framed** (with checksum policy)
- Total packet size (word-aligned), task-id type/value, status code
- Header metadata: type, encrypted/fragmented, priority, flags, validated,
  reserved, sender-id, receiver-id
- Payload sources:
  1) Byte **list** (`--payload`)
  2) **Hex** string (`--payload-hex`)
  3) **File** bytes (`--payload-file`)
  4) **struct.pack** format + args (`--payload-pack`, `--payload-args`)
  5) **Type-first schema** (`--payload-schema`, `--payload-values`) with:
     - Scalars: int8/uint8/int16/uint16/int32/uint32/int64/uint64/float/double/bool
     - C-Strings: string[N] / cstring[N]  (NUL-terminated + zero-padded to N)
     - Raw bytes: bytes[N]
     - Padding: pad[N]
     - Arrays: T[M]
     - Raw blob: struct (from values, or via --struct-hex/--struct-file sentinel injection)

Little Endian & No Hidden Padding
---------------------------------
- **Little endian only** for multi-byte scalars (mirror your MCU/firmware).
- **No implicit alignment** is inserted by this CLI. To match ABI/padding,
  use explicit `pad[N]` in the schema.

Examples
--------
**Schema (with C-strings)**
    --payload-schema "uint16, uint32, float, string[4]" \
    --payload-values "(17, 123456, 23.75, 'TEMP')"

**Arrays and padding**
    --payload-schema "uint8, uint8, uint16, uint32, pad[2], uint16" \
    --payload-values "(0x02, 0b00010001, 500, 0xDEADBEEF, 2500)"

**Raw struct via sentinel + hex**
    --payload-schema "uint16, struct, uint8" \
    --payload-values "(0xA55A, '__STRUCT__', 7)" \
    --struct-hex "DE AD BE EF 01 02"

Author
------
Mark Tikhonov <mtik.philosopher@gmail.com>

Changelog
---------
2025-09-01
- Added schema-based payload with C-string defaults and raw struct support.
- Separated utilities into payload_utils.py.
- Retained legacy payload sources for flexibility.
"""

from __future__ import annotations

import argparse
import ast
import os
import struct
from typing import List

from utils import (
    HEADER_TYPES,
    HEADER_FLAGS,
    CHECKSUM_POLICIES,
    TASK_ID_TYPES,
    DEFAULTS,
    # validators
    int_in_range,
    positive_int,
    nonneg_int,
    parse_flags,
    parse_payload_list,
    parse_payload_hex,
    read_payload_file,
    require_one_payload_source,
    derive_payload_size,
    validate_transport,
    validate_ids,
    # schema
    parse_schema,
    literal_tuple_or_list,
    pack_schema,
)

class Parser:
    """Builds the etask CLI `argparse.ArgumentParser` and performs cross-field validation."""
    def __init__(self) -> None:
        self._parser: argparse.ArgumentParser | None = None

    def build(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="etask-packet",
            description="Build etask packets (basic/framed) and select a transport (UART/TCP).",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # ---- Packet kind & sizing ----
        pkt = parser.add_argument_group("packet kind & sizing")
        pkt.add_argument("--packet-kind", choices=["basic", "framed"], default="basic",
                         help="Select basic or framed packet format.")
        pkt.add_argument("--checksum", choices=tuple(CHECKSUM_POLICIES.keys()), default="crc32",
                         help="Checksum policy used only when --packet-kind=framed.")
        pkt.add_argument("--packet-size", type=lambda s: positive_int(s, "packet-size"), default=32,
                         help="Total packet size in bytes; must be word-aligned.")
        pkt.add_argument("--word-bytes", type=lambda s: positive_int(s, "word-bytes"),
                         default=DEFAULTS["word_bytes"],
                         help="Word size for alignment checks (embedded targets typically 4).")

        # ---- Task ID & status ----
        tid = parser.add_argument_group("task ID & status")
        tid.add_argument("--task-id-type", choices=tuple(TASK_ID_TYPES.keys()), default="u8",
                         help="Underlying type of the task ID field.")
        tid.add_argument("--task-id", type=lambda s: nonneg_int(s, "task-id"), default=0,
                         help="Task ID value (must fit into selected --task-id-type).")
        tid.add_argument("--status-code", type=lambda s: int_in_range(s, 0, 255, "status-code"), default=0,
                         help="Optional status code byte (0-255).")

        # ---- Header fields ----
        hdr = parser.add_argument_group("header")
        hdr.add_argument("--type", choices=tuple(HEADER_TYPES.keys()), default="data",
                         help="Packet header type (4-bit field).")
        hdr.add_argument("--encrypted", action="store_true", help="Set 'encrypted' flag.")
        hdr.add_argument("--fragmented", action="store_true", help="Set 'fragmented' flag.")
        hdr.add_argument("--priority", type=lambda s: int_in_range(s, 0, 7, "priority"), default=0,
                         help="Priority (3 bits, 0-7).")
        hdr.add_argument("--flags", action="append", default=[],
                         help=("Header flags (repeat or comma-list). "
                               f"Valid: {', '.join(HEADER_FLAGS.keys())}"))
        hdr.add_argument("--validated", action="store_true",
                         help="Set header-level 'has checksum' bit.")
        hdr.add_argument("--reserved", action="store_true", help="Set reserved bit.")
        hdr.add_argument("--sender-id",
                         type=lambda s: int_in_range(s, DEFAULTS["sender_min"], DEFAULTS["sender_max"], "sender-id"),
                         default=1,
                         help="Originator ID (1-255). 0 is reserved for MCU unless firmware changed.")
        hdr.add_argument("--receiver-id",
                         type=lambda s: int_in_range(s, DEFAULTS["id_min"], DEFAULTS["id_max"], "receiver-id"),
                         default=1,
                         help="Receiver ID (0-255).")

        # ---- Payload sources (legacy) ----
        pay = parser.add_argument_group("payload (legacy sources)")
        pay.add_argument("--payload", type=parse_payload_list,
                         help="List of byte values (comma/space separated). Accepts 0x.., 0b.., decimal.")
        pay.add_argument("--payload-hex", type=parse_payload_hex,
                         help="Contiguous hex string (spaces allowed), e.g. 'DE AD BE EF'.")
        pay.add_argument("--payload-file", type=read_payload_file,
                         help="Read raw payload bytes from a file path.")
        pay.add_argument("--payload-fit", choices=["pad", "clip", "error"], default="pad",
                         help="Resolve size mismatch vs derived payload: pad with zeros, clip, or error.")

        # ---- Payload via struct.pack ----
        sp = parser.add_argument_group("payload (struct.pack)")
        sp.add_argument("--payload-pack",
                        help="Python 'struct' format string (little-endian implied if you start with '<').")
        sp.add_argument("--payload-args",
                        help="Python literal tuple/list with values for --payload-pack, e.g., \"(10, 'hello', 3.14)\".")
        sp.add_argument("--string-encoding", default="utf-8",
                        help="Encoding for str -> bytes if you use 's' fields in --payload-pack.")

        # ---- Payload via type-first schema (C-string defaults) ----
        sc = parser.add_argument_group("payload (type-first schema)")
        sc.add_argument(
            "--payload-schema",
            help=("Comma/space separated schema using natural names:\n"
                  "  - Scalars: int8,uint8,int16,uint16,int32,uint32,int64,uint64,float,double,bool\n"
                  "  - C-strings: string[N] / cstring[N] (NUL-terminated + zero-padded to N)\n"
                  "  - Raw bytes: bytes[N]\n"
                  "  - Padding:   pad[N]\n"
                  "  - Arrays:    <scalar>[M]\n"
                  "  - Raw blob:  struct (expects bytes; can use sentinel '__STRUCT__')"))
        sc.add_argument(
            "--payload-values",
            help=("Python literal tuple/list with values matching the schema, 1:1 with value-yielding fields.\n"
                  "Arrays expect a list/tuple of the declared length. "
                  "For 'struct', pass bytes *or* '__STRUCT__' to inject --struct-hex/--struct-file."))
        sc.add_argument("--struct-hex",
                        help="Optional hex string for substituting a 'struct' field when values contain '__STRUCT__'.")
        sc.add_argument("--struct-file",
                        help="Optional file path for substituting a 'struct' field when values contain '__STRUCT__'.")

        # ---- Transport selection ----
        tr = parser.add_argument_group("transport")
        tr.add_argument("--iface", choices=["uart", "tcp"], required=True, help="Select transport interface.")

        uart = parser.add_argument_group("uart")
        uart.add_argument("--uart-port", help="Serial port path, e.g. /dev/ttyUSB0 or COM3.")
        uart.add_argument("--baud", type=lambda s: positive_int(s, "baud"), default=115200)
        uart.add_argument("--bytesize", type=lambda s: int_in_range(s, 5, 8, "bytesize"), default=8)
        uart.add_argument("--parity", default="N", help="Parity: N (none), E, O, M, S.")
        uart.add_argument("--stopbits", type=float, default=1.0, help="Stop bits: 1, 1.5, 2.")
        uart.add_argument("--timeout", type=float, default=1.0, help="Read/write timeout (seconds).")

        tcp = parser.add_argument_group("tcp")
        tcp.add_argument("--host", default="127.0.0.1", help="Host/IP for TCP connection.")
        tcp.add_argument("--port", type=lambda s: int_in_range(s, 1, 65535, "port"), default=11111)
        tcp.add_argument("--tcp-timeout", type=float, default=1.0, help="Socket timeout (seconds).")

        # ---- Diagnostics ----
        diag = parser.add_argument_group("diagnostics")
        diag.add_argument("--show-derived", action="store_true",
                          help="Print derived sizes/fields after parsing.")

        self._parser = parser
        return parser

    def parse(self, args: List[str] | None = None) -> argparse.Namespace:
        if self._parser is None:
            self.build()
        assert self._parser is not None

        ns = self._parser.parse_args(args=args)

        # Interface & IDs
        validate_transport(ns)
        validate_ids(ns.sender_id, ns.receiver_id)

        # Header flags -> mask
        ns.flags_mask = parse_flags(ns.flags)

        # Task ID sizing & bounds
        ns.task_id_size = TASK_ID_TYPES[ns.task_id_type]
        max_task_val = (1 << (8 * ns.task_id_size)) - 1
        if not (0 <= ns.task_id <= max_task_val):
            raise argparse.ArgumentTypeError(
                f"--task-id {ns.task_id} does not fit into {ns.task_id_type} ({ns.task_id_size} bytes)."
            )

        # Derived sizes
        ns.payload_size, ns.checksum_size = derive_payload_size(
            ns.packet_kind, ns.packet_size, ns.task_id_size, ns.checksum, ns.word_bytes
        )

        # Ensure only one payload source among all five families
        require_one_payload_source(
            ns.payload, ns.payload_hex, ns.payload_file, ns.payload_pack, ns.payload_schema
        )

        provided: List[int] = []
        provided_len = 0

        # Legacy list / hex / file
        if ns.payload is not None:
            provided = ns.payload
        elif ns.payload_hex is not None:
            provided = ns.payload_hex
        elif ns.payload_file is not None:
            provided = ns.payload_file
        # struct.pack flow
        elif ns.payload_pack is not None:
            if not ns.payload_args:
                raise argparse.ArgumentTypeError("--payload-args is required when using --payload-pack.")
            values = ast.literal_eval(ns.payload_args)
            # Note: we allow users to omit '<' and still be LE by prepending it
            fmt = ns.payload_pack
            if not fmt.startswith(("<", ">", "!", "@", "=")):
                fmt = "<" + fmt
            try:
                blob = struct.pack(fmt, *(
                    v.encode(ns.string_encoding) if isinstance(v, str) else v
                    for v in (values if isinstance(values, (list, tuple)) else (values,))
                ))
            except struct.error as e:
                raise argparse.ArgumentTypeError(f"--payload-pack pack error: {e}") from e
            provided = list(blob)
        # Schema-based flow
        elif ns.payload_schema is not None:
            fields = parse_schema(ns.payload_schema)
            if not ns.payload_values:
                raise argparse.ArgumentTypeError("--payload-values is required with --payload-schema")
            vals = literal_tuple_or_list(ns.payload_values, "--payload-values")

            # Handle external struct blob if requested
            struct_blob = None
            if ns.struct_hex and ns.struct_file:
                raise argparse.ArgumentTypeError("Provide at most one of --struct-hex or --struct-file.")
            if ns.struct_hex:
                try:
                    struct_blob = bytes.fromhex("".join(ns.struct_hex.split()))
                except ValueError as e:
                    raise argparse.ArgumentTypeError(f"--struct-hex invalid hex: {e}") from e
            elif ns.struct_file:
                if not os.path.exists(ns.struct_file):
                    raise argparse.ArgumentTypeError(f"--struct-file not found: {ns.struct_file}")
                with open(ns.struct_file, "rb") as f:
                    struct_blob = f.read()

            blob = pack_schema(fields, vals, string_encoding=ns.string_encoding, struct_blob=struct_blob)
            provided = list(blob)
        else:
            provided = []

        provided_len = len(provided)

        # Reconcile to derived payload_size
        if provided_len == ns.payload_size:
            ns.payload_bytes = provided
        elif provided_len < ns.payload_size:
            if ns.payload_fit == "error":
                raise argparse.ArgumentTypeError(
                    f"Provided payload too short: {provided_len} < {ns.payload_size}."
                )
            ns.payload_bytes = provided + [0] * (ns.payload_size - provided_len)
        else:
            # provided_len > payload_size
            if ns.payload_fit == "error":
                raise argparse.ArgumentTypeError(
                    f"Provided payload too long: {provided_len} > {ns.payload_size}."
                )
            ns.payload_bytes = provided[:ns.payload_size]

        if ns.show_derived:
            print("=== Derived ===")
            print(f"  packet_kind : {ns.packet_kind}")
            print(f"  checksum    : {ns.checksum} ({ns.checksum_size} bytes)")
            print(f"  packet_size : {ns.packet_size} bytes (word={ns.word_bytes})")
            print(f"  task_id     : {ns.task_id} ({ns.task_id_type}, {ns.task_id_size} bytes)")
            print(f"  payload     : {ns.payload_size} bytes (provided {provided_len})")
            print(f"  flags_mask  : 0x{ns.flags_mask:02X}")
            print(f"  header.type : {ns.type}")
            print(f"  header.bits : enc={int(ns.encrypted)} frag={int(ns.fragmented)} "
                  f"prio={ns.priority} validated={int(ns.validated)} reserved={int(ns.reserved)}")
            print(f"  ids         : sender={ns.sender_id} receiver={ns.receiver_id}")

        return ns

