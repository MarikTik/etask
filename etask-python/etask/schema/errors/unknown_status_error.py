class UnknownStatusError(ValueError):
    """Raised when a ``returns:`` key does not name a declarable status code.

    Either the key is not a ``status_code`` at all, or it names one a completing
    task can never send (a manager/API code, or a framework-reserved one such as
    ``result_too_large``) - see :mod:`etask.schema.models.status_code`.
    """

    def __init__(self, key: str, path: str, reason: str, allowed: "list[str]"):
        super().__init__(
            f"invalid result status '{key}' at '{path}': {reason}. "
            f"Declarable statuses: {', '.join(allowed)}"
        )
        self.key = key
        self.path = path
        self.reason = reason
        self.allowed = allowed
