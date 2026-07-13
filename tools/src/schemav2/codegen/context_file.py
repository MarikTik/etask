from typing import List

from schemav2.models.node import Node
from schemav2.codegen.naming import Naming


class ContextFile:
    """Renders the user-fillable ``context`` class for a scope.

    The context is the local state/hardware a scope's tasks act on. It is
    generated once and then owned by the user; the generator never rewrites it.
    """

    @staticmethod
    def render(scope: Node) -> str:
        guard = Naming.context_guard(scope)
        ns = Naming.scope_namespace(scope)
        brief = f"Local context for the '{scope.name}' scope (hardware handles, state)."
        lines: List[str] = []
        lines.append("// SPDX-License-Identifier: MIT")
        lines.append("/**")
        lines.append(f"* @file {Naming.context_include()}")
        lines.append("*")
        lines.append(f"* @brief {brief}")
        lines.append("*")
        lines.append("* @note Generated once by etask, then owned by you. Add whatever hardware")
        lines.append("*       handles and state the tasks in this scope need to operate on.")
        lines.append("*/")
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append("")
        lines.append(f"namespace {ns} {{")
        lines.append("    class context {")
        lines.append("    public:")
        lines.append("        // TODO: add hardware handles / state for this scope.")
        lines.append("    };")
        lines.append(f"}} // namespace {ns}")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines) + "\n"
