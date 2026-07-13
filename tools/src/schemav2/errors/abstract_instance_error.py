class AbstractInstanceError(ValueError):
    """Raised when an abstract_scope's ``instances`` list is invalid.

    Covers a missing/empty list, duplicate instance names, and instance names
    that collide with existing sibling nodes.
    """

    def __init__(self, path: str, reason: str):
        super().__init__(f"invalid abstract scope at '{path}': {reason}")
        self.path = path
        self.reason = reason
