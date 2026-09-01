from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Union
import copy
import json
import keyword
import re

import yaml

from etask.schema.models.budget import Budget
from etask.schema.models.links import Links
from etask.schema.models.node import Node, Kind
from etask.schema.models.param import Param
from etask.schema.models.return_shape import ReturnShape
from etask.schema.models.status_code import StatusCode
from etask.schema.models.tier import Tier
from etask.schema.models.type_map import TypeMap
from etask.schema.errors.invalid_identifier_error import InvalidIdentifierError
from etask.schema.errors.unknown_type_error import UnknownTypeError
from etask.schema.errors.unknown_status_error import UnknownStatusError
from etask.schema.errors.schema_shape_error import SchemaShapeError
from etask.schema.errors.abstract_instance_error import AbstractInstanceError
from etask.schema.uid_ledger import UidLedger

#: ``type:`` value -> node kind. Every tier name is a task; the kind says what
#: shape the node has in the tree, the tier says what the task *is*.
_KINDS = {
    "scope": Kind.SCOPE,
    "abstract_scope": Kind.ABSTRACT_SCOPE,
    **{tier.value: Kind.TASK for tier in Tier},
}
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

#: The schema's top-level sections. `system` is the device itself - the tree of
#: scopes and tasks - and is required; everything else configures how that tree
#: is realized and is optional. Keeping them as named siblings rather than
#: mixing settings into the node namespace is what lets later sections be added
#: without any of them being mistaken for a scope called "budget".
_SECTION_SYSTEM = "system"
_SECTION_BUDGET = "budget"
_SECTION_LINKS = "links"
_SECTIONS = (_SECTION_SYSTEM, _SECTION_BUDGET, _SECTION_LINKS)
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

    The build runs in four passes: parse+validate the explicit-keyed tree,
    expand abstract scopes into concrete instances, size and assign uids, then
    resolve each link's declared subsystems to the uids it carries. The last
    pass is last because it needs the other three: a subsystem may name a scope
    that only exists after expansion, and it resolves *to* uids.
    """

    @staticmethod
    def build(schema_path: Union[str, Path], ledger: Optional[UidLedger] = None) -> Node:
        """Builds the tree, assigning every task a uid.

        @param schema_path The schema to read.
        @param ledger Previous uid assignments to honor, if any. Without one,
               derived uids are recomputed from scratch every run - fine for a
               one-off inspection, wrong for a live wire protocol (see
               :mod:`etask.schema.uid_ledger`). The ledger is updated in place; the
               caller decides whether to save it.
        """
        schema = Tree.__load(Path(schema_path))
        system, budget, links = Tree.__parse_sections(schema)

        root = Node(name="", kind=Kind.ROOT, budget=budget, links=links)

        Tree.__parse_children(root, system)
        Tree.__expand_children(root)
        Tree.__assign_uids(root, ledger)
        Tree.__resolve_link_subsystems(root)
        return root

    @staticmethod
    def __parse_sections(schema: Dict) -> "tuple[Dict, Budget, Links]":
        """Splits the top level into the node tree and the settings beside it.

        ``system:`` holds the device - the scopes and tasks - and is required.
        ``budget:`` is optional; without it every tier falls back to the sum of
        its tasks' concurrency, which is the worst case and the only figure the
        schema alone can justify. ``links:`` is optional too, and empty without
        it: a system that declares no link speaks only over the internal
        channel, which is what most systems do.

        @param schema The raw top-level mapping.
        @return The ``system`` mapping, the parsed budget, and the parsed links.
        @throws SchemaShapeError If ``system`` is missing or malformed, or an
                unrecognized section appears beside it.
        """
        if _SECTION_SYSTEM not in schema:
            raise SchemaShapeError(
                "<root>",
                "missing required 'system' section. The device's scopes and tasks "
                "live under a top-level 'system:' key, so that settings beside it "
                "(such as 'budget:') are unambiguous:\n"
                "        system:\n"
                "          led:\n"
                "            type: polled_task",
            )

        unknown = [key for key in schema if key not in _SECTIONS]
        if unknown:
            raise SchemaShapeError(
                "<root>",
                f"unknown top-level {'section' if len(unknown) == 1 else 'sections'} "
                f"{', '.join(repr(u) for u in sorted(unknown))}; "
                f"expected one of {', '.join(_SECTIONS)}. "
                "Scopes and tasks belong under 'system:', not at the top level.",
            )

        system = schema[_SECTION_SYSTEM]
        if not isinstance(system, dict):
            raise SchemaShapeError("system", "'system' must be a mapping of named nodes")

        budget = (
            Budget.parse(schema[_SECTION_BUDGET]) if _SECTION_BUDGET in schema else Budget()
        )
        links = (
            Links.parse(schema[_SECTION_LINKS], Tree.__validate_identifier)
            if _SECTION_LINKS in schema
            else Links()
        )
        return system, budget, links

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
        parent: Node, schema: Dict
    ) -> None:
        for name, body in schema.items():
            path = Tree.__child_path(parent, name)
            Tree.__validate_identifier(name, path)

            if not isinstance(body, dict):
                raise SchemaShapeError(path, "node body must be a mapping")

            kind = Tree.__parse_kind(body.get("type"), path)
            child = Node(
                name=name, kind=kind, parent=parent,
                tier=Tier.parse(body.get("type")),
                brief=body.get("brief"), description=body.get("description"),
            )
            parent.children[name] = child

            if kind is Kind.TASK:
                Tree.__parse_task(child, body, path)
            elif kind is Kind.ABSTRACT_SCOPE:
                Tree.__parse_abstract_scope(child, body, path)
            else:
                Tree.__parse_scope(child, body, path)

    @staticmethod
    def __parse_kind(raw: Optional[str], path: str) -> Kind:
        if raw is None:
            raise SchemaShapeError(path, "missing required 'type' key")
        if raw == "task":
            # A bare `task` used to mean "all six lifecycle hooks". Now that a
            # task declares what it *is*, there is no honest default to pick for
            # it: the tiers differ in what they cost and what the manager will
            # let you do with them, so guessing would silently decide something
            # the schema is supposed to state.
            raise SchemaShapeError(
                path,
                "'task' is no longer a type by itself - a task declares its tier. "
                f"Use one of: {Tier.names()}.\n"
                "        instant_task  - fire and forget: runs on arrival, no reply, "
                "no storage (e.g. stop, off)\n"
                "        oneshot_task  - runs once and replies (e.g. read a sensor)\n"
                "        polled_task   - runs across ticks, decides when it is done\n"
                "        stateful_task - a polled task that can be paused and resumed",
            )
        if raw not in _KINDS:
            raise SchemaShapeError(
                path, f"unknown type '{raw}'; expected one of {', '.join(_KINDS)}"
            )
        return _KINDS[raw]

    @staticmethod
    def __parse_scope(node: Node, body: Dict, path: str) -> None:
        Tree.__reject_task_keys(body, path)
        children = body.get("children", {})
        if not isinstance(children, dict):
            raise SchemaShapeError(path, "'children' must be a mapping")
        Tree.__parse_children(node, children)

    @staticmethod
    def __parse_abstract_scope(
        node: Node, body: Dict, path: str
    ) -> None:
        Tree.__reject_task_keys(body, path)
        node.instances = Tree.__parse_instances(body.get("instances"), path)
        children = body.get("children", {})
        if not isinstance(children, dict):
            raise SchemaShapeError(path, "'children' must be a mapping")
        Tree.__parse_children(node, children)

    @staticmethod
    def __parse_task(
        node: Node, body: Dict, path: str
    ) -> None:
        if "children" in body:
            raise SchemaShapeError(path, "task nodes are leaves and cannot have 'children'")

        node.params = Tree.__parse_params(body.get("params", {}), path)
        node.returns = Tree.__parse_returns(body.get("returns", body.get("return", {})), path)
        node.concurrency = Tree.__parse_concurrency(body.get("concurrency"), path)
        Tree.__validate_tier(node, path)

        if "uid" in body:
            # A uid is the framework's to assign, not the schema's to pin.
            #
            # It is a wire identifier, and the ledger already keeps each one
            # stable across regeneration - which is the only thing pinning one
            # was ever good for. What pinning *also* does is let a schema edit
            # silently repoint a number a deployed peer still associates with a
            # different task, which is the failure the ledger exists to prevent.
            # A single high pin additionally forces `optimal_mph` onto its
            # sparse backend for the whole tree, costing 10-20 KB of flash (see
            # `__generate_uid`).
            raise SchemaShapeError(
                path,
                "'uid' is assigned by the generator and cannot be set in the schema. "
                "Uids are wire identifiers: the uid ledger (.<schema>.uids.json) "
                "keeps each one stable across regeneration, which is what pinning "
                "one by hand was for - and pinning also risks repointing an id a "
                "flashed device already knows. Remove the 'uid:' line; the "
                "generator will assign one and record it in the ledger.",
            )

    @staticmethod
    def __validate_tier(node: Node, path: str) -> None:
        """Rejects a task declaring something its tier cannot honor.

        Both rules are about instant commands, which are not managed tasks: they
        run inside the call that delivered them and are gone. Anything that
        assumes an instance persisting past that call is meaningless for them,
        and silently ignoring it would leave the schema claiming a behavior the
        firmware does not have.
        """
        if node.returns and node.tier is not None and not node.tier.can_return:
            raise SchemaShapeError(
                path,
                "an instant_task cannot declare 'returns': it has no on_complete "
                "and sends no reply, so a result shape would describe something "
                "no peer ever receives. Use oneshot_task for a task that runs "
                "once and answers.",
            )

        if node.tier is Tier.INSTANT and node.concurrency is not None:
            raise SchemaShapeError(
                path,
                "an instant_task cannot declare 'concurrency': it occupies no "
                "storage and runs to completion within a single call, so there "
                "are never two instances to limit.",
            )

    @staticmethod
    def __parse_concurrency(value: object, path: str) -> Optional[int]:
        if value is None:
            return None
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise SchemaShapeError(path, "'concurrency' must be an integer >= 1")
        return value

    # ------------------------------------------------------------ param parsing

    @staticmethod
    def __parse_params(value: Dict, path: str) -> List[Param]:
        if not isinstance(value, dict):
            raise SchemaShapeError(f"{path}.params", "'params' must be a mapping of name -> type")
        return [Tree.__make_param(name, type_, f"{path}.params.{name}") for name, type_ in value.items()]

    @staticmethod
    def __parse_returns(value: Union[Dict, List], path: str) -> List[ReturnShape]:
        """Parses ``returns:`` in either of its two forms.

        A task's reply already carries a status byte, so a task may declare a
        different result shape per status. The two forms are told apart by what
        the mapping's *values* are - types, or nested shapes:

        ```yaml
        returns: { ax: float, ay: float }          # one shape, on `finished`
        returns: [uint8, float]                    # ditto, positional
        returns:                                   # one shape per status
          finished:      { ax: float, ay: float }
          task_io_error: { sensor: uint8 }
        ```
        Mixing them (a mapping whose values are part types, part shapes) is
        rejected rather than guessed at.
        """
        if not isinstance(value, (dict, list)):
            raise SchemaShapeError(
                f"{path}.returns", "'returns' must be a mapping or a list of types"
            )
        if not value:
            # No `returns:` at all (or an empty one): the task declares no result,
            # and no on_complete override is generated for it.
            return []
        if isinstance(value, list):
            return Tree.__single_shape(value, path)
        if not Tree.__is_status_keyed(value, path):
            return Tree.__single_shape(value, path)
        return Tree.__status_keyed_shapes(value, path)

    @staticmethod
    def __is_status_keyed(value: Dict, path: str) -> bool:
        """Whether this mapping is ``status -> shape`` rather than ``name -> type``."""
        nested = {key for key, body in value.items() if isinstance(body, (dict, list))}
        if not nested:
            return False
        if len(nested) != len(value):
            plain = sorted(set(value) - nested)
            raise SchemaShapeError(
                f"{path}.returns",
                "'returns' is either one shape (name -> type) or one shape per "
                "status (status -> shape), never both; "
                f"{sorted(nested)} look like status shapes but {plain} look like "
                "values. Nest the plain values under a status key",
            )
        return True

    @staticmethod
    def __single_shape(value: Union[Dict, List], path: str) -> List[ReturnShape]:
        """The unadorned form: one shape, carried by an ordinary completion."""
        key = StatusCode.DEFAULT_KEY
        name, code = StatusCode.resolve(key)
        return [ReturnShape(key=key, name=name, code=code,
                            values=Tree.__parse_values(value, f"{path}.returns"))]

    @staticmethod
    def __status_keyed_shapes(value: Dict, path: str) -> List[ReturnShape]:
        shapes: List[ReturnShape] = []
        by_code: Dict[int, str] = {}
        for key, body in value.items():
            resolved = StatusCode.resolve(key)
            if resolved is None:
                reason = (
                    "not a known status_code"
                    if not StatusCode.looks_like_status(key)
                    else "not a usable status_code"
                )
                raise UnknownStatusError(key, f"{path}.returns", reason, StatusCode.declarable())
            name, code = resolved
            rejection = StatusCode.rejection_reason(name, code)
            if rejection is not None:
                raise UnknownStatusError(
                    key, f"{path}.returns", rejection, StatusCode.declarable()
                )
            previous = by_code.get(code)
            if previous is not None:
                raise SchemaShapeError(
                    f"{path}.returns",
                    f"'{key}' and '{previous}' are the same status code "
                    f"(0x{code:02X}); declare it once",
                )
            by_code[code] = key
            shapes.append(ReturnShape(
                key=key, name=name, code=code,
                values=Tree.__parse_values(body, f"{path}.returns.{key}"),
            ))
        # Wire order is the schema's for values, but shapes themselves are a set:
        # order them by code so generated switches and docs read predictably.
        shapes.sort(key=lambda shape: shape.code)
        return shapes

    @staticmethod
    def __parse_values(value: Union[Dict, List], path: str) -> List[Param]:
        if isinstance(value, list):
            return [Tree.__make_param(None, t, f"{path}[{i}]") for i, t in enumerate(value)]
        if isinstance(value, dict):
            return [Tree.__make_param(name, t, f"{path}.{name}") for name, t in value.items()]
        raise SchemaShapeError(path, "a result shape must be a mapping or a list of types")

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
        for key in ("params", "returns", "return", "uid", "concurrency"):
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
                brief=abstract.brief,
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
            tier=src.tier,  # a cloned task is the same kind of task
            brief=src.brief,
            description=src.description,
            parent=parent,
            uid=None,  # cloned tasks always receive generated uids
            params=copy.deepcopy(src.params),
            returns=copy.deepcopy(src.returns),
            concurrency=src.concurrency,
            instances=list(src.instances) if src.instances is not None else None,
        )
        for child_name, child in src.children.items():
            clone.children[child_name] = Tree.__copy_node(child, clone)
        return clone

    # ------------------------------------------------------- pass 3: uid pass

    @staticmethod
    def __assign_uids(root: Node, ledger: Optional[UidLedger] = None) -> None:
        # Nothing claims a uid before this pass any more - the schema cannot pin
        # one - so the map of what is taken starts empty and is filled here,
        # first from the ledger and then by packing the rest from zero.
        used_uids: Dict[int, str] = {}
        tasks = Tree.__collect_tasks(root)
        # Retired uids stay reserved, so they occupy the space just like live ones.
        occupied = len(tasks) + (len(ledger.retired) if ledger is not None else 0)
        uid_bytes = Tree.__uid_width(occupied)
        if ledger is not None:
            # A width only ever grows: narrowing it would re-derive every uid a
            # peer already knows (see etask.schema.uid_ledger).
            uid_bytes = ledger.width(uid_bytes)

        pending = [task for task in tasks if task.uid is None]
        # Sorted by path, not by traversal order: uids are handed out lowest-first,
        # so *who asks first* decides who gets the lower number. Ordering by path
        # makes that independent of how the YAML happens to be laid out -
        # reordering siblings must never renumber the wire.
        pending.sort(key=Tree.__path)

        if ledger is not None:
            Tree.__reuse_ledger_uids(pending, used_uids, ledger)

        # Retired uids stay reserved: a new task must not inherit the id a peer
        # still associates with a task that used to exist. (Live ledger uids are
        # already in `used_uids` by now.)
        reserved = ledger.reserved() if ledger is not None else {}
        for task in pending:
            if task.uid is None:
                path = Tree.__path(task)
                task.uid = Tree.__generate_uid(path, used_uids, uid_bytes, reserved)
                used_uids[task.uid] = path
        root.uid_bytes = uid_bytes

        if ledger is not None:
            ledger.record({Tree.__path(task): task.uid for task in tasks}, uid_bytes)

    @staticmethod
    def __reuse_ledger_uids(
        pending: List[Node], used_uids: Dict[int, str], ledger: UidLedger
    ) -> None:
        """Hands each task back the uid it already owned, where one is on record."""
        for task in pending:
            path = Tree.__path(task)
            uid = ledger.known(path)
            if uid is None:
                continue
            # Nothing can be holding this uid: the ledger's own are unique, the
            # schema can no longer pin one, and packed uids are not handed out
            # until after this loop. A collision would mean a corrupt ledger.
            assert uid not in used_uids, (
                f"uid {uid} is claimed twice; the ledger beside this schema is "
                f"inconsistent"
            )
            task.uid = uid
            used_uids[uid] = path

    @staticmethod
    def __collect_tasks(node: Node) -> List[Node]:
        tasks = [node] if node.is_task else []
        for child in node.children.values():
            tasks.extend(Tree.__collect_tasks(child))
        return tasks

    @staticmethod
    def __uid_width(total_tasks: int) -> int:
        """The narrowest uid width that fits every task, live and retired.

        Uids are packed from zero, so the count alone decides the width - there
        is no pinned value that could sit above it.
        """
        for width in _UID_WIDTHS_BYTES:
            if total_tasks <= (1 << (width * 8)):
                return width
        raise ValueError(f"too many tasks ({total_tasks}) to fit any supported uid width")

    @staticmethod
    def __generate_uid(
        path: str,
        used_uids: Dict[int, str],
        uid_bytes: int,
        reserved: Dict[int, str],
    ) -> int:
        """The lowest uid nobody holds and nobody has retired.

        Uids used to be seeded from ``blake2b(path)``. That predates the ledger,
        and made sense while a uid was a pure function of the schema: spreading
        them out made an accidental collision unlikely. The ledger now records
        what each path owns, so the seed only ever decides the number for a task
        that has *never* had one - and a hash spreads those across the whole
        width for no benefit.

        The cost of that sprawl is real. `dispatch_factory` keys on
        `etools::hashing::optimal_mph`, which chooses between a direct-address
        table (LLUT, sized `max_uid + 1`) and two-level perfect hashing (FKS,
        sized by the *count*). Hashed uids at two bytes reach toward 65,535, so
        LLUT would cost 131,072 bytes and FKS wins by default. Packed uids keep
        `max_uid` next to the task count, and LLUT - a bounds check and one load
        - wins instead. Measured on the emitted table:

            tasks   hashed (FKS)   packed (LLUT)   saved
              260       10,696 B          520 B   10,176 B
              400       11,584 B          800 B   10,784 B
              600       22,000 B        1,200 B   20,800 B

        and a lookup drops from 29 instructions to 13.

        Only `max_uid` matters, not contiguity: retiring a task leaves a hole,
        and holes are free. A project that churns tasks over its life ends with
        `max_uid` near the number ever created rather than the number live,
        which grows slowly enough that LLUT stays the cheaper option for a long
        time - and `optimal_mph` switches back on its own if it ever does not.

        @param path The task's dotted path, for the error message only.
        @param used_uids Uids already taken, by path.
        @param uid_bytes The tree's uid width in bytes.
        @param reserved Uids held by retired tasks; never handed out again.
        @return The lowest free uid.
        """
        capacity = 1 << (uid_bytes * 8)
        uid = 0
        while uid in used_uids or uid in reserved:
            uid += 1
        if uid >= capacity:
            raise ValueError(
                f"no free uid left at width {uid_bytes} byte(s) for '{path}' "
                f"({len(used_uids)} in use, {len(reserved)} reserved by the ledger)"
            )
        return uid

    # ------------------------------------- pass 4: link subsystem resolution

    @staticmethod
    def __resolve_link_subsystems(root: Node) -> None:
        """Resolves every link's ``subsystems:`` to the uids it carries.

        @param root The built tree, with uids assigned.
        @throws SchemaShapeError If a declared subsystem names nothing, names a
                task rather than a scope, or names a scope holding no task.
        """
        if not root.links:
            return

        root.links.resolve(
            lambda link_name, paths: Tree.__carried_uids(root, link_name, paths)
        )

    @staticmethod
    def __carried_uids(root: Node, link_name: str, paths: "tuple[str, ...]") -> FrozenSet[int]:
        """The uids beneath a link's declared subsystem paths.

        @param root The built tree.
        @param link_name The link, for error messages.
        @param paths Its declared subsystem paths.
        @return Every uid carried, from every named subtree.
        @throws SchemaShapeError If a path does not resolve to a scope with tasks.
        """
        uids: Set[int] = set()
        for path in paths:
            scope = Tree.__resolve_scope(root, link_name, path)
            beneath = [task.uid for task in Tree.__collect_tasks(scope) if task.uid is not None]

            if not beneath:
                raise SchemaShapeError(
                    f"links.{link_name}.subsystems",
                    f"'{path}' holds no task, so listing it carries nothing. "
                    "Name a subsystem that has tasks beneath it, or drop the entry.",
                )
            uids.update(beneath)
        return frozenset(uids)

    @staticmethod
    def __resolve_scope(root: Node, link_name: str, path: str) -> Node:
        """Walks one dotted subsystem path to its scope.

        @param root The built tree.
        @param link_name The link, for error messages.
        @param path The dotted path, e.g. ``sensors.imu``.
        @return The scope node it names.
        @throws SchemaShapeError If a segment does not exist, or the path names
                a task rather than a scope.
        """
        node = root
        walked: List[str] = []

        for segment in path.split("."):
            child = node.children.get(segment)
            if child is None:
                raise SchemaShapeError(
                    f"links.{link_name}.subsystems",
                    f"'{path}' names no subsystem in this system"
                    + (f" ('{'.'.join(walked)}' exists, but has no '{segment}')"
                       if walked else "")
                    + f". Available here: {Tree.__nameable(node)}.",
                )
            walked.append(segment)
            node = child

        if node.is_task and len(walked) > 1:
            # Refused rather than allowed: frame size is the only thing a
            # narrower list would buy, and it would buy it by letting the schema
            # claim that one task of a subsystem travels a different wire than
            # its siblings - which is not how a device is wired.
            #
            # A *root-level* task is the exception, handled by the length test
            # above: it belongs to no subsystem, so naming it stranded nobody.
            # Refusing it would make a top-level failsafe unreachable from every
            # link that restricts its subsystems, which is the worst task to
            # make unreachable.
            raise SchemaShapeError(
                f"links.{link_name}.subsystems",
                f"'{path}' is a task, not a subsystem. A link carries whole "
                "subsystems, because the parts of a device are wired to a bus "
                "together - splitting one across links would say that "
                f"'{path}' arrives over {link_name} while its siblings arrive "
                f"elsewhere. Name its enclosing scope ('{'.'.join(walked[:-1])}') "
                "instead. A task declared at the top level, belonging to no "
                "subsystem, may be named directly.",
            )
        return node

    @staticmethod
    def __nameable(node: Node) -> str:
        """What a subsystem path could legally name at this point.

        Scopes anywhere, plus tasks at the top level - those belong to no
        subsystem, so a link names them directly or cannot carry them at all.

        @param node The scope reached so far; the root when nothing is walked.
        @return A comma-separated list, for an error message.
        """
        at_root = node.parent is None
        names = [
            name for name, child in node.children.items()
            if not child.is_task or at_root
        ]
        return ", ".join(names) if names else "(no nested subsystems)"

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
