from typing import List

from schemav2.models.node import Node
from schemav2.codegen.naming import Naming


class ContextFile:
    """Renders the user-fillable ``context`` class for a scope.

    The context is the local state/hardware a scope's tasks act on. It is
    generated once and then owned by the user; the generator never rewrites it.
    Any ``brief``/``description`` on the scope flows into the class docs, so the
    subsystem the context belongs to is described where its state lives.
    """

    @staticmethod
    def render(scope: Node) -> str:
        guard = Naming.context_guard(scope)
        ns = Naming.scope_namespace(scope)

        lines: List[str] = []
        lines.append("// SPDX-License-Identifier: MIT")
        lines.append("/**")
        lines.append(f"* @file {Naming.context_include()}")
        lines.append("*")
        lines.append(f"* @brief Local context for the `{scope.name}` scope (hardware handles, state).")
        lines.append("*")
        lines.append("* @note Generated once by etask, then owned by you. Add whatever hardware")
        lines.append("*       handles and state the tasks in this scope need to operate on.")
        lines.append("*/")
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append("")
        lines.append(f"namespace {ns} {{")
        lines.extend(ContextFile.__class_doc(scope, "    "))
        lines.append("    class context {")
        lines.append("    public:")
        lines.append("        // TODO: add hardware handles / state for this scope.")
        lines.append("    };")
        lines.append(f"}} // namespace {ns}")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def __class_doc(scope: Node, indent: str) -> List[str]:
        brief = scope.doc_brief
        summary = (
            f"Shared state and hardware for the `{scope.name}` scope - {brief}"
            if brief else
            f"Shared state and hardware for the `{scope.name}` scope."
        )
        body: List[str] = [f"@brief {summary}"]
        detail = scope.doc_detail
        if detail:
            body.append("")
            body.extend(detail.splitlines())
        body.append("")
        body.append(f"Injected by reference into every task in `{Naming.scope_namespace(scope)}`;")
        body.append("a task reads and mutates it to coordinate with its siblings in the scope.")

        out = [f"{indent}/**"]
        for ln in body:
            out.append(f"{indent}* {ln}" if ln else f"{indent}*")
        out.append(f"{indent}*/")
        return out
