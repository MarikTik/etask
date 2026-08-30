from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, Iterator, List, Optional, Tuple

from etask.schema.errors.schema_shape_error import SchemaShapeError
from etask.schema.models.link import Link


#: How a link name is checked. The rule - a C++ identifier that collides with
#: no keyword - is the same one every node name obeys, and it lives in
#: :class:`etask.schema.tree.Tree`, which owns it for the whole schema. It is
#: passed in rather than duplicated here: a link name becomes a namespace
#: exactly like a scope name does, and two copies of that rule would drift.
NameValidator = Callable[[str, str], None]

#: How a link's declared subsystem paths become task uids. Takes the link name
#: (for error messages) and its declared paths; returns the uids of every task
#: beneath them. Passed in rather than implemented here because walking the tree
#: is :class:`etask.schema.tree.Tree`'s job, and this module must not depend on
#: the node model it would otherwise have to import.
SubsystemResolver = Callable[[str, Tuple[str, ...]], FrozenSet[int]]


@dataclass(frozen=True)
class Links:
    """The external links a system declares - the schema's ``links:`` section.

    Optional, and empty when omitted: a project with no ``links:`` speaks only
    over the internal channel, which is what the great majority of systems do
    and must keep working untouched.

    The collection exists rather than a bare list because "which links are
    there" is asked far more often than "what is link *n*", and because the one
    rule that spans links - distinct names, since each becomes a namespace -
    has to live somewhere.
    """

    #: The links in declaration order, keyed by name. Ordered so generated
    #: output follows the schema rather than a hash.
    by_name: Dict[str, Link] = field(default_factory=dict)

    #: Per link, the uids of the tasks it carries - the resolution of that
    #: link's ``subsystems:``, filled in by :meth:`resolve` once the tree
    #: exists. A link that carries everything is absent from this map rather
    #: than mapped to every uid: "carries everything" has to stay distinguishable
    #: from "happens to list them all", because only the former keeps its
    #: meaning when a task is added later.
    carried: Dict[str, FrozenSet[int]] = field(default_factory=dict)

    def __bool__(self) -> bool:
        """Whether the system declares any external link at all."""
        return bool(self.by_name)

    def __len__(self) -> int:
        """How many links are declared."""
        return len(self.by_name)

    def __iter__(self) -> Iterator[Link]:
        """Iterates the links in declaration order."""
        return iter(self.by_name.values())

    @property
    def names(self) -> List[str]:
        """The link names, in declaration order."""
        return list(self.by_name)

    def get(self, name: str) -> Optional[Link]:
        """The link with this name, or ``None``.

        @param name The link name.
        @return The link, if one is declared under that name.
        """
        return self.by_name.get(name)

    def carries_everything(self, name: str) -> bool:
        """Whether this link carries every task the device has.

        True for a link that declared no ``subsystems:``. Kept separate from
        :meth:`uids_for` because a link that carries everything must keep doing
        so as tasks are added, which a snapshot of today's uids would not.

        @param name The link name.
        @return Whether the link is unrestricted.
        """
        return name not in self.carried

    def uids_for(self, name: str, every_uid: FrozenSet[int]) -> FrozenSet[int]:
        """The uids this link actually carries.

        @param name The link name.
        @param every_uid Every uid in the system, returned for an unrestricted
               link. The caller supplies it rather than the collection holding
               it, so the "carries everything" link keeps no stale copy.
        @return The carried uids.
        """
        return self.carried.get(name, every_uid)

    def resolve(self, resolver: SubsystemResolver) -> None:
        """Turns each link's declared ``subsystems:`` into a set of task uids.

        Deferred to its own pass because the names cannot be checked when they
        are parsed: ``links:`` is read before the tree is built, and an abstract
        scope does not become its instances until later still. By the time this
        runs, both are settled, so a name that does not resolve is genuinely
        wrong rather than merely early.

        @param resolver Maps one link's declared paths to the uids beneath them,
               raising if a path names nothing or names a task. See
               :data:`SubsystemResolver`.
        @throws SchemaShapeError If any declared subsystem cannot be resolved.
        """
        for link in self:
            if link.subsystems is not None:
                self.carried[link.name] = resolver(link.name, link.subsystems)

    @staticmethod
    def parse(body: object, validate_name: NameValidator) -> "Links":
        """Builds the collection from the schema's ``links:`` mapping.

        @param body The raw value of the top-level ``links:`` key.
        @param validate_name Checks one link name, raising if it is not usable
               as a C++ identifier. See :data:`NameValidator`.
        @return The parsed links, in declaration order.
        @throws SchemaShapeError If the section is not a mapping of names to
                link bodies, or any link is malformed.
        @throws InvalidIdentifierError If a link name cannot be a namespace.
        """
        if not isinstance(body, dict):
            raise SchemaShapeError(
                "links",
                "'links' must be a mapping of link names to link bodies:\n"
                "        links:\n"
                "          serial:\n"
                "            transport: uart",
            )

        links: Dict[str, Link] = {}
        for name in body:
            path = f"links.{name}"
            # A YAML mapping cannot repeat a key, so distinctness only has to be
            # enforced against what a *case difference* would collapse to - and
            # it does not collapse here, so the loop below is the whole rule.
            # What can still collide is a name already taken by a link parsed
            # from a merged or JSON source, which this catches too.
            if name in links:
                raise SchemaShapeError(
                    path,
                    f"duplicate link name '{name}'; each link becomes its own "
                    "namespace, so two links cannot share a name. Rename one.",
                )
            validate_name(name, path)
            links[name] = Link.parse(name, body[name], path)

        return Links(by_name=links)
