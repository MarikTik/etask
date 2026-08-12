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

    ``entries`` is one ``(include, type_expr)`` pair per task, where ``type_expr``
    is the task's type (bare, or wrapped in ``capacity<T, N>`` when it declares
    concurrency), e.g. ``("../tasks/gripper/calibrate.hpp", "tasks::gripper::calibrate")`` - the
    emitter computes the include path relative to this file's location.
    """

    @staticmethod
    def render(entries: List[Tuple[str, str]]) -> str:
        lines: List[str] = []
        lines.append("/**")
        lines.append("* @file task_list.hpp")
        lines.append("*")
        lines.append("* @brief Every task type this application runs, as a typelist.")
        lines.append("*")
        lines.append("* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema")
        lines.append("*          on every generate; hand edits are overwritten. Regenerate via the")
        lines.append("*          CMake `etask-generate` target, or `etask generate`.")
        lines.append("*          Build the task manager from it in your config, e.g.")
        lines.append("*          `using manager_t = etask::core::task_manager_from_t<generated::task_list>;`.")
        lines.append("*/")
        lines.append(f"#ifndef {_GUARD}")
        lines.append(f"#define {_GUARD}")
        lines.append("#include <etools/meta/typelist.hpp>")
        # Only pulled in when a task declares concurrency > 1 (capacity<T, N>).
        if any("capacity<" in type_expr for _, type_expr in entries):
            lines.append("#include <etools/factories/utils/capacity.hpp>")
        for include, _ in entries:
            lines.append(f'#include "{include}"')
        lines.append("")
        lines.append(f"namespace {_NAMESPACE} {{")
        lines.append("")
        if entries:
            lines.append("    using task_list = etools::meta::typelist<")
            for i, (_, type_expr) in enumerate(entries):
                comma = "," if i < len(entries) - 1 else ""
                lines.append(f"        {type_expr}{comma}")
            lines.append("    >;")
        else:
            # No tasks yet: an empty list is still well-formed; the manager's own
            # static_assert (>= 1 task) is what flags a genuinely empty project.
            lines.append("    using task_list = etools::meta::typelist<>;")
        lines.append("")
        lines.append(f"}} // namespace {_NAMESPACE}")
        lines.append(f"#endif // {_GUARD}")
        return "\n".join(lines) + "\n"
