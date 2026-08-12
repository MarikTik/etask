class RenameError(ValueError):
    """Raised when a task rename cannot be performed as requested.

    Covers an unknown task path, a target name colliding with a sibling, and
    (for now) renaming a task that lives under an abstract scope, whose fan-out
    rides with the deferred abstract-scope codegen.
    """

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason
