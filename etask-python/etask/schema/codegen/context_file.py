from typing import List, Tuple

from etask.schema.models.node import Node
from etask.schema.codegen.naming import Naming
from etask.schema.codegen.comment import escape_block
from etask.schema.codegen.managed_region import ManagedRegion
from etask.schema.codegen.doc_region import DocRegion


_INCLUDES_REGION = "child_includes"
_CHILDREN_REGION = "children"
_MEMBER_INDENT = "        "


class ContextFile:
    """Renders a scope's ``context`` - its own state, plus its child scopes' contexts.

    Contexts form one composition tree. A scope's ``context`` holds the state and
    hardware the scope's tasks act on, **and** its child scopes' contexts as
    members, so the whole tree is owned by a single root - ``sys::context``,
    the document root's context - constructed once, top-down. A task receives its
    own scope's context and can reach downward into child contexts, never up or
    sideways (you only ever receive your own scope's context).

    The struct body and the pre-namespace includes each carry a *managed region*
    (see :class:`ManagedRegion`): the child-context members and their headers are
    generator-owned and reconciled to the schema, while a scope's own state is
    user-owned and never touched. Contexts are ``struct`` - access control is
    left to the user (add ``private:`` and friends if you want to tighten it);
    encapsulation already holds by the downward-only reachability above.
    """

    # ------------------------------------------------------------ managed items

    @staticmethod
    def child_scopes(scope: Node) -> List[Node]:
        """The scope's child *scopes* (not tasks), in declaration order."""
        return [c for c in scope.children.values() if c.is_scope]

    @staticmethod
    def include_entries(scope: Node) -> List[Tuple[str, str]]:
        """(identity, code) for the child-context ``#include`` region."""
        return [(c.name, f'#include "{c.name}/context.hpp"') for c in ContextFile.child_scopes(scope)]

    @staticmethod
    def member_entries(scope: Node) -> List[Tuple[str, str]]:
        """(identity, code) for the child-context member region."""
        return [(c.name, f"{c.name}::context {c.name};") for c in ContextFile.child_scopes(scope)]

    # ------------------------------------------------------------- fresh render

    @staticmethod
    def render(scope: Node) -> str:
        guard = Naming.context_guard(scope)
        ns = Naming.scope_namespace(scope)

        lines: List[str] = []
        lines.extend(DocRegion.render("file", ContextFile.__file_doc(scope)))
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.extend(ManagedRegion.render_block(
            _INCLUDES_REGION, "child subsystem context headers", ContextFile.include_entries(scope)))
        lines.append("")
        lines.append(f"namespace {ns} {{")
        lines.extend(DocRegion.render("class", ContextFile.__class_doc(scope, "    "), "    "))
        lines.append("    struct context {")
        lines.append(f"{_MEMBER_INDENT}// Add this scope's own hardware handles / state here.")
        lines.append("")
        lines.extend(ManagedRegion.render_block(
            _CHILDREN_REGION, "child subsystem contexts", ContextFile.member_entries(scope), _MEMBER_INDENT))
        lines.append("    };")
        lines.append(f"}} // namespace {ns}")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------- update

    @staticmethod
    def reconcile(text: str, scope: Node) -> str:
        """Refresh an existing context's managed regions to match the schema."""
        text = ManagedRegion.reconcile(text, _INCLUDES_REGION, ContextFile.include_entries(scope))
        text = ManagedRegion.reconcile(text, _CHILDREN_REGION, ContextFile.member_entries(scope))
        text = DocRegion.reconcile(text, "file", ContextFile.__file_doc(scope))
        text = DocRegion.reconcile(text, "class", ContextFile.__class_doc(scope, "    "))
        return text

    # ---------------------------------------------------------------- doc bits

    @staticmethod
    def __is_system_root(scope: Node) -> bool:
        return scope.is_root

    @staticmethod
    def __file_doc(scope: Node) -> List[str]:
        if ContextFile.__is_system_root(scope):
            brief = "The system's composition root - owns every subsystem's context."
        else:
            brief = f"Local context for the `{scope.name}` scope (state, hardware, child contexts)."
        return [
            "/**",
            f"* @file {Naming.context_include()}",
            "*",
            f"* @brief {brief}",
            "*",
            "* @note Generated once by etask, then owned by you - EXCEPT the",
            "*       `//! etask:managed` regions, which the generator keeps in step with",
            "*       the schema (child contexts added/removed as scopes change). Add your",
            "*       own state outside those regions; it is never overwritten.",
            "*/",
        ]

    @staticmethod
    def __class_doc(scope: Node, indent: str) -> List[str]:
        if ContextFile.__is_system_root(scope):
            body: List[str] = [
                "@brief The system composition root: every subsystem's context, owned here.",
                "",
                "Constructed once, top-down; a system-level task (e.g. reboot) receives this",
                "and can reach any subsystem through it.",
            ]
        else:
            brief = scope.doc_brief
            summary = (
                f"Shared state and hardware for the `{scope.name}` scope - {escape_block(brief)}"
                if brief else
                f"Shared state and hardware for the `{scope.name}` scope."
            )
            body = [f"@brief {summary}"]
            detail = scope.doc_detail
            if detail:
                body.append("")
                body.extend(escape_block(detail).splitlines())
            body.append("")
            body.append(f"Injected by reference into every task in `{Naming.scope_namespace(scope)}`,")
            body.append("which may also reach into the child-scope contexts it holds.")

        out = [f"{indent}/**"]
        for ln in body:
            out.append(f"{indent}* {ln}" if ln else f"{indent}*")
        out.append(f"{indent}*/")
        return out
