"""The flat, tagless value codec -- the Python side of ``eser::flat``.

Values are laid out back to back in declaration order, little-endian, with no
tags, no names, and no length prefixes: the *schema* is the only thing that says
what the bytes mean. That is why the schema restricts itself to fixed-size types,
and why the order of ``params:`` / ``returns:`` is a wire contract rather than a
stylistic choice.

Little-endian is not a guess: ``eser::flat::serializer`` defaults to
``endianness::little`` (see ``serializer.hpp``), which is also what ecomm-python
already uses for header fields.
"""

from __future__ import annotations

import struct
from typing import Any, Dict, Sequence, Tuple

#: schema type name -> (struct format char, wire size in bytes)
#: Transcribed from ``schemav2.models.type_map.TypeMap``; the two must agree, and
#: a test asserts they do.
_FORMATS: Dict[str, Tuple[str, int]] = {
    "int": ("i", 4),
    "int8": ("b", 1),
    "int16": ("h", 2),
    "int32": ("i", 4),
    "int64": ("q", 8),
    "uint8": ("B", 1),
    "uint16": ("H", 2),
    "uint32": ("I", 4),
    "uint64": ("Q", 8),
    "float": ("f", 4),
    "double": ("d", 8),
    "bool": ("?", 1),
}


class UnknownWireType(ValueError):
    """Raised for a schema type this codec has no encoding for."""

    def __init__(self, type_name: str):
        super().__init__(
            f"unknown wire type '{type_name}'; known types: {', '.join(sorted(_FORMATS))}"
        )
        self.type_name = type_name


def struct_format(types: Sequence[str]) -> str:
    """The little-endian ``struct`` format string for a list of schema types."""
    out = ["<"]
    for name in types:
        entry = _FORMATS.get(name)
        if entry is None:
            raise UnknownWireType(name)
        out.append(entry[0])
    return "".join(out)


def wire_size(types: Sequence[str]) -> int:
    """Total bytes the given types occupy on the wire."""
    total = 0
    for name in types:
        entry = _FORMATS.get(name)
        if entry is None:
            raise UnknownWireType(name)
        total += entry[1]
    return total


def pack(types: Sequence[str], values: Sequence[Any]) -> bytes:
    """Serializes ``values`` as ``types``, in order."""
    if len(types) != len(values):
        raise ValueError(
            f"expected {len(types)} value(s) for types {list(types)}, got {len(values)}"
        )
    return struct.pack(struct_format(types), *values)


def unpack(types: Sequence[str], data: bytes) -> Tuple[Any, ...]:
    """Deserializes ``types`` from the front of ``data``.

    Trailing bytes are ignored: a reply's result region is the whole remaining
    payload, zero-padded past the values the task actually wrote.
    """
    needed = wire_size(types)
    if len(data) < needed:
        raise ValueError(
            f"need {needed} byte(s) to decode {list(types)}, got {len(data)}"
        )
    return struct.unpack_from(struct_format(types), data, 0)


def is_known(type_name: str) -> bool:
    return type_name in _FORMATS


def known_types() -> "list[str]":
    return sorted(_FORMATS)
