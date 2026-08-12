"""``Directive`` / ``CompletionReason`` -- mirror ``protocol/directive.hpp``
and ``completion_reason.hpp``.

One byte at the front of every request payload::

    bit:     7   6      5  4  3  2  1  0
         +---+---+---+---+---+---+---+---+
         |  command  |       reason       |
         +---+---+---+---+---+---+---+---+

The command is 2 bits (4 operations); the reason is 6 bits, which is exactly why
``completion_reason`` is capped at ``0x3F`` in the C++ header -- the pair fits one
byte with nothing wasted. ``reason`` is only meaningful for ``COMPLETE_TASK``;
every other command conventionally leaves it zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

_REASON_BITS = 6
_REASON_MASK = (1 << _REASON_BITS) - 1  # 0x3F


class Operation(IntEnum):
    """Which ``task_manager`` operation a request asks for."""

    REGISTER_TASK = 0
    PAUSE_TASK = 1
    RESUME_TASK = 2
    COMPLETE_TASK = 3


class CompletionReason(IntEnum):
    """Why a task is being concluded. Capped at 6 bits (``MAX``)."""

    FINISHED = 0x00
    ABORTED = 0x01
    USER_DEFINED_START = 0x10
    MAX = 0x3F


@dataclass(frozen=True)
class Directive:
    """The packed command+reason byte."""

    command: Operation
    reason: int = CompletionReason.FINISHED

    def __post_init__(self) -> None:
        if not 0 <= int(self.reason) <= CompletionReason.MAX:
            raise ValueError(
                f"completion reason 0x{int(self.reason):02X} does not fit the 6 bits "
                f"the directive byte reserves for it (max 0x{CompletionReason.MAX:02X})"
            )

    @property
    def raw(self) -> int:
        """The packed byte, ready to write to ``payload[0]``."""
        return (int(self.command) << _REASON_BITS) | (int(self.reason) & _REASON_MASK)

    @staticmethod
    def unpack(raw: int) -> "Directive":
        """Reads a directive back out of a payload byte."""
        return Directive(
            command=Operation(raw >> _REASON_BITS),
            reason=raw & _REASON_MASK,
        )


#: Placeholder id for topologies with no per-message addressing
#: (``ecomm::protocol::topology::point_to_point``); mirrors ``no_addressing_id``.
NO_ADDRESSING_ID = 0
