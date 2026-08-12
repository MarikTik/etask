from etask.schema.codegen.naming import Naming


class TaskBaseFile:
    """Renders ``task.hpp`` - the project's task base alias.

    Every generated task derives from ``task`` (defined here) rather than naming
    the etask core template directly, so a task file only ever mentions ``task``
    and ``global::task_id``. It lives at the **root of the generated tree** (next
    to the top ``context.hpp``), because that is where every task's
    ``#include "task.hpp"`` - one ``../`` per scope level - resolves to.

    It is emitted **once** and then owned by the user: it binds to the generated
    ``global::task_id`` enum but is not itself a projection of the schema, so it
    is created if missing and never overwritten (see :class:`Emitter`).
    """

    @staticmethod
    def render() -> str:
        guard = Naming.task_base_guard()
        ns = Naming.root_namespace()
        lines = [
            "/**",
            f"* @file {Naming.task_base_include()}",
            "*",
            "* @brief Project task base alias, bound to the generated task-id type.",
            "*",
            "* Every task scaffold in this tree derives from `task` (defined here).",
            "* Binding it once, here, keeps the generated task files free of any direct",
            "* dependency on the etask core template - they only ever name `task` and",
            "* `global::task_id`.",
            "*",
            "* @note Generated once by etask, then owned by you. The `global::task_id`",
            f"*       enum it binds to is generated from your schema (see",
            f"*       {Naming.task_id_include_from_root()}); this alias is not, and is never",
            "*       overwritten once it exists.",
            "*/",
            f"#ifndef {guard}",
            f"#define {guard}",
            "#include <etask/core/task.hpp>",
            f'#include "{Naming.task_id_include_from_root()}"',
            "",
            "/**",
            "* @brief The base class for every task in this project.",
            "*",
            "* An `etask::core::task` specialized on this project's generated task id type.",
            "*/",
            f"using task = etask::core::task<global::task_id>;",
            "",
            f"#endif // {guard}",
        ]
        return "\n".join(lines) + "\n"
