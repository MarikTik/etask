from typing import List

from schemav2.models.node import Node
from schemav2.codegen.naming import Naming
from schemav2.codegen.comment import escape_block
from schemav2.codegen.doc_region import DocRegion

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
        lines.extend(DocRegion.render("file", TaskFile.__file_doc(task, f"{cls}.hpp")))
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append(f'#include "{Naming.base_include(task)}"')
        if task.injected_scope is not None:
            lines.append(f'#include "{Naming.context_include()}"')
        if task.returns:
            lines.append("#include <etask/core/outcome.hpp>")
        lines.append("")
        lines.append(f"namespace {ns} {{")
        lines.extend(DocRegion.render("class", TaskFile.__class_doc(task, "    "), "    "))
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
                "        etask::core::outcome "
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
        lines.extend(DocRegion.render("file", TaskFile.__file_doc(task, f"{cls}.cpp")))
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
                f"    etask::core::outcome "
                f"{cls}::on_complete([[maybe_unused]] etask::core::completion_reason reason)"
            )
            lines.append("    {")
            lines.extend(TaskFile.__on_complete_body(task))
            lines.append("    }")
        lines.append(f"}} // namespace {ns}")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------ body helpers

    @staticmethod
    def __on_complete_body(task: Node) -> List[str]:
        """The generate-once body: a compiling stub, plus the shapes to pick from.

        The shapes are spelled out as code the user can uncomment, because the
        one thing that is easy to get wrong here is pairing a status with the
        wrong value list - and that mistake is invisible until a peer decodes
        garbage.
        """
        shapes = task.returns or []
        if len(shapes) == 1 and shapes[0].is_default:
            return [
                "        // TODO: return the task result values (branch on `reason`).",
                "        return {};",
            ]
        lines = ["        // TODO: return one of this task's declared result shapes:"]
        for shape in shapes:
            values = ", ".join(
                value.name if value.name else f"v{i}"
                for i, value in enumerate(shape.values)
            )
            if shape.is_default:
                lines.append(f"        //   {shape.key}: return {{{values}}};")
            else:
                lines.append(
                    f"        //   {shape.key}: return etask::core::outcome{{{values}}}"
                    f".with_status({shape.cpp_enumerator});"
                )
        lines.append("        return {};")
        return lines

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
        brief = escape_block(task.doc_brief or f"`{Naming.class_name(task)}` task.")
        return [
            "/**",
            f"* @file {file_name}",
            "*",
            f"* @brief {brief}",
            "*",
            "* @note Generated by etask. The constructor signature (etask:sig) tracks",
            "*       the schema and the bodies are yours. This doc block is kept in sync",
            "*       with the schema until you edit it - after that it is yours too.",
            "*/",
        ]

    @staticmethod
    def __class_doc(task: Node, indent: str) -> List[str]:
        brief = escape_block(task.doc_brief or f"`{Naming.class_name(task)}` task.")
        body: List[str] = [f"@brief {brief}"]
        detail = task.doc_detail
        if detail:
            body.append("")
            body.extend(escape_block(detail).splitlines())
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
        ]
        shapes = task.returns or []
        if len(shapes) == 1 and shapes[0].is_default:
            body.append("@return This task's result - just return the values, in order:")
            labels = TaskFile.__shape_doc(shapes[0], body, "          ")
            body.append("        e.g. `return {" + ", ".join(labels) + "};` - the values are")
            body.append("        serialized straight into the outgoing packet. Return `{}` on a")
            body.append("        forced completion if no meaningful result applies.")
            return body

        body.append("@return One of this task's declared result shapes. The status code")
        body.append("        the reply carries is what tells the peer which shape it got,")
        body.append("        so pick the status *and* the values together:")
        for shape in shapes:
            body.append("")
            # The custom form already spells its code out; don't say it twice.
            header = shape.key if shape.key.startswith("custom(") else \
                f"{shape.key} (0x{shape.code:02X})"
            body.append(f"        {header}:")
            labels = TaskFile.__shape_doc(shape, body, "          ")
            values = ", ".join(labels)
            if shape.is_default:
                body.append(f"          `return {{{values}}};`  (the default status;")
                body.append("          no with_status() needed)")
            else:
                body.append(f"          `return etask::core::outcome{{{values}}}")
                body.append(f"              .with_status({shape.cpp_enumerator});`")
        body.append("")
        body.append("        Returning values with no status keeps the manager's own code")
        body.append("        (task_finished / task_aborted). A shape not listed here is not")
        body.append("        in the schema, so no peer knows how to decode it.")
        return body

    @staticmethod
    def __shape_doc(shape, body: List[str], indent: str) -> List[str]:
        """Appends one `- name : type` line per value; returns example labels."""
        labels: List[str] = []
        for i, value in enumerate(shape.values):
            body.append(f"{indent}- {shape.label(i)} : {value.cpp_type}")
            labels.append(value.name if value.name else f"v{i}")
        return labels
