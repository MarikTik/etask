"""``StatusCode`` -- mirrors ``etask/core/status_code.hpp``.

The single byte a reply carries at payload offset ``sizeof(task_uid)``. It says
how the request ended and, when a task declares more than one result shape,
*which shape the remaining bytes are*.

Three ranges, exactly as in the C++ header:

- ``0x00-0x1F`` manager/API -- the manager rejected the request and no task ran,
  so the reply has no result bytes. ``ok`` additionally serves as ``outcome``'s
  "the task chose no status" sentinel and never appears on a completion reply.
- ``0x20-0x6F`` task/runtime -- how a task that actually ran ended.
- ``0x70-0xFF`` custom -- yours.
"""

from __future__ import annotations

from enum import IntEnum


class StatusCode(IntEnum):
    """Unified status space used in packets and API returns."""

    # --- manager / API (0x00-0x1F) ---
    OK = 0x00
    TASK_NOT_REGISTERED = 0x01
    TASK_ALREADY_RUNNING = 0x02
    TASK_ALREADY_PAUSED = 0x03
    TASK_ALREADY_RESUMED = 0x04
    TASK_NOT_PAUSED = 0x05
    TASK_NOT_RUNNING = 0x06
    INVALID_STATE_TRANSITION = 0x07
    TASK_ALREADY_FINISHED = 0x08
    TASK_ALREADY_CONCLUDING = 0x09
    PERMISSION_DENIED = 0x0A
    WOULD_BLOCK = 0x0B
    REENTRANCY_CONFLICT = 0x0C
    CHANNEL_NULL = 0x0D
    CHANNEL_ERROR = 0x0E
    CONSTRUCTOR_NOT_FOUND = 0x0F
    INVALID_PARAMS = 0x10
    OUT_OF_MEMORY = 0x11
    TASK_LIMIT_REACHED = 0x12
    DUPLICATE_TASK = 0x13
    TASK_UNKNOWN = 0x14
    INVALID_COMPLETION_REASON = 0x15
    TASK_NOT_PAUSABLE = 0x16
    TASK_NOT_ADDRESSABLE = 0x17
    TASK_BUDGET_EXHAUSTED = 0x18
    SCHEMA_MISMATCH = 0x19
    INTERNAL_ERROR = 0x1F

    # --- task / runtime (0x20-0x6F) ---
    TASK_FINISHED = 0x20
    TASK_ABORTED = 0x21
    TASK_TIMEOUT = 0x22
    TASK_IO_ERROR = 0x23
    TASK_VALIDATION_FAILED = 0x24
    TASK_DEPENDENCY_MISSING = 0x25
    TASK_BUSY = 0x26
    RESULT_TOO_LARGE = 0x27
    TASK_COMPLETED_EARLY = 0x28

    # --- custom (0x70-0xFF) ---
    CUSTOM_ERROR_START = 0x70

    @property
    def is_manager(self) -> bool:
        """Whether this code means "the manager refused; no task ran"."""
        return self.value < 0x20

    @property
    def is_task(self) -> bool:
        """Whether this code describes how a task that ran ended."""
        return 0x20 <= self.value < StatusCode.CUSTOM_ERROR_START

    @property
    def is_custom(self) -> bool:
        return self.value >= StatusCode.CUSTOM_ERROR_START


def status_name(code: int) -> str:
    """A readable name for any status byte, including unlisted custom ones."""
    try:
        return StatusCode(code).name.lower()
    except ValueError:
        if code >= StatusCode.CUSTOM_ERROR_START:
            return f"custom(0x{code:02X})"
        return f"unknown(0x{code:02X})"
