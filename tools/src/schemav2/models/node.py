from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from schemav2.models.param import Param


class Kind(Enum):
    ROOT = "root"
    SCOPE = "scope"
    ABSTRACT_SCOPE = "abstract_scope"
    TASK = "task"


@dataclass
class Node:
    name: str
    kind: Kind
    description: Optional[str] = None
    parent: Optional["Node"] = None
    children: Dict[str, "Node"] = field(default_factory=dict)

    # task-only
    uid: Optional[int] = None
    params: Optional[List[Param]] = None
    returns: Optional[List[Param]] = None

    # abstract_scope-only: the concrete instance names this scope expands into
    instances: Optional[List[str]] = None

    # root-only: uid byte width shared by every uid in the tree
    uid_bytes: Optional[int] = None

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

        A task receives its parent scope (downward composition). Tasks whose
        parent is the document root receive no scope (``None``).
        """
        if self.parent is None or self.parent.is_root:
            return None
        return self.parent
