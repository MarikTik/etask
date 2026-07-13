from typing import List

from schemav2.models.node import Node

_ROOT_NAMESPACE = "tasks"
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
