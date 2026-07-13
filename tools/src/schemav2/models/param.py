from dataclasses import dataclass
from typing import Optional

from schemav2.models.type_map import TypeMap


@dataclass
class Param:
    """A single task parameter or return value.

    ``name`` is ``None`` for positional (list-form) returns; ``type`` is always
    one of the schema types validated by :class:`TypeMap`.
    """

    type: str
    name: Optional[str] = None

    @property
    def cpp_type(self) -> str:
        return TypeMap.cpp_type(self.type)

    @property
    def wire_size(self) -> Optional[int]:
        return TypeMap.wire_size(self.type)
