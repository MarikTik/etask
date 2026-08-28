from typing import List

from etask.schema.models.node import Node

_ROOT_NAMESPACE = "sys"
_SIG_ANCHOR = "//! etask:sig"
_CONTEXT_TYPE = "context"
_CONTEXT_PARAM = "ctx"
_CONTEXT_FILE = "context.hpp"


class Naming:
    """Maps tree nodes to C++/filesystem names for the task-file generator.

    A task at schema path ``a.b.c`` lives at ``<a>/<b>/c.hpp`` (+ ``.cpp``), in
    namespace ``tasks::a::b``, class ``c``, referencing ``global::task_id::a_b_c``.
    Each scope that owns tasks also gets a ``context`` class (``a/b/context.hpp``)
    injected as the last constructor argument of its tasks.
    """

    anchor = _SIG_ANCHOR
    context_type = _CONTEXT_TYPE
    context_param = _CONTEXT_PARAM

    @staticmethod
    def context_include() -> str:
        return _CONTEXT_FILE

    @staticmethod
    def scope_namespace(scope: Node) -> str:
        return "::".join([_ROOT_NAMESPACE, *Naming.path_parts(scope)])

    @staticmethod
    def context_guard(scope: Node) -> str:
        joined = "_".join([_ROOT_NAMESPACE, *Naming.path_parts(scope), _CONTEXT_TYPE, "hpp"])
        return joined.upper() + "_"

    @staticmethod
    def path_parts(node: Node) -> List[str]:
        parts: List[str] = []
        current = node
        while current is not None and current.parent is not None:
            parts.append(current.name)
            current = current.parent
        parts.reverse()
        return parts

    @staticmethod
    def scope_parts(task: Node) -> List[str]:
        return Naming.path_parts(task)[:-1]

    @staticmethod
    def class_name(task: Node) -> str:
        return task.name

    @staticmethod
    def namespace(task: Node) -> str:
        parts = [_ROOT_NAMESPACE, *Naming.scope_parts(task)]
        return "::".join(parts)

    @staticmethod
    def uid_symbol(task: Node) -> str:
        return "_".join(Naming.path_parts(task))

    @staticmethod
    def relative_dir(task: Node) -> str:
        return "/".join(Naming.scope_parts(task))

    @staticmethod
    def scope_dir(scope: Node) -> str:
        return "/".join(Naming.path_parts(scope))

    @staticmethod
    def include_guard(task: Node, ext: str) -> str:
        joined = "_".join([_ROOT_NAMESPACE, *Naming.path_parts(task), ext])
        return joined.upper() + "_"

    @staticmethod
    def base_include(task: Node) -> str:
        depth = len(Naming.scope_parts(task))
        return "../" * depth + "task.hpp"

    # ---- the task-base alias file (task.hpp), emitted once at the tree root ----

    @staticmethod
    def root_namespace() -> str:
        return _ROOT_NAMESPACE

    @staticmethod
    def task_base_include() -> str:
        return "task.hpp"

    @staticmethod
    def task_base_guard() -> str:
        return f"{_ROOT_NAMESPACE.upper()}_TASK_HPP_"

    @staticmethod
    def task_id_include_from_root() -> str:
        """Path from the generated-tree root (where task.hpp sits) to task_id.hpp."""
        return "../generated/task_id.hpp"

    # ---- the scope accessor file (generated/scopes.hpp) ----

    @staticmethod
    def scopes_namespace() -> str:
        """Namespace holding the scope accessors."""
        return "generated::scopes"

    @staticmethod
    def scopes_guard() -> str:
        return "GENERATED_SCOPES_HPP_"

    @staticmethod
    def scope_accessor(scope: Node) -> str:
        """The accessor function name for a scope's context.

        Flat and path-joined, matching :meth:`uid_symbol` - ``rotors.fl`` becomes
        ``rotors_fl``, so an accessor reads the same way the task id it serves
        does. The document root's accessor is ``system``, since its scope has no
        path parts of its own.
        """
        parts = Naming.path_parts(scope)
        return "_".join(parts) if parts else "system"

    @staticmethod
    def scope_context_type(scope: Node) -> str:
        """The fully-qualified `context` type of a scope."""
        return f"{Naming.scope_namespace(scope)}::{_CONTEXT_TYPE}"

    @staticmethod
    def scopes_include(task: Node) -> str:
        """Path from a task's directory to ``generated/scopes.hpp``.

        One ``../`` per scope level to reach the generated-tree root, then one
        more to step out of it - the same shape as
        :meth:`task_id_include_from_root`, which sits beside it.
        """
        depth = len(Naming.scope_parts(task))
        return "../" * depth + "../generated/scopes.hpp"

    @staticmethod
    def scope_member_path(scope: Node) -> str:
        """The member path from the top-level context down to this scope's.

        ``rotors.fl`` is reached as ``.rotors.fl`` from the top, because each
        scope's context holds its children as members of the same names (see
        :class:`ContextFile`). Empty for the top-level scope itself.
        """
        return "".join(f".{part}" for part in Naming.path_parts(scope))
