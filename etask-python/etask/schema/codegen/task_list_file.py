from typing import Dict, List, Tuple

from etask.schema.models.tier import Tier


_NAMESPACE = "generated"
_GUARD = "GENERATED_TASK_LIST_HPP_"

#: Emission order, and the list name each tier gets.
_LISTS = (
    (Tier.INSTANT, "instant_tasks", "fire-and-forget commands: no storage, no reply"),
    (Tier.ONESHOT, "polled_tasks", None),      # oneshot IS a polled task - same manager
    (Tier.POLLED, "polled_tasks", None),
    (Tier.STATEFUL, "stateful_tasks", "tasks that can be paused and resumed"),
)

#: Which list name each tier's tasks land in.
_LIST_FOR_TIER: Dict[Tier, str] = {tier: name for tier, name, _ in _LISTS}

#: The lists themselves, in emission order, without duplicates.
_LIST_NAMES = ("instant_tasks", "polled_tasks", "stateful_tasks")

#: Managed tiers get a budget constant; instant commands occupy no storage, so
#: there is nothing to bound and emitting one would imply a guarantee the tier
#: does not make.
_BUDGETS: Dict[str, str] = {
    "polled_tasks": "polled_budget",
    "stateful_tasks": "stateful_budget",
}

_LIST_DOCS = {
    "instant_tasks": [
        "Fire-and-forget commands (`instant_task`).",
        "",
        "Run to completion inside the call that delivers them: no storage, no",
        "tick, no reply. Dispatched by `instant_task_manager`.",
    ],
    "polled_tasks": [
        "Tasks driven across ticks (`polled_task`, `oneshot_task`).",
        "",
        "Owned by `polled_task_manager`, which executes them until they report",
        "themselves finished, then delivers the result. A `oneshot_task` belongs",
        "here too - it is a polled task whose completion predicate is sealed.",
    ],
    "stateful_tasks": [
        "Tasks that can be suspended (`stateful_task`).",
        "",
        "Owned by `stateful_task_manager`: everything the polled manager does,",
        "plus honoring pause and resume.",
    ],
}


class TaskListFile:
    """Renders ``task_list.hpp`` - the project's task types, split by tier.

    Like ``task_id.hpp`` (and unlike the task scaffolds), this is a pure
    projection of the schema and is **rewritten in full every run**. It is the
    generated half of the manager wiring: the user's config builds its manager
    from these lists, so the task set never has to be hand-maintained in a
    user-owned file.

    Three lists rather than one, because the three tiers are run by three
    different managers. A tier with no tasks emits an empty typelist, which the
    façade turns into no machinery at all - so a project of pure commands
    carries no polling loop.

    Alongside each managed tier's list, a **budget** constant: the number of
    tasks of that tier that may be live at once, which sizes the manager's
    inline record storage. The value emitted is the sum of the tier's per-task
    concurrency reservations - the state where every task runs at its own limit
    simultaneously, and so the only bound derivable from the schema alone. A
    project that has measured a lower real peak should lower it and save the
    storage; the manager rejects a budget above this sum, since the extra slots
    could never be filled.

    ``entries`` is one ``(include, type_expr, tier, slots)`` tuple per task,
    where ``type_expr`` is the task's type (bare, or wrapped in
    ``capacity<T, N>`` when it declares concurrency) and ``slots`` is that same
    reservation as a number; the emitter computes the include path relative to
    this file's location.
    """

    @staticmethod
    def render(entries: List[Tuple[str, str, Tier, int]]) -> str:
        by_list: Dict[str, List[str]] = {name: [] for name in _LIST_NAMES}
        budgets: Dict[str, int] = {name: 0 for name in _LIST_NAMES}
        for _, type_expr, tier, slots in entries:
            name = _LIST_FOR_TIER[tier]
            by_list[name].append(type_expr)
            budgets[name] += slots

        lines: List[str] = []
        lines.extend(TaskListFile.__header())
        lines.append(f"#ifndef {_GUARD}")
        lines.append(f"#define {_GUARD}")
        lines.append("#include <etools/meta/typelist.hpp>")
        if any("capacity<" in type_expr for _, type_expr, _, _ in entries):
            lines.append("#include <etools/factories/utils/capacity.hpp>")
        lines.append("#include <cstddef>")
        for include, _, _, _ in entries:
            lines.append(f'#include "{include}"')
        lines.append("")
        lines.append(f"namespace {_NAMESPACE} {{")
        for name in _LIST_NAMES:
            lines.append("")
            lines.extend(TaskListFile.__list(name, by_list[name]))
            if name in _BUDGETS:
                lines.append("")
                lines.extend(TaskListFile.__budget(name, budgets[name]))
        lines.append("")
        lines.append(f"}} // namespace {_NAMESPACE}")
        lines.append(f"#endif // {_GUARD}")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------ parts

    @staticmethod
    def __header() -> List[str]:
        return [
            "/**",
            "* @file task_list.hpp",
            "*",
            "* @brief Every task type this application runs, split by tier.",
            "*",
            "* A task's tier decides which manager owns it, so the schema's tasks arrive",
            "* here as three lists rather than one. A tier with no tasks is an empty",
            "* typelist, and the façade instantiates nothing for it.",
            "*",
            "* Each managed tier also carries a budget: how many of its tasks may be live",
            "* at once, which sizes that manager's inline storage.",
            "*",
            "* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema",
            "*          on every generate; hand edits are overwritten. Regenerate via the",
            "*          CMake `etask-generate` target, or `etask generate`.",
            "*          Build the task manager from these in your config:",
            "*          `using manager_t = etask::core::managers::task_manager_from_t<`",
            "*          `    generated::instant_tasks,`",
            "*          `    generated::polled_tasks,`",
            "*          `    generated::stateful_tasks,`",
            "*          `    generated::polled_budget,`",
            "*          `    generated::stateful_budget>;`",
            "*/",
        ]

    @staticmethod
    def __budget(list_name: str, total: int) -> List[str]:
        """Renders one tier's budget constant, with the reasoning inline."""
        const = _BUDGETS[list_name]
        tier = "polled" if const == "polled_budget" else "stateful"
        extra = (
            "A suspended task still holds its record, so this tier fills up on "
            "paused tasks as surely as on running ones."
            if tier == "stateful"
            else "One record per live task, held inline - no heap."
        )
        lines = [
            "    /**",
            f"    * @brief How many {tier} tasks may be live at once.",
            "    *",
            "    * Sizes the manager's inline record storage, so it is the tier's real",
            "    * memory cost. " + extra,
            "    *",
            "    * This is the sum of every task's `concurrency` in this tier - every task",
            "    * running at its own limit simultaneously, which is the only bound the",
            "    * schema alone implies. Most devices never approach it: measure your real",
            "    * peak and set `budget:` in the schema to save the difference. The manager",
            "    * rejects a budget above this sum, since the extra slots could never fill.",
            "    */",
            f"    inline constexpr std::size_t {const} = {total};",
        ]
        return lines

    @staticmethod
    def __list(name: str, type_exprs: List[str]) -> List[str]:
        lines: List[str] = ["    /**"]
        doc = _LIST_DOCS[name]
        lines.append(f"    * @brief {doc[0]}")
        for extra in doc[1:]:
            lines.append(f"    * {extra}" if extra else "    *")
        if not type_exprs:
            lines.append("    *")
            lines.append("    * This project declares none, so nothing is generated for this tier.")
        lines.append("    */")
        if not type_exprs:
            lines.append(f"    using {name} = etools::meta::typelist<>;")
            return lines
        lines.append(f"    using {name} = etools::meta::typelist<")
        for i, type_expr in enumerate(type_exprs):
            comma = "," if i < len(type_exprs) - 1 else ""
            lines.append(f"        {type_expr}{comma}")
        lines.append("    >;")
        return lines
