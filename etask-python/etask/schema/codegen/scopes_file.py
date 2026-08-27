import os
from pathlib import Path
from typing import List, Optional

from etask.schema.models.node import Node
from etask.schema.codegen.naming import Naming


class ScopesFile:
    """Renders ``scopes.hpp`` - one accessor per scope, over one hidden context tree.

    A task in a scope is constructed with that scope's ``context&``. When the
    task arrives over the wire there is nothing to hand in at the call site, so
    the adapter binds the scope through a nullary accessor instead (see
    ``etask::core::scoped_task_unpack_adapter``). This file is where those
    accessors come from.

    ## The tree is owned here, and is not the user's to hold

    Every scope's context is a member of its parent's, so the whole tree is one
    object (see :class:`ContextFile`). That object lives in a function-local
    static inside ``detail`` and is never named anywhere a user would reach it.

    That is deliberate, and it is the point of the file. A visible root is a
    thing a user can get wrong: construct a second one, keep a reference to a
    context that belongs to a different tree, or pass the wrong scope to
    something that takes a ``context&``. None of those are possible if there is
    nothing to name. What a user *does* interact with is their own scope's
    context, delivered to their task's constructor by the framework - which is
    the only place a context reference is ever needed.

    The top-level context is a scope like any other, so it gets an accessor too;
    it is simply the one whose member path is empty.

    ## Why a function-local static

    Not a namespace-scope variable: that constructs at static-init time, before
    ``main`` and before any board setup has run. A context holds hardware
    handles, so constructing one early is precisely the hazard the framework
    otherwise avoids by building tasks only at registration. A function-local
    static constructs on first use - the first task registration - which is
    after ``setup()`` by construction.
    """

    @staticmethod
    def render(root: Node, out_dir: Path, scopes_path: Path) -> str:
        scopes = ScopesFile.__collect_scopes(root)
        lines: List[str] = []
        lines.extend(ScopesFile.__header())
        guard = Naming.scopes_guard()
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        for include in ScopesFile.__includes(scopes, out_dir, scopes_path):
            lines.append(f'#include "{include}"')
        lines.append("")
        lines.extend(ScopesFile.__tree_owner(root))
        lines.append("")
        lines.append(f"namespace {Naming.scopes_namespace()} {{")
        for scope in scopes:
            lines.append("")
            lines.extend(ScopesFile.__accessor(scope))
        lines.append("")
        lines.append(f"}} // namespace {Naming.scopes_namespace()}")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------ parts

    @staticmethod
    def __header() -> List[str]:
        return [
            "/**",
            "* @file scopes.hpp",
            "*",
            "* @brief One accessor per scope, over the project's context tree.",
            "*",
            "* A task that belongs to a scope is constructed with that scope's `context&`.",
            "* A task arriving over the wire has no call site to hand one in, so the",
            "* unpacking adapter binds the scope through the accessor named here.",
            "*",
            "* The context tree itself is owned by this file and deliberately cannot be",
            "* named from outside it: a root you can reach is a root you can duplicate,",
            "* alias, or pass the wrong branch of. Your scope's context reaches you the",
            "* one way it should - as your task's constructor argument.",
            "*",
            "* What lives *inside* each context is entirely yours; see the `context.hpp`",
            "* in each scope directory.",
            "*",
            "* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema",
            "*          on every generate; hand edits are overwritten. Regenerate via the",
            "*          CMake `etask-generate` target, or `etask generate`.",
            "*/",
        ]

    @staticmethod
    def __includes(scopes: List[Node], out_dir: Path, scopes_path: Path) -> List[str]:
        """One include per scope context, relative to this file's directory."""
        here = scopes_path.parent
        includes: List[str] = []
        for scope in scopes:
            hpp = out_dir / Naming.scope_dir(scope) / Naming.context_include()
            includes.append(os.path.relpath(hpp, here).replace(os.sep, "/"))
        return includes

    @staticmethod
    def __tree_owner(root: Node) -> List[str]:
        """The hidden owner of the whole context tree."""
        top = Naming.scope_context_type(root)
        return [
            "namespace generated::detail {",
            "",
            "    /**",
            "    * @brief The project's one context tree.",
            "    *",
            "    * Every scope's context is a member of its parent's, so this single",
            f"    * `{top}` transitively owns all of them.",
            "    *",
            "    * A function-local static, so it is constructed on **first use** - the",
            "    * first task registration - rather than before `main`. Contexts hold",
            "    * hardware handles, and constructing those at static-init time is the one",
            "    * ordering hazard this framework otherwise has no way to hit.",
            "    *",
            "    * @note Internal. It is in `detail` because nothing outside should be able",
            "    *       to name it: a reachable tree is one that can be duplicated or",
            "    *       partially aliased. Tasks receive their own scope's context, which",
            "    *       is the only access anything needs.",
            "    *",
            "    * @return The tree, for the accessors in `generated::scopes` to index into.",
            "    */",
            f"    [[nodiscard]] inline {top}& tree() noexcept",
            "    {",
            f"        static {top} instance;",
            "        return instance;",
            "    }",
            "",
            "} // namespace generated::detail",
        ]

    @staticmethod
    def __accessor(scope: Node) -> List[str]:
        """One scope's accessor, and the doc saying what it is for."""
        name = Naming.scope_accessor(scope)
        type_ = Naming.scope_context_type(scope)
        path = Naming.scope_member_path(scope)
        label = ".".join(Naming.path_parts(scope)) or "the top-level scope"
        return [
            "    /**",
            f"    * @brief The `context` of `{label}`.",
            "    *",
            "    * Bound as the scope argument of every task in it (see",
            "    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset",
            "    * into the one context tree - there is no lookup and no indirection.",
            "    */",
            f"    [[nodiscard]] inline {type_}& {name}() noexcept",
            "    {",
            f"        return detail::tree(){path};",
            "    }",
        ]

    @staticmethod
    def __collect_scopes(node: Node) -> List[Node]:
        """The root and every descendant scope, parents before children.

        Parent-first so the emitted accessors read top-down, matching the order
        the contexts are declared in.
        """
        scopes = [node] if node.is_root or node.is_scope else []
        for child in node.children.values():
            if not child.is_task:
                scopes.extend(ScopesFile.__collect_scopes(child))
        return scopes
