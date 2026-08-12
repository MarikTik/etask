class SchemaShapeError(ValueError):
    """Raised when the schema structure is malformed.

    Covers a missing/invalid ``type``, a task node carrying ``children``, a
    scope carrying ``params``/``returns``, non-dict node bodies, and similar
    structural violations of the v2 grammar.
    """

    def __init__(self, path: str, reason: str):
        super().__init__(f"malformed schema at '{path}': {reason}")
        self.path = path
        self.reason = reason
