from __future__ import annotations
from enum import Enum
from typing import Optional


class Tier(Enum):
    """Which task tier a schema node declares - what the task *is*.

    A task pays for the lifecycle hooks its tier carries, so the tier is the
    single most consequential thing a task node says about itself. See
    ``etask/core/tasks/tasks.hpp`` for the C++ side.

    ============ ============================================ ================
    Tier         Hooks                                        Costs
    ============ ============================================ ================
    ``INSTANT``  none - the constructor is the whole task     no vtable, no
                                                              storage, no tick
    ``ONESHOT``  ``on_execute``, ``on_complete``               one tick
    ``POLLED``   + ``is_finished`` (the task decides)          polling
    ``STATEFUL`` + ``on_pause``, ``on_resume``                 suspension
    ============ ============================================ ================
    """

    INSTANT = "instant_task"
    ONESHOT = "oneshot_task"
    POLLED = "polled_task"
    STATEFUL = "stateful_task"

    @property
    def is_instant(self) -> bool:
        """Whether this is a fire-and-forget command: no completion, no reply."""
        return self is Tier.INSTANT

    @property
    def is_managed(self) -> bool:
        """Whether the manager owns the task across ticks and delivers a result.

        True for every tier but :attr:`INSTANT`. A managed task derives from
        ``etask::core::task``, occupies a registry slot, and concludes through a
        channel.
        """
        return self is not Tier.INSTANT

    @property
    def base_alias(self) -> str:
        """The project-local base class name a task of this tier derives from.

        These are the aliases emitted into the generated tree's ``task.hpp``,
        so a task file names only the alias and never the etask core template.
        """
        return self.value

    @property
    def has_execute(self) -> bool:
        """Whether tasks of this tier implement ``on_execute()``."""
        return self is not Tier.INSTANT

    @property
    def has_is_finished(self) -> bool:
        """Whether tasks of this tier implement ``is_finished()``.

        False for :attr:`ONESHOT`, whose ``is_finished()`` is sealed ``final``
        in the base - overriding it is a compile error, not a choice.
        """
        return self in (Tier.POLLED, Tier.STATEFUL)

    @property
    def has_suspension(self) -> bool:
        """Whether tasks of this tier implement ``on_pause()``/``on_resume()``."""
        return self is Tier.STATEFUL

    @property
    def can_return(self) -> bool:
        """Whether a task of this tier may declare ``returns:``.

        An instant command has no ``on_complete`` and sends no reply, so a
        result shape would describe something that never reaches anyone.
        """
        return self.is_managed

    @staticmethod
    def parse(raw: Optional[str]) -> Optional["Tier"]:
        """The tier a ``type:`` string names, or ``None`` if it names no tier.

        @param raw The schema's ``type:`` value.
        """
        for tier in Tier:
            if tier.value == raw:
                return tier
        return None

    @staticmethod
    def names() -> str:
        """The declarable tier names, for error messages."""
        return ", ".join(tier.value for tier in Tier)
