"""The status codes a schema may key a result shape on.

Mirrors ``etask/core/status_code.hpp``. A task's reply carries one status byte,
and that byte is what tells a peer *which* result shape it is holding - so the
schema has to name the same codes the firmware does, by the same names.

Three ranges, and only two of them are a task's to claim (this is the schema-side
statement of the assert in ``outcome::with_status``):

- **manager/API** (``0x00-0x1F``) means "the manager rejected the request, no task
  ran". A completing task never sends one, so a schema cannot declare a shape for
  one. That includes ``ok``, which is precisely the value ``outcome`` uses to say
  *no status was chosen*.
- **task/runtime** (``0x20-0x6F``) is the normal space: ``finished``, ``aborted``,
  ``task_timeout``, and friends.
- **custom** (``0x70-0xFF``) is yours, written ``custom(0x71)``.

``finished`` and ``aborted`` are aliases for ``task_finished`` / ``task_aborted``
- the two the manager itself sends - because they are what most schemas write and
the ``task_`` prefix adds nothing at the point of use.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

_CUSTOM_RE = re.compile(r"^custom\(\s*(0[xX][0-9a-fA-F]+|\d+)\s*\)$")

#: Framework-owned codes a schema must not declare a shape for, with the reason.
_RESERVED: Dict[str, str] = {
    "result_too_large": (
        "the framework emits it with an empty result when a task's values do not "
        "fit the packet, so a declared shape could never arrive"
    ),
}


class StatusCode:
    """The ``status_code`` enumerators, as the schema is allowed to name them."""

    #: enumerator name -> numeric value (transcribed from status_code.hpp)
    _CODES: Dict[str, int] = {
        # manager / API (0x00-0x1F) - listed so they can be rejected by name
        # rather than by a bare "unknown status" message.
        "ok": 0x00,
        "task_not_registered": 0x01,
        "task_already_running": 0x02,
        "task_already_paused": 0x03,
        "task_already_resumed": 0x04,
        "task_not_paused": 0x05,
        "task_not_running": 0x06,
        "invalid_state_transition": 0x07,
        "task_already_finished": 0x08,
        "task_already_concluding": 0x09,
        "permission_denied": 0x0A,
        "would_block": 0x0B,
        "reentrancy_conflict": 0x0C,
        "channel_null": 0x0D,
        "channel_error": 0x0E,
        "constructor_not_found": 0x0F,
        "invalid_params": 0x10,
        "out_of_memory": 0x11,
        "task_limit_reached": 0x12,
        "duplicate_task": 0x13,
        "task_unknown": 0x14,
        "invalid_completion_reason": 0x15,
        "task_not_pausable": 0x16,
        "task_not_addressable": 0x17,
        "task_budget_exhausted": 0x18,
        "schema_mismatch": 0x19,
        "internal_error": 0x1F,
        # task / runtime (0x20-0x6F)
        "task_finished": 0x20,
        "task_aborted": 0x21,
        "task_timeout": 0x22,
        "task_io_error": 0x23,
        "task_validation_failed": 0x24,
        "task_dependency_missing": 0x25,
        "task_busy": 0x26,
        "result_too_large": 0x27,
        "task_completed_early": 0x28,
    }

    #: schema-facing alias -> enumerator name
    _ALIASES: Dict[str, str] = {
        "finished": "task_finished",
        "aborted": "task_aborted",
    }

    #: The shape a bare ``returns:`` (no status keys) describes.
    DEFAULT_KEY = "finished"

    CUSTOM_START = 0x70

    @staticmethod
    def is_manager(code: int) -> bool:
        return code < 0x20

    @staticmethod
    def is_custom(code: int) -> bool:
        return code >= StatusCode.CUSTOM_START

    @staticmethod
    def resolve(key: str) -> Optional[Tuple[str, int]]:
        """Maps a schema key to ``(enumerator name, value)``, or ``None``.

        Accepts an enumerator name, one of the friendly aliases, or the
        ``custom(0x71)`` form. Returning ``None`` means "not a status at all" -
        the caller decides whether that is an error or (for a bare ``returns:``)
        simply a value name.
        """
        alias = StatusCode._ALIASES.get(key)
        if alias is not None:
            return alias, StatusCode._CODES[alias]
        if key in StatusCode._CODES:
            return key, StatusCode._CODES[key]
        match = _CUSTOM_RE.match(key)
        if match is None:
            return None
        value = int(match.group(1), 0)
        if not (StatusCode.CUSTOM_START <= value <= 0xFF):
            return None
        return f"custom(0x{value:02X})", value

    @staticmethod
    def looks_like_status(key: str) -> bool:
        """Whether a key is *meant* as a status, even an unusable one.

        Used to tell "you named a status we reject" apart from "you wrote a value
        name", so the error message can be the specific one.
        """
        return (
            key in StatusCode._CODES
            or key in StatusCode._ALIASES
            or key.startswith("custom(")
        )

    @staticmethod
    def rejection_reason(name: str, code: int) -> Optional[str]:
        """Why this code may not key a result shape, or ``None`` if it may."""
        if name in _RESERVED:
            return f"'{name}' is reserved by the framework: {_RESERVED[name]}"
        if StatusCode.is_manager(code):
            return (
                f"'{name}' (0x{code:02X}) is a manager/API status, which means the "
                "manager rejected the request and no task ran - a completing task "
                "can never send it (see outcome::with_status)"
            )
        return None

    @staticmethod
    def declarable() -> "list[str]":
        """Every key a schema may legitimately use, for error messages."""
        names = [
            name for name, code in StatusCode._CODES.items()
            if not StatusCode.is_manager(code) and name not in _RESERVED
        ]
        return sorted(StatusCode._ALIASES) + sorted(names) + ["custom(0xNN)"]

    @staticmethod
    def cpp_enumerator(name: str, code: int) -> str:
        """How the code is written in generated C++."""
        if name.startswith("custom("):
            return f"static_cast<etask::core::status_code>(0x{code:02X})"
        return f"etask::core::status_code::{name}"
