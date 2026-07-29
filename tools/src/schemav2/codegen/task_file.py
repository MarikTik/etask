from typing import List

from schemav2.models.node import Node
from schemav2.codegen.naming import Naming

# Lifecycle hooks scaffolded as void overrides. is_finished and on_complete are
# handled separately (they have non-void returns and richer docs).
_VOID_HOOKS = ("on_start", "on_execute", "on_pause", "on_resume")

# Framework-authored documentation for each lifecycle override. Task-agnostic:
# it describes the manager's contract for that hook and when a task should fill
# it in, so a freshly generated task reads as self-documenting even before the
# user writes a line of logic. Each value is the body of a doc comment (lines
# without the leading `* `); an empty string renders a blank doc line.
_HOOK_DOCS = {
    "on_start": [
        "@brief One-time setup, run once before the first on_execute().",
        "",
        "Acquire hardware, latch constructor parameters into working state, arm",
        "timers. Runs exactly once per instance, before any execute/pause/resume.",
        "Leave empty if the task needs no setup.",
    ],
    "on_execute": [
        "@brief One slice of work, run every update() tick while the task runs.",
        "",
        "Called repeatedly by the manager and must not block: do a little and",
        "return so other tasks get their turn. Keeps running until is_finished()",
        "returns true or the task is completed externally.",
    ],
    "on_pause": [
        "@brief Run once when the task is paused.",
        "",
        "Most tasks need nothing here. Override when something must not persist",
        "across a pause - stop a motor, release a bus, freeze an integrator - so",
        "the paused state is safe. Pair with on_resume(). Leave empty otherwise.",
    ],
    "on_resume": [
        "@brief Run once when a paused task resumes.",
        "",
        "The mirror of on_pause(): re-acquire or restart whatever it released.",
        "Leave empty if on_pause() was empty.",
    ],
    "is_finished": [
        "@brief Whether the task is done; polled after each on_execute().",
        "",
        "Return true once there is no work left; the manager then calls",
        "on_complete() and removes the task. Returning true unconditionally makes",
        "this a single-shot task that concludes after one on_execute().",
        "",
        "@return true when finished, false to keep running.",
    ],
}


class TaskFile:
    """Renders the ``.hpp`` / ``.cpp`` text for a single task node.

    The constructor's parameter list is the only schema-derived *code* line the
    updater later rewrites in place; it is tagged with :data:`Naming.anchor` in
    both files. Everything else - the class documentation and the per-hook
    doc-comment templates - is generated once alongside the scaffold and then
    owned by the user.
    """

    # ------------------------------------------------------------ signatures

    @staticmethod
    def hpp_params(task: Node) -> str:
        parts = [f"{p.cpp_type} {p.name}" for p in task.params or []]
        if task.injected_scope is not None:
            parts.append(f"{Naming.context_type}& {Naming.context_param}")
        return ", ".join(parts)

    @staticmethod
    def cpp_params(task: Node) -> str:
        # Declared params are meant to be used, so they stay bare; the scope
        # context is optional per task, so it is the [[maybe_unused]] last arg.
        parts = [f"{p.cpp_type} {p.name}" for p in task.params or []]
        if task.injected_scope is not None:
            parts.append(f"[[maybe_unused]] {Naming.context_type}& {Naming.context_param}")
        return ", ".join(parts)

    # ------------------------------------------------------------- rendering

    @staticmethod
    def render_hpp(task: Node) -> str:
        cls = Naming.class_name(task)
        guard = Naming.include_guard(task, "hpp")
        ns = Naming.namespace(task)

        lines: List[str] = []
        lines.append("// SPDX-License-Identifier: MIT")
        lines.extend(TaskFile.__file_doc(task, f"{cls}.hpp"))
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append(f'#include "{Naming.base_include(task)}"')
        if task.injected_scope is not None:
            lines.append(f'#include "{Naming.context_include()}"')
        if task.returns:
            lines.append("#include <etools/memory/buffer.hpp>")
        lines.append("")
        lines.append(f"namespace {ns} {{")
        lines.extend(TaskFile.__class_doc(task, "    "))
        lines.append(f"    class {cls} : public task {{")
        lines.append("    public:")

        lines.extend(TaskFile.__doc(TaskFile.__ctor_doc(task), "        "))
        lines.append(f"        {cls}({TaskFile.hpp_params(task)}); {Naming.anchor}")
        lines.append("")

        for hook in _VOID_HOOKS:
            lines.extend(TaskFile.__doc(_HOOK_DOCS[hook], "        "))
            lines.append(f"        void {hook}() override;")
            lines.append("")

        lines.extend(TaskFile.__doc(_HOOK_DOCS["is_finished"], "        "))
        lines.append("        bool is_finished() override;")

        if task.returns:
            lines.append("")
            lines.extend(TaskFile.__doc(TaskFile.__on_complete_doc(task), "        "))
            lines.append(
                "        etools::memory::buffer<> "
                "on_complete(etask::core::completion_reason reason) override;"
            )

        lines.append("")
        lines.append(
            f"        static constexpr global::task_id uid = "
            f"global::task_id::{Naming.uid_symbol(task)};"
        )
        lines.append("    };")
        lines.append(f"}} // namespace {ns}")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def render_cpp(task: Node) -> str:
        cls = Naming.class_name(task)
        ns = Naming.namespace(task)
        lines: List[str] = []
        lines.append("// SPDX-License-Identifier: MIT")
        lines.extend(TaskFile.__file_doc(task, f"{cls}.cpp"))
        # No include guard: a .cpp is a translation unit, compiled once, not included.
        lines.append(f'#include "{cls}.hpp"')
        lines.append("")
        lines.append(f"namespace {ns} {{")
        lines.append(f"    {cls}::{cls}({TaskFile.cpp_params(task)}) {Naming.anchor}")
        lines.append("    {")
        lines.append("        // TODO: initialize the task from its parameters.")
        lines.append("    }")
        for hook in _VOID_HOOKS:
            lines.append(f"    void {cls}::{hook}()")
            lines.append("    {")
            lines.append("    }")
        lines.append(f"    bool {cls}::is_finished()")
        lines.append("    {")
        lines.append("        return true;")
        lines.append("    }")
        if task.returns:
            lines.append(
                f"    etools::memory::buffer<> "
                f"{cls}::on_complete([[maybe_unused]] etask::core::completion_reason reason)"
            )
            lines.append("    {")
            lines.append("        // TODO: pack and return the task result (branch on `reason`).")
            lines.append("        return {};")
            lines.append("    }")
        lines.append(f"}} // namespace {ns}")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------ doc helpers

    @staticmethod
    def __doc(body: List[str], indent: str) -> List[str]:
        """Wrap raw body lines into a `/** ... */` block at ``indent``."""
        out = [f"{indent}/**"]
        for ln in body:
            out.append(f"{indent}* {ln}" if ln else f"{indent}*")
        out.append(f"{indent}*/")
        return out

    @staticmethod
    def __file_doc(task: Node, file_name: str) -> List[str]:
        brief = task.doc_brief or f"`{Naming.class_name(task)}` task."
        return [
            "/**",
            f"* @file {file_name}",
            "*",
            f"* @brief {brief}",
            "*",
            "* @note Generated by etask. The constructor signature is owned by the",
            "*       generator (tagged with the etask:sig anchor); the bodies are yours.",
            "*/",
        ]

    @staticmethod
    def __class_doc(task: Node, indent: str) -> List[str]:
        brief = task.doc_brief or f"`{Naming.class_name(task)}` task."
        body: List[str] = [f"@brief {brief}"]
        detail = task.doc_detail
        if detail:
            body.append("")
            body.extend(detail.splitlines())
        body.append("")
        body.append("Lifecycle: on_start() runs once, then on_execute() each tick until")
        body.append("is_finished() returns true (or an external completion), then")
        body.append("on_complete(). on_pause()/on_resume() bracket a pause. See")
        body.append("etask::core::task for the full contract.")
        return TaskFile.__doc(body, indent)

    @staticmethod
    def __ctor_doc(task: Node) -> List[str]:
        body: List[str] = ["@brief Construct the task from its parameters."]
        params = task.params or []
        if params or task.injected_scope is not None:
            body.append("")
        for p in params:
            body.append(f"@param {p.name} TODO: describe `{p.name}`.")
        if task.injected_scope is not None:
            body.append(
                f"@param {Naming.context_param} The `{Naming.context_type}` shared by "
                f"this task's scope (hardware handles / state)."
            )
        return body

    @staticmethod
    def __on_complete_doc(task: Node) -> List[str]:
        body: List[str] = [
            "@brief Conclude the task and produce its result. Runs exactly once.",
            "",
            "Invoked by the manager as the task ends, on every path:",
            " - natural completion (reason == completion_reason::finished), after",
            "   is_finished() returned true;",
            " - a forced completion requested through a channel (reason ==",
            "   completion_reason::aborted, or a caller-supplied reason).",
            "Branch on `reason` to decide what to return.",
            "",
            "@param reason Why the task is concluding. A system-only, input-only",
            "              signal - see etask::core::completion_reason.",
            "@return A buffer packing this task's declared return values, in order:",
        ]
        for i, r in enumerate(task.returns or []):
            label = r.name if r.name else f"[{i}]"
            body.append(f"          - {label} : {r.cpp_type}")
        body.append(
            "        On a forced completion you may return an empty buffer if no"
        )
        body.append("        meaningful result applies.")
        return body
