from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from etask.schema.models.budget import Budget
from etask.schema.models.links import Links
from etask.schema.models.param import Param
from etask.schema.models.return_shape import ReturnShape
from etask.schema.models.tier import Tier


class Kind(Enum):
    ROOT = "root"
    SCOPE = "scope"
    ABSTRACT_SCOPE = "abstract_scope"
    TASK = "task"


@dataclass
class Node:
    name: str
    kind: Kind
    brief: Optional[str] = None
    description: Optional[str] = None
    parent: Optional["Node"] = None
    children: Dict[str, "Node"] = field(default_factory=dict)

    # task-only: which tier this task declares - what it *is*, and so which
    # lifecycle hooks it carries and which manager owns it. Always set on a task
    # node; None on every other kind.
    tier: Optional[Tier] = None
    uid: Optional[int] = None
    params: Optional[List[Param]] = None
    #: One entry per result shape the task can reply with, keyed by status code.
    #: A plain ``returns:`` yields a single ``finished`` shape; empty means the
    #: task returns nothing at all.
    returns: Optional[List[ReturnShape]] = None
    # task-only: how many instances of this task's uid may run concurrently.
    # None means the default of 1 (a bare task type); > 1 lowers to capacity<T, N>.
    concurrency: Optional[int] = None

    # abstract_scope-only: the concrete instance names this scope expands into
    instances: Optional[List[str]] = None

    # root-only: uid byte width shared by every uid in the tree
    uid_bytes: Optional[int] = None

    # root-only: the schema's `budget:` section - how many tasks of each managed
    # tier may be live at once. Absent tiers fall back to the sum of that tier's
    # per-task concurrency. Always set on the root (a default-constructed Budget
    # when the schema declares none); None on every other kind.
    budget: Optional["Budget"] = None

    # root-only: the schema's `links:` section - the external links this system
    # speaks over, each becoming a generated packet type. Always set on the root
    # (an empty Links when the schema declares none, which is the internal-
    # channel-only case); None on every other kind.
    links: Optional["Links"] = None

    @property
    def doc_brief(self) -> Optional[str]:
        """One-line summary for documentation.

        The ``brief`` when given, else the ``description`` as a fallback, else
        ``None``. Both schema fields are optional and unenforced; a node with
        neither simply carries no generated documentation text.
        """
        text = self.brief or self.description
        return text.strip() if text else None

    @property
    def doc_detail(self) -> Optional[str]:
        """Longer documentation paragraph, or ``None``.

        Only the ``description`` counts here, and only when a distinct ``brief``
        already carries the summary - otherwise the description has already been
        promoted to the brief (see :attr:`doc_brief`) and repeating it would be
        redundant.
        """
        if self.brief and self.description:
            return self.description.strip()
        return None

    @property
    def finished_shape(self) -> Optional[ReturnShape]:
        """The shape of an ordinary completion, if the task declares one.

        The common case by far - a task that returns one set of values returns
        them on ``task_finished`` - so it is worth naming rather than making
        every caller search the list.
        """
        for shape in self.returns or []:
            if shape.is_default:
                return shape
        return None

    @property
    def is_root(self) -> bool:
        return self.kind is Kind.ROOT

    @property
    def is_task(self) -> bool:
        return self.kind is Kind.TASK

    @property
    def is_scope(self) -> bool:
        return self.kind is Kind.SCOPE

    @property
    def is_abstract_scope(self) -> bool:
        return self.kind is Kind.ABSTRACT_SCOPE

    @property
    def injected_scope(self) -> Optional["Node"]:
        """The scope object a task is constructed with.

        A task receives its parent scope (downward composition). A task at the
        document root receives the root itself - the ``sys`` scope, whose
        ``sys::context`` is the composition root that owns every subsystem's
        context - so system-level tasks (e.g. ``reboot``) can reach the whole
        tree. Only a parentless node (the root itself) has no injected scope.
        """
        return self.parent
