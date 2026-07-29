from typing import List

from schemav2.models.node import Node
from schemav2.codegen.naming import Naming

# uid byte width (root.uid_bytes) -> the C++ underlying type of the enum. The
# width is chosen by the tree pass to fit every task's uid; the enum mirrors it
# so the on-wire task id and the enum storage are exactly the same size.
_UID_UNDERLYING = {
    1: "std::uint8_t",
    2: "std::uint16_t",
    4: "std::uint32_t",
    8: "std::uint64_t",
}

_NAMESPACE = "global"
_GUARD = "GLOBAL_TASK_ID_HPP_"


class TaskIdFile:
    """Renders ``task_id.hpp`` - the ``global::task_id`` enum.

    Unlike task scaffolds and contexts (generated once, then user-owned), this
    file is a pure projection of the schema's uid assignment and is **rewritten
    in full on every run**: one strongly-typed enumerator per task, keyed by its
    dotted path (``gripper.calibrate`` -> ``gripper_calibrate``) to the uid the
    tree pass assigned. Editing it by hand is pointless - the next generate
    overwrites it - which is exactly why the uid<->name binding is safe to trust.
    """

    @staticmethod
    def render(root: Node) -> str:
        underlying = _UID_UNDERLYING[root.uid_bytes]
        tasks = TaskIdFile.__collect_tasks(root)

        lines: List[str] = []
        lines.append("// SPDX-License-Identifier: MIT")
        lines.append("/**")
        lines.append("* @file task_id.hpp")
        lines.append("*")
        lines.append("* @brief Strongly-typed identifier for every task in the schema.")
        lines.append("*")
        lines.append("* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema")
        lines.append("*          on every `etask-gen generate` run; hand edits are overwritten.")
        lines.append("*          Each enumerator is named by the task's dotted schema path with")
        lines.append("*          `.` replaced by `_`, and valued with the uid the generator")
        lines.append("*          assigned (explicit in the schema, or path-hashed otherwise).")
        lines.append("*/")
        lines.append(f"#ifndef {_GUARD}")
        lines.append(f"#define {_GUARD}")
        lines.append("#include <cstdint>")
        lines.append("")
        lines.append(f"namespace {_NAMESPACE} {{")
        lines.append("")
        lines.append(f"    enum class task_id : {underlying} {{")
        # Pad the `symbol = value,` columns so any `///<` briefs line up.
        entries = [f"{Naming.uid_symbol(task)} = {task.uid}," for task in tasks]
        width = max((len(e) for e in entries), default=0)
        for task, entry in zip(tasks, entries):
            brief = task.doc_brief
            if brief:
                # A `///<` comment IS the member's @brief in Doxygen. Keep it to
                # one line - a brief promoted from a multi-line description could
                # otherwise span lines and break the comment.
                summary = brief.splitlines()[0].strip()
                lines.append(f"        {entry.ljust(width)}  ///< {summary}")
            else:
                lines.append(f"        {entry}")
        lines.append("    };")
        lines.append("")
        lines.append(f"}} // namespace {_NAMESPACE}")
        lines.append(f"#endif // {_GUARD}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def __collect_tasks(node: Node) -> List[Node]:
        tasks = [node] if node.is_task else []
        for child in node.children.values():
            tasks.extend(TaskIdFile.__collect_tasks(child))
        return tasks
