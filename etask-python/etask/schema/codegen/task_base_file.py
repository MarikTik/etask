from etask.schema.codegen.naming import Naming
from etask.schema.models.tier import Tier


class TaskBaseFile:
    """Renders ``task.hpp`` - the project's task base aliases.

    Every generated task derives from one of the aliases defined here rather
    than naming an etask core template directly, so a task file only ever
    mentions its tier's short name and ``global::task_id``. It lives at the
    **root of the generated tree** (next to the top ``context.hpp``), because
    that is where every task's ``#include "task.hpp"`` - one ``../`` per scope
    level - resolves to.

    It is emitted **once** and then owned by the user: it binds to the generated
    ``global::task_id`` enum but is not itself a projection of the schema, so it
    is created if missing and never overwritten (see :class:`Emitter`).

    .. note::
       Because it is never overwritten, a project generated before the task
       tiers existed keeps its old single ``task`` alias and will not compile
       against the new tiers. :class:`Emitter` detects that and reports it,
       rather than silently rewriting a user-owned file.
    """

    #: Per-tier: the alias name, the core template it binds to, and why it exists.
    _ALIASES = (
        (
            Tier.INSTANT.base_alias,
            "etask::core::instant_task",
            [
                "A fire-and-forget command: it runs to completion inside the call that",
                "delivers it, then is destroyed. No lifecycle hooks, no vtable, no",
                "storage, no reply. Not a class template - it has no uid type to bind,",
                "because it has no virtual to dispatch.",
            ],
        ),
        (
            Tier.ONESHOT.base_alias,
            "etask::core::oneshot_task<global::task_id>",
            [
                "Runs once and answers: on_execute() then on_complete(). is_finished()",
                "is sealed true, so the 'runs once' guarantee cannot be edited away.",
            ],
        ),
        (
            Tier.POLLED.base_alias,
            "etask::core::polled_task<global::task_id>",
            [
                "Runs across ticks and decides for itself when it is done, via",
                "is_finished(). Cannot be paused - that is a stateful_task.",
            ],
        ),
        (
            Tier.STATEFUL.base_alias,
            "etask::core::stateful_task<global::task_id>",
            [
                "A polled task that can be suspended: on_pause() and on_resume()",
                "bracket a pause, and both are required, because deriving from this",
                "tier is a claim that the task holds something needing them.",
            ],
        ),
    )

    @staticmethod
    def render() -> str:
        guard = Naming.task_base_guard()
        lines = [
            "/**",
            f"* @file {Naming.task_base_include()}",
            "*",
            "* @brief Project task base aliases, bound to the generated task-id type.",
            "*",
            "* Every task scaffold in this tree derives from one of the aliases defined",
            "* here. Binding them once, in one place, keeps the generated task files free",
            "* of any direct dependency on the etask core templates - they name only the",
            "* tier and `global::task_id`.",
            "*",
            "* A task's tier is what it *is*, and decides which lifecycle hooks it carries",
            "* and what it costs:",
            "*",
            "* | Alias           | Hooks                                    | Costs         |",
            "* |-----------------|------------------------------------------|---------------|",
            "* | `instant_task`  | none - the constructor is the task       | nothing       |",
            "* | `oneshot_task`  | on_execute, on_complete                  | one tick      |",
            "* | `polled_task`   | + is_finished                            | polling       |",
            "* | `stateful_task` | + on_pause, on_resume                    | suspension    |",
            "*",
            "* @note Generated once by etask, then owned by you. The `global::task_id`",
            "*       enum these bind to is generated from your schema (see",
            f"*       {Naming.task_id_include_from_root()}); this file is not, and is never",
            "*       overwritten once it exists.",
            "*/",
            f"#ifndef {guard}",
            f"#define {guard}",
            "#include <etask/core/tasks/tasks.hpp>",
            f'#include "{Naming.task_id_include_from_root()}"',
        ]
        for alias, target, description in TaskBaseFile._ALIASES:
            lines.append("")
            lines.append("/**")
            lines.append(f"* @brief {description[0]}")
            for extra in description[1:]:
                lines.append(f"* {extra}")
            lines.append("*/")
            lines.append(f"using {alias:<13} = {target};")
        lines.append("")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines) + "\n"
