from dataclasses import dataclass
from typing import Dict, Optional

from etask.schema.errors.schema_shape_error import SchemaShapeError


#: Tier-facing budget names, and the generated constant each one becomes.
#: Instant commands are absent deliberately: they occupy no storage and never
#: survive the call that starts them, so there is nothing to bound.
_FIELDS = ("polled", "stateful")


@dataclass(frozen=True)
class Budget:
    """How many tasks of each managed tier may be live at once.

    The schema's optional ``budget:`` section. Each value sizes that tier's
    manager storage, which is held inline - so it is the tier's real memory
    cost, decided at compile time.

    A tier the user does not mention is ``None`` here, and the generator falls
    back to the sum of that tier's per-task ``concurrency``: every task running
    at its own limit simultaneously. That is the only bound the schema alone
    implies, and it is deliberately the pessimistic one - the framework will not
    guess a smaller number on the user's behalf, because how many tasks actually
    coexist is a property of the application, not of the schema.

    A declared budget is therefore always a *reduction*, justified by
    measurement. Declaring more than the sum is rejected: those slots could
    never be occupied, since every live task also holds one of its own type's
    reserved slots.
    """

    #: Max concurrently live polled/oneshot tasks, or None to use the tier sum.
    polled: Optional[int] = None

    #: Max concurrently live stateful tasks (running or suspended), or None.
    stateful: Optional[int] = None

    @staticmethod
    def parse(body: object) -> "Budget":
        """Builds a Budget from the schema's ``budget:`` mapping.

        @param body The raw value of the top-level ``budget:`` key.
        @return The parsed budget; unmentioned tiers stay ``None``.
        @throws SchemaShapeError If the section is not a mapping, names a tier
                that does not take a budget, or gives a non-positive value.
        """
        if not isinstance(body, dict):
            raise SchemaShapeError("budget", "'budget' must be a mapping of tier names to counts")

        unknown = [key for key in body if key not in _FIELDS]
        if unknown:
            raise SchemaShapeError(
                "budget",
                f"unknown budget {'entry' if len(unknown) == 1 else 'entries'} "
                f"{', '.join(repr(u) for u in sorted(unknown))}; "
                f"expected one of {', '.join(_FIELDS)}. "
                "An instant_task takes no budget: it occupies no storage and runs "
                "to completion inside the call that delivers it.",
            )

        values: Dict[str, Optional[int]] = {}
        for field in _FIELDS:
            values[field] = Budget.__parse_count(body[field], field) if field in body else None

        return Budget(**values)

    @staticmethod
    def __parse_count(raw: object, field: str) -> int:
        """Validates one tier's count.

        @param raw The declared value.
        @param field Which tier it belongs to, for the error message.
        @return The count.
        @throws SchemaShapeError If it is not a positive integer.
        """
        # bool is an int subclass, and `polled: true` is a mistake worth naming.
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise SchemaShapeError("budget", f"'{field}' must be an integer, got {raw!r}")

        if raw < 1:
            raise SchemaShapeError(
                "budget",
                f"'{field}' must be at least 1, got {raw}. A tier that may hold no "
                "live task cannot run one; remove the tier's tasks instead.",
            )

        return raw
