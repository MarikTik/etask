from typing import List, Optional

from etask.schema.models.node import Node
from etask.schema.models.return_shape import ReturnShape
from etask.schema.codegen.naming import Naming

#: schema type -> Python annotation. The wire encoding lives in
#: ``etask.codec``; this is only what a reader and a type checker see.
_ANNOTATIONS = {
    "int": "int",
    "int8": "int",
    "int16": "int",
    "int32": "int",
    "int64": "int",
    "uint8": "int",
    "uint16": "int",
    "uint32": "int",
    "uint64": "int",
    "float": "float",
    "double": "float",
    "bool": "bool",
}


class PythonFile:
    """Renders the generated Python client bindings for a whole schema.

    One module, because it is a projection of the schema and nothing else: no
    user code lives here, so there is nothing to preserve across runs and no
    reason to spread it over a package. It is always rewritten, exactly like
    ``task_id.hpp`` and ``task_list.hpp``.

    What it declares, per task: the uid, a typed ``async`` call, and one frozen
    dataclass per declared result shape. What it does *not* contain is any wire
    logic - packing, launching, and status-to-shape dispatch all come from
    ``etask.binding``, so a protocol fix does not require regenerating projects.
    """

    @staticmethod
    def render(root: Node, uid_bytes: int, module_name: str = "tasks") -> str:
        tasks = PythonFile.__collect_tasks(root)
        PythonFile.__reject_class_name_collisions(root, tasks)
        lines: List[str] = []
        lines.extend(PythonFile.__header(module_name, len(tasks)))
        lines.append("")
        lines.append(f"UID_BYTES = {uid_bytes}")
        lines.append('"""Width of a task uid on the wire, pinned by the project\'s uid ledger."""')
        lines.append("")
        lines.append("")
        lines.extend(PythonFile.__task_id_enum(tasks))
        lines.append("")
        for task in tasks:
            lines.extend(PythonFile.__result_shapes(task))
            lines.extend(PythonFile.__binding(task))
        lines.extend(PythonFile.__tree(root, tasks))
        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------ parts

    @staticmethod
    def __header(module_name: str, task_count: int) -> List[str]:
        return [
            '"""Generated etask client bindings - do not edit.',
            "",
            f"Regenerated from the project's schema on every `etask generate --python`",
            f"run; {task_count} task(s).",
            "",
            "Each task is an awaitable call whose result is one of its declared",
            "shapes, chosen by the status code the reply carries::",
            "",
            "    async with Client(channel, uid_bytes=UID_BYTES) as client:",
            "        tasks = Tasks(client)",
            "        result = await tasks.<scope>.<task>(<params>)",
            "",
            "Launching does not block: start several tasks and await them together",
            "with `asyncio.gather`. See `etask.client` for how replies are matched.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "from dataclasses import dataclass",
            "from enum import IntEnum",
            "",
            "from etask.binding import (",
            "    InstantTaskBinding,",
            "    Scope,",
            "    TaskBinding,",
            "    UndeclaredResult,",
            "    build_shapes,",
            ")",
            "from etask.client import Client",
        ]

    @staticmethod
    def __task_id_enum(tasks: List[Node]) -> List[str]:
        lines = [
            "class TaskId(IntEnum):",
            '    """Every task\'s wire uid - the same values as `global::task_id` in C++."""',
            "",
        ]
        if not tasks:
            lines.append("    pass")
        for task in tasks:
            lines.append(f"    {PythonFile.__enum_name(task)} = {task.uid}")
        lines.append("")
        return lines

    @staticmethod
    def __result_shapes(task: Node) -> List[str]:
        lines: List[str] = []
        for shape in task.returns or []:
            cls = PythonFile.__shape_class(task, shape)
            lines.append("")
            lines.append("")
            lines.append("@dataclass(frozen=True)")
            lines.append(f"class {cls}:")
            lines.append(
                f'    """`{".".join(Naming.path_parts(task))}` result carried by '
                f'`{shape.key}` (0x{shape.code:02X})."""'
            )
            lines.append("")
            if not shape.values:
                lines.append("    # This status carries no values.")
                lines.append("    pass")
                continue
            for index, value in enumerate(shape.values):
                name = PythonFile.__field_name(value.name, index)
                lines.append(f"    {name}: {_ANNOTATIONS[value.type]}")
        return lines

    @staticmethod
    def __binding(task: Node) -> List[str]:
        if task.tier is not None and task.tier.is_instant:
            return PythonFile.__instant_binding(task)
        cls = PythonFile.__task_class(task)
        path = ".".join(Naming.path_parts(task))
        params = task.params or []
        shapes = task.returns or []

        lines = ["", "", f"class {cls}(TaskBinding):"]
        lines.append(f'    """{PythonFile.__brief(task)}')
        lines.append("")
        lines.append(f"    Schema path `{path}`, uid {task.uid}.")
        if shapes:
            lines.append("")
            lines.append("    Returns one of:")
            for shape in shapes:
                lines.append(
                    f"      - `{PythonFile.__shape_class(task, shape)}` "
                    f"on `{shape.key}` (0x{shape.code:02X})"
                )
            lines.append("    ...or `UndeclaredResult` for any other completion status.")
        lines.append('    """')
        lines.append("")
        lines.append(f"    UID = TaskId.{PythonFile.__enum_name(task)}")
        lines.append(f'    PATH = "{path}"')
        lines.append(f"    PARAMS = ({PythonFile.__type_tuple([p.type for p in params])})")
        if shapes:
            lines.append("    SHAPES = build_shapes([")
            for shape in shapes:
                types = PythonFile.__type_tuple([v.type for v in shape.values])
                lines.append(
                    f"        (0x{shape.code:02X}, {PythonFile.__shape_class(task, shape)}, "
                    f"({types})),"
                )
            lines.append("    ])")
        else:
            lines.append("    SHAPES = {}")
        lines.append("")

        # Result-shape aliases, so a caller can `match` without importing names:
        # `tasks.sensors.gps.fix.Finished(...)`.
        for shape in shapes:
            alias = PythonFile.__shape_alias(shape)
            lines.append(f"    {alias} = {PythonFile.__shape_class(task, shape)}")
        if shapes:
            lines.append("")

        signature = ", ".join(
            f"{p.name}: {_ANNOTATIONS[p.type]}" for p in params
        )
        signature = f"self, *, {signature}" if signature else "self"
        returns = PythonFile.__return_annotation(task)
        lines.append(f"    async def __call__({signature}){returns}:")
        lines.append(f'        """Starts `{path}` and waits for its reply.')
        lines.append("")
        if params:
            lines.append("        Args:")
            for p in params:
                lines.append(f"            {p.name}: `{p.type}`.")
            lines.append("")
        lines.append("        Raises:")
        lines.append("            TaskRejected: the device refused to start the task.")
        lines.append('        """')
        argument_list = ", ".join(p.name for p in params)
        lines.append(f"        return await self._invoke([{argument_list}])")
        return lines

    @staticmethod
    def __instant_binding(task: Node) -> List[str]:
        """A fire-and-forget command: a plain call, with nothing to await.

        The device runs it inside the call that delivers it and sends no reply,
        so this is deliberately not a coroutine - awaiting one would wait for a
        message that is never coming.
        """
        cls = PythonFile.__task_class(task)
        path = ".".join(Naming.path_parts(task))
        params = task.params or []

        lines = ["", "", f"class {cls}(InstantTaskBinding):"]
        lines.append(f'    """{PythonFile.__brief(task)}')
        lines.append("")
        lines.append(f"    Schema path `{path}`, uid {task.uid}.")
        lines.append("")
        lines.append("    A fire-and-forget command: it runs on the device the moment the")
        lines.append("    request arrives and sends nothing back, so calling it returns")
        lines.append("    immediately and there is no result to await. It cannot be paused,")
        lines.append("    resumed, or completed - there is never a live instance to address.")
        lines.append('    """')
        lines.append("")
        lines.append(f"    UID = TaskId.{PythonFile.__enum_name(task)}")
        lines.append(f'    PATH = "{path}"')
        lines.append(f"    PARAMS = ({PythonFile.__type_tuple([p.type for p in params])})")
        lines.append("")

        signature = ", ".join(f"{p.name}: {_ANNOTATIONS[p.type]}" for p in params)
        signature = f"self, *, {signature}" if signature else "self"
        lines.append(f"    def __call__({signature}) -> None:")
        lines.append(f'        """Runs `{path}` on the device. Returns as soon as the request is sent.')
        lines.append("")
        if params:
            lines.append("        Args:")
            for p in params:
                lines.append(f"            {p.name}: `{p.type}`.")
            lines.append("")
        lines.append("        Nothing is returned and no exception is raised if the device")
        lines.append("        rejects the command: an instant task sends no reply. Use a")
        lines.append("        oneshot_task when the outcome matters.")
        lines.append('        """')
        argument_list = ", ".join(p.name for p in params)
        lines.append(f"        self._dispatch([{argument_list}])")
        return lines

    @staticmethod
    def __tree(root: Node, tasks: List[Node]) -> List[str]:
        """The scope tree: one class per scope, then the root ``Tasks``.

        Scopes are emitted deepest-first so a parent can name its children's
        classes directly, without forward references.
        """
        lines: List[str] = []
        for scope in reversed(PythonFile.__collect_scopes(root)):
            lines.append("")
            lines.append("")
            lines.append(f"class {PythonFile.__scope_class(scope)}(Scope):")
            path = ".".join(Naming.path_parts(scope))
            brief = scope.doc_brief or f"the `{scope.name}` scope"
            lines.append(f'    """{brief.splitlines()[0]}')
            lines.append("")
            lines.append(f"    Schema scope `{path}`.")
            lines.append('    """')
            lines.append("")
            lines.extend(PythonFile.__scope_body(scope, "    "))

        lines.append("")
        lines.append("")
        lines.append("class Tasks(Scope):")
        lines.append('    """The project\'s task tree, mirroring the schema\'s scopes.')
        lines.append("")
        lines.append("    Construct it with a live `Client`; every task below is an")
        lines.append("    awaitable call at the same path the schema declares.")
        lines.append('    """')
        lines.append("")
        lines.append("    UID_BYTES = UID_BYTES")
        lines.append("")
        lines.extend(PythonFile.__scope_body(root, "    "))
        return lines

    @staticmethod
    def __scope_body(scope: Node, indent: str) -> List[str]:
        children = list(scope.children.values())
        if not children:
            return [f"{indent}pass"]
        lines = [f"{indent}def __init__(self, client: Client) -> None:",
                 f"{indent}    super().__init__(client)"]
        for child in children:
            if child.is_task:
                lines.append(
                    f"{indent}    self.{child.name} = {PythonFile.__task_class(child)}(client)"
                )
            else:
                lines.append(
                    f"{indent}    self.{child.name} = "
                    f"{PythonFile.__scope_class(child)}(client)"
                )
        return lines

    # ---------------------------------------------------------------- naming

    @staticmethod
    def __reject_class_name_collisions(root: Node, tasks: List[Node]) -> None:
        """Two schema paths must not fold into one Python class name.

        Path parts are joined and snake_case is flattened, so ``a_b.c`` and
        ``a.b_c`` would both become ``ABC``. Nothing in the schema forbids that
        pair, and the resulting module would silently define one class twice -
        so it is caught here rather than emitted.
        """
        seen = {}
        nodes = tasks + PythonFile.__collect_scopes(root)
        for node in nodes:
            path = ".".join(Naming.path_parts(node))
            key = PythonFile.__pascal(Naming.path_parts(node))
            if key in seen:
                raise ValueError(
                    f"'{path}' and '{seen[key]}' both become the Python class name "
                    f"'{key}'; rename one of them"
                )
            seen[key] = path

    @staticmethod
    def __collect_tasks(node: Node) -> List[Node]:
        tasks = [node] if node.is_task else []
        for child in node.children.values():
            tasks.extend(PythonFile.__collect_tasks(child))
        return tasks

    @staticmethod
    def __collect_scopes(node: Node) -> List[Node]:
        scopes: List[Node] = []
        for child in node.children.values():
            if not child.is_task:
                scopes.append(child)
                scopes.extend(PythonFile.__collect_scopes(child))
        return scopes

    @staticmethod
    def __pascal(parts: List[str]) -> str:
        """``["nav", "fly_to"] -> "NavFlyTo"`` - snake_case words capitalize too."""
        words = [word for part in parts for word in part.split("_") if word]
        return "".join(word[:1].upper() + word[1:] for word in words)

    @staticmethod
    def __task_class(task: Node) -> str:
        return "_" + PythonFile.__pascal(Naming.path_parts(task))

    @staticmethod
    def __scope_class(scope: Node) -> str:
        return "_" + PythonFile.__pascal(Naming.path_parts(scope)) + "Scope"

    @staticmethod
    def __enum_name(task: Node) -> str:
        return "_".join(Naming.path_parts(task)).upper()

    @staticmethod
    def __shape_class(task: Node, shape: ReturnShape) -> str:
        return PythonFile.__pascal(Naming.path_parts(task)) + PythonFile.__shape_alias(shape)

    @staticmethod
    def __shape_alias(shape: ReturnShape) -> str:
        if shape.name.startswith("custom("):
            return f"Custom{shape.code:02X}"
        stripped = shape.name[len("task_"):] if shape.name.startswith("task_") else shape.name
        return PythonFile.__pascal(stripped.split("_"))

    @staticmethod
    def __field_name(name: Optional[str], index: int) -> str:
        return name if name else f"v{index}"

    @staticmethod
    def __type_tuple(types: List[str]) -> str:
        if not types:
            return ""
        inner = ", ".join(f'"{t}"' for t in types)
        return inner + ("," if len(types) == 1 else "")

    @staticmethod
    def __return_annotation(task: Node) -> str:
        shapes = task.returns or []
        if not shapes:
            return " -> UndeclaredResult"
        names = [PythonFile.__shape_class(task, shape) for shape in shapes]
        names.append("UndeclaredResult")
        return " -> " + " | ".join(names)

    @staticmethod
    def __brief(task: Node) -> str:
        brief = task.doc_brief or f"`{task.name}` task."
        return brief.splitlines()[0].replace('"""', "'''")
