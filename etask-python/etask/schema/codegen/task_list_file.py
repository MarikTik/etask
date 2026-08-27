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

    ``entries`` is one ``(include, type_expr, tier)`` triple per task, where
    ``type_expr`` is the task's type (bare, or wrapped in ``capacity<T, N>``
    when it declares concurrency); the emitter computes the include path
    relative to this file's location.
    """

    @staticmethod
    def render(entries: List[Tuple[str, str, Tier]]) -> str:
        by_list: Dict[str, List[str]] = {name: [] for name in _LIST_NAMES}
        for _, type_expr, tier in entries:
            by_list[_LIST_FOR_TIER[tier]].append(type_expr)

        lines: List[str] = []
        lines.extend(TaskListFile.__header())
        lines.append(f"#ifndef {_GUARD}")
        lines.append(f"#define {_GUARD}")
        lines.append("#include <etools/meta/typelist.hpp>")
        if any("capacity<" in type_expr for _, type_expr, _ in entries):
            lines.append("#include <etools/factories/utils/capacity.hpp>")
        for include, _, _ in entries:
            lines.append(f'#include "{include}"')
        lines.append("")
        lines.append(f"namespace {_NAMESPACE} {{")
        for name in _LIST_NAMES:
            lines.append("")
            lines.extend(TaskListFile.__list(name, by_list[name]))
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
            "* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema",
            "*          on every generate; hand edits are overwritten. Regenerate via the",
            "*          CMake `etask-generate` target, or `etask generate`.",
            "*          Build the task manager from these in your config:",
            "*          `using manager_t = etask::core::managers::task_manager_from_t<`",
            "*          `    generated::instant_tasks,`",
            "*          `    generated::polled_tasks,`",
            "*          `    generated::stateful_tasks>;`",
            "*/",
        ]

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
