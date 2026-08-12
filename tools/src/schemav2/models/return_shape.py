from dataclasses import dataclass, field
from typing import List

from schemav2.models.param import Param
from schemav2.models.status_code import StatusCode


@dataclass
class ReturnShape:
    """One result shape, and the status byte that identifies it on the wire.

    A task's reply is ``[uid][status_code][result…]``. The status byte is
    therefore already a discriminator - it costs nothing extra to let a task
    return *different* values depending on how it ended, as long as the schema
    says which shape goes with which status. That is what this type records.

    A task with a plain ``returns:`` has exactly one shape, keyed
    :data:`StatusCode.DEFAULT_KEY` (``finished``), because an unadorned
    completion carries the manager's ``task_finished``.
    """

    #: The key as the schema writes it (``finished``, ``task_io_error``, ``custom(0x71)``).
    key: str
    #: The ``status_code`` enumerator this key resolves to.
    name: str
    #: The numeric status byte on the wire.
    code: int
    #: The values carried with this status, in wire order.
    values: List[Param] = field(default_factory=list)

    @property
    def is_default(self) -> bool:
        """Whether this is the shape of an ordinary, natural completion."""
        return self.name == "task_finished"

    @property
    def cpp_enumerator(self) -> str:
        return StatusCode.cpp_enumerator(self.name, self.code)

    @property
    def wire_size(self) -> int:
        """Bytes this shape occupies in the reply's result region."""
        return sum(value.wire_size or 0 for value in self.values)

    def label(self, index: int) -> str:
        """Display name of the value at ``index`` (its name, or ``[i]``)."""
        value = self.values[index]
        return value.name if value.name else f"[{index}]"
