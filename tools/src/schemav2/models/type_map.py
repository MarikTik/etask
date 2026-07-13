from typing import Dict, Optional


class TypeMap:
    """Allowed schema parameter/return types and their C++ lowering.

    The wire codec is tagless and flat (positional), so every fixed-width type
    also carries the number of bytes it occupies on the wire. ``string`` is
    variable-length and therefore has no fixed wire size (``None``).
    """

    # schema type -> (C++ type, fixed wire size in bytes or None if variable)
    _TYPES: Dict[str, "tuple[str, Optional[int]]"] = {
        "int": ("std::int32_t", 4),
        "int8": ("std::int8_t", 1),
        "int16": ("std::int16_t", 2),
        "int32": ("std::int32_t", 4),
        "int64": ("std::int64_t", 8),
        "uint8": ("std::uint8_t", 1),
        "uint16": ("std::uint16_t", 2),
        "uint32": ("std::uint32_t", 4),
        "uint64": ("std::uint64_t", 8),
        "float": ("float", 4),
        "double": ("double", 8),
        "bool": ("bool", 1),
        "string": ("const char*", None),
    }

    @staticmethod
    def is_valid(schema_type: str) -> bool:
        return schema_type in TypeMap._TYPES

    @staticmethod
    def cpp_type(schema_type: str) -> str:
        return TypeMap._TYPES[schema_type][0]

    @staticmethod
    def wire_size(schema_type: str) -> Optional[int]:
        return TypeMap._TYPES[schema_type][1]

    @staticmethod
    def allowed() -> "list[str]":
        return list(TypeMap._TYPES.keys())
