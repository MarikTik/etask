from pathlib import Path
from typing import Dict, List, Optional, Union
import copy
import hashlib
import json
import keyword
import re

import yaml

from schemav2.models.node import Node, Kind
from schemav2.models.param import Param
from schemav2.models.type_map import TypeMap
from schemav2.errors.duplicate_uid_error import DuplicateUidError
from schemav2.errors.invalid_identifier_error import InvalidIdentifierError
from schemav2.errors.unknown_type_error import UnknownTypeError
from schemav2.errors.schema_shape_error import SchemaShapeError
from schemav2.errors.abstract_instance_error import AbstractInstanceError

_KINDS = {"scope": Kind.SCOPE, "abstract_scope": Kind.ABSTRACT_SCOPE, "task": Kind.TASK}
_BOOL_RE = re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$")


class _SchemaLoader(yaml.SafeLoader):
    """SafeLoader with YAML-1.2 boolean semantics.

    PyYAML defaults to YAML 1.1, where ``on``/``off``/``yes``/``no`` resolve to
    booleans — fatal for a robotics schema full of ``on``/``off`` tasks. Here
    only ``true``/``false`` are booleans; everything else stays a string.
    """


_SchemaLoader.yaml_implicit_resolvers = {
    char: [(tag, regexp) for tag, regexp in mappers if tag != "tag:yaml.org,2002:bool"]
    for char, mappers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
_SchemaLoader.add_implicit_resolver("tag:yaml.org,2002:bool", _BOOL_RE, list("tTfF"))
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_UID_WIDTHS_BYTES = (1, 2, 4, 8)

# C++ keywords a node name must not collide with (names become namespaces/classes).
_CPP_KEYWORDS = frozenset({
    "alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor", "bool",
    "break", "case", "catch", "char", "char8_t", "char16_t", "char32_t", "class", "compl",
    "concept", "const", "consteval", "constexpr", "constinit", "const_cast", "continue",
    "co_await", "co_return", "co_yield", "decltype", "default", "delete", "do", "double",
    "dynamic_cast", "else", "enum", "explicit", "export", "extern", "false", "float",
    "for", "friend", "goto", "if", "inline", "int", "long", "mutable", "namespace", "new",
    "noexcept", "not", "not_eq", "nullptr", "operator", "or", "or_eq", "private",
    "protected", "public", "register", "reinterpret_cast", "requires", "return", "short",
    "signed", "sizeof", "static", "static_assert", "static_cast", "struct", "switch",
    "template", "this", "thread_local", "throw", "true", "try", "typedef", "typeid",
    "typename", "union", "unsigned", "using", "virtual", "void", "volatile", "wchar_t",
    "while", "xor", "xor_eq",
})


class Tree:
    """Builds the etask task tree from a v2 schema (YAML or JSON).

    The build runs in three passes: parse+validate the explicit-keyed tree,
    expand abstract scopes into concrete instances, then size and assign uids.
    """

    @staticmethod
    def build(schema_path: Union[str, Path]) -> Node:
        schema = Tree.__load(Path(schema_path))
        root = Node(name="", kind=Kind.ROOT)

        used_uids: Dict[int, str] = {}
        Tree.__parse_children(root, schema, used_uids, in_abstract=False)
        Tree.__expand_children(root)
        Tree.__assign_uids(root, used_uids)
        return root

    # ------------------------------------------------------------------ loading

    @staticmethod
    def __load(schema_path: Path) -> Dict:
        text = schema_path.read_text()
        if schema_path.suffix == ".json":
            data = json.loads(text)
        else:
            # YAML is a JSON superset, so this also parses .yaml/.yml and bare files.
            data = yaml.load(text, Loader=_SchemaLoader)
        if not isinstance(data, dict):
            raise SchemaShapeError("<root>", "top level must be a mapping of named nodes")
        return data

    # -------------------------------------------------------------- pass 1: parse

    @staticmethod
    def __parse_children(
        parent: Node, schema: Dict, used_uids: Dict[int, str], in_abstract: bool
    ) -> None:
        for name, body in schema.items():
            path = Tree.__child_path(parent, name)
            Tree.__validate_identifier(name, path)

            if not isinstance(body, dict):
                raise SchemaShapeError(path, "node body must be a mapping")

            kind = Tree.__parse_kind(body.get("type"), path)
            child = Node(name=name, kind=kind, parent=parent, description=body.get("description"))
            parent.children[name] = child

            if kind is Kind.TASK:
                Tree.__parse_task(child, body, path, used_uids, in_abstract)
            elif kind is Kind.ABSTRACT_SCOPE:
                Tree.__parse_abstract_scope(child, body, path, used_uids)
            else:
                Tree.__parse_scope(child, body, path, used_uids, in_abstract)

    @staticmethod
    def __parse_kind(raw: Optional[str], path: str) -> Kind:
        if raw is None:
            raise SchemaShapeError(path, "missing required 'type' key")
        if raw not in _KINDS:
            raise SchemaShapeError(
                path, f"unknown type '{raw}'; expected one of {', '.join(_KINDS)}"
            )
        return _KINDS[raw]

    @staticmethod
    def __parse_scope(
        node: Node, body: Dict, path: str, used_uids: Dict[int, str], in_abstract: bool
    ) -> None:
        Tree.__reject_task_keys(body, path)
        children = body.get("children", {})
        if not isinstance(children, dict):
            raise SchemaShapeError(path, "'children' must be a mapping")
        Tree.__parse_children(node, children, used_uids, in_abstract)

    @staticmethod
    def __parse_abstract_scope(
        node: Node, body: Dict, path: str, used_uids: Dict[int, str]
    ) -> None:
        Tree.__reject_task_keys(body, path)
        node.instances = Tree.__parse_instances(body.get("instances"), path)
        children = body.get("children", {})
        if not isinstance(children, dict):
            raise SchemaShapeError(path, "'children' must be a mapping")
        # Tasks inside an abstract scope always get generated uids -> in_abstract=True.
        Tree.__parse_children(node, children, used_uids, in_abstract=True)

    @staticmethod
    def __parse_task(
        node: Node, body: Dict, path: str, used_uids: Dict[int, str], in_abstract: bool
    ) -> None:
        if "children" in body:
            raise SchemaShapeError(path, "task nodes are leaves and cannot have 'children'")

        node.params = Tree.__parse_params(body.get("params", {}), path)
        node.returns = Tree.__parse_returns(body.get("returns", body.get("return", {})), path)

        uid = body.get("uid")
        if uid is None:
            return
        if in_abstract:
            raise SchemaShapeError(
                path, "tasks inside an abstract scope may not declare an explicit 'uid'"
            )
        if not isinstance(uid, int) or isinstance(uid, bool):
            raise SchemaShapeError(path, "'uid' must be an integer")
        existing = used_uids.get(uid)
        if existing is not None:
            raise DuplicateUidError(uid, existing, path)
        used_uids[uid] = path
        node.uid = uid

    # ------------------------------------------------------------ param parsing

    @staticmethod
    def __parse_params(value: Dict, path: str) -> List[Param]:
        if not isinstance(value, dict):
            raise SchemaShapeError(f"{path}.params", "'params' must be a mapping of name -> type")
        return [Tree.__make_param(name, type_, f"{path}.params.{name}") for name, type_ in value.items()]

    @staticmethod
    def __parse_returns(value: Union[Dict, List], path: str) -> List[Param]:
        if isinstance(value, list):
            return [Tree.__make_param(None, t, f"{path}.returns[{i}]") for i, t in enumerate(value)]
        if isinstance(value, dict):
            return [Tree.__make_param(name, t, f"{path}.returns.{name}") for name, t in value.items()]
        raise SchemaShapeError(f"{path}.returns", "'returns' must be a mapping or a list of types")

    @staticmethod
    def __make_param(name: Optional[str], type_: object, path: str) -> Param:
        if not isinstance(type_, str) or not TypeMap.is_valid(type_):
            raise UnknownTypeError(str(type_), path, TypeMap.allowed())
        return Param(name=name, type=type_)

    # ------------------------------------------------------------- validation

    @staticmethod
    def __validate_identifier(name: str, path: str) -> None:
        if not _IDENTIFIER_RE.match(name):
            raise InvalidIdentifierError(name, path, "must match [A-Za-z_][A-Za-z0-9_]*")
        if name in _CPP_KEYWORDS or keyword.iskeyword(name):
            raise InvalidIdentifierError(name, path, "collides with a reserved keyword")

    @staticmethod
    def __reject_task_keys(body: Dict, path: str) -> None:
        for key in ("params", "returns", "return", "uid"):
            if key in body:
                raise SchemaShapeError(path, f"scope nodes cannot declare '{key}'")

    @staticmethod
    def __parse_instances(raw: object, path: str) -> List[str]:
        if not isinstance(raw, list) or not raw:
            raise AbstractInstanceError(path, "'instances' must be a non-empty list of names")
        seen = set()
        for name in raw:
            if not isinstance(name, str):
                raise AbstractInstanceError(path, "instance names must be strings")
            Tree.__validate_identifier(name, f"{path}.instances")
            if name in seen:
                raise AbstractInstanceError(path, f"duplicate instance name '{name}'")
            seen.add(name)
        return list(raw)

    # ------------------------------------------------------ pass 2: expansion

    @staticmethod
    def __expand_children(node: Node) -> None:
        for name, child in list(node.children.items()):
            if child.is_abstract_scope:
                del node.children[name]
                Tree.__expand_abstract(node, child)
            else:
                Tree.__expand_children(child)

    @staticmethod
    def __expand_abstract(parent: Node, abstract: Node) -> None:
        for instance_name in abstract.instances or []:
            if instance_name in parent.children:
                raise AbstractInstanceError(
                    Tree.__path(abstract),
                    f"instance '{instance_name}' collides with an existing sibling node",
                )
            # The instance itself becomes a concrete scope; its children are copied
            # faithfully (nested abstract scopes stay abstract for later expansion).
            concrete = Node(
                name=instance_name,
                kind=Kind.SCOPE,
                description=abstract.description,
                parent=parent,
            )
            for child_name, child in abstract.children.items():
                concrete.children[child_name] = Tree.__copy_node(child, concrete)
            parent.children[instance_name] = concrete
            Tree.__expand_children(concrete)

    @staticmethod
    def __copy_node(src: Node, parent: Node) -> Node:
        clone = Node(
            name=src.name,
            kind=src.kind,  # preserve kind, incl. nested abstract_scope
            description=src.description,
            parent=parent,
            uid=None,  # cloned tasks always receive generated uids
            params=copy.deepcopy(src.params),
            returns=copy.deepcopy(src.returns),
            instances=list(src.instances) if src.instances is not None else None,
        )
        for child_name, child in src.children.items():
            clone.children[child_name] = Tree.__copy_node(child, clone)
        return clone

    # ------------------------------------------------------- pass 3: uid pass

    @staticmethod
    def __assign_uids(root: Node, used_uids: Dict[int, str]) -> None:
        tasks = Tree.__collect_tasks(root)
        max_explicit_uid = max(used_uids.keys(), default=0)
        uid_bytes = Tree.__uid_width(len(tasks), max_explicit_uid)

        for task in tasks:
            if task.uid is None:
                path = Tree.__path(task)
                task.uid = Tree.__generate_uid(path, used_uids, uid_bytes)
                used_uids[task.uid] = path
        root.uid_bytes = uid_bytes

    @staticmethod
    def __collect_tasks(node: Node) -> List[Node]:
        tasks = [node] if node.is_task else []
        for child in node.children.values():
            tasks.extend(Tree.__collect_tasks(child))
        return tasks

    @staticmethod
    def __uid_width(total_tasks: int, max_explicit_uid: int) -> int:
        for width in _UID_WIDTHS_BYTES:
            capacity = 1 << (width * 8)
            if total_tasks <= capacity and max_explicit_uid < capacity:
                return width
        raise ValueError(f"too many tasks ({total_tasks}) to fit any supported uid width")

    @staticmethod
    def __generate_uid(path: str, used_uids: Dict[int, str], uid_bytes: int) -> int:
        capacity = 1 << (uid_bytes * 8)
        digest = hashlib.blake2b(path.encode(), digest_size=uid_bytes).digest()
        uid = int.from_bytes(digest, "big")
        while uid in used_uids:
            uid = (uid + 1) % capacity
        return uid

    # ------------------------------------------------------------------ paths

    @staticmethod
    def __path(node: Node) -> str:
        parts: List[str] = []
        current: Optional[Node] = node
        while current is not None and current.parent is not None:
            parts.append(current.name)
            current = current.parent
        return ".".join(reversed(parts))

    @staticmethod
    def __child_path(parent: Node, name: str) -> str:
        parent_path = Tree.__path(parent)
        return f"{parent_path}.{name}" if parent_path else name


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else str(
        Path(__file__).parents[3] / "schema" / "schema.yaml"
    )
    tree = Tree.build(path)

    def _dump(node: Node, depth: int = 0) -> None:
        label = node.kind.value
        extra = f" uid={node.uid}" if node.is_task else ""
        print("  " * depth + f"{node.name or '<root>'} [{label}]{extra}")
        for child in node.children.values():
            _dump(child, depth + 1)

    print(f"uid_bytes = {tree.uid_bytes}")
    _dump(tree)
