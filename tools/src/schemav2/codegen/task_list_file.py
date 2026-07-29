from typing import List, Tuple


_NAMESPACE = "generated"
_GUARD = "GENERATED_TASK_LIST_HPP_"


class TaskListFile:
    """Renders ``task_list.hpp`` - the set of task types as an ``etools::meta::typelist``.

    Like ``task_id.hpp`` (and unlike the task scaffolds), this is a pure
    projection of the schema and is **rewritten in full every run**. It is the
    generated half of the manager wiring: the user's config builds its manager
    from this list with ``etask::core::task_manager_from_t<generated::task_list>``,
    so the task set never has to be hand-maintained in a user-owned file.

    ``entries`` is one ``(include, qualified_type)`` pair per task, e.g.
    ``("../tasks/gripper/calibrate.hpp", "tasks::gripper::calibrate")`` - the
    emitter computes the include path relative to this file's location.
    """

    @staticmethod
    def render(entries: List[Tuple[str, str]]) -> str:
        lines: List[str] = []
        lines.append("// SPDX-License-Identifier: MIT")
        lines.append("/**")
        lines.append("* @file task_list.hpp")
        lines.append("*")
        lines.append("* @brief Every task type this application runs, as a typelist.")
        lines.append("*")
        lines.append("* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema")
        lines.append("*          on every `etask-gen generate` run; hand edits are overwritten.")
        lines.append("*          Build the task manager from it in your config, e.g.")
        lines.append("*          `using manager_t = etask::core::task_manager_from_t<generated::task_list>;`.")
        lines.append("*/")
        lines.append(f"#ifndef {_GUARD}")
        lines.append(f"#define {_GUARD}")
        lines.append("#include <etools/meta/typelist.hpp>")
        for include, _ in entries:
            lines.append(f'#include "{include}"')
        lines.append("")
        lines.append(f"namespace {_NAMESPACE} {{")
        lines.append("")
        if entries:
            lines.append("    using task_list = etools::meta::typelist<")
            for i, (_, qualified) in enumerate(entries):
                comma = "," if i < len(entries) - 1 else ""
                lines.append(f"        {qualified}{comma}")
            lines.append("    >;")
        else:
            # No tasks yet: an empty list is still well-formed; the manager's own
            # static_assert (>= 1 task) is what flags a genuinely empty project.
            lines.append("    using task_list = etools::meta::typelist<>;")
        lines.append("")
        lines.append(f"}} // namespace {_NAMESPACE}")
        lines.append(f"#endif // {_GUARD}")
        return "\n".join(lines) + "\n"
