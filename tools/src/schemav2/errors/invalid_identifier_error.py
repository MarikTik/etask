class InvalidIdentifierError(ValueError):
    """Raised when a node name is not a legal C++ identifier.

    Node names become C++ namespaces, classes and directories, so they must be
    valid identifiers and must not collide with reserved keywords.
    """

    def __init__(self, name: str, path: str, reason: str):
        super().__init__(f"invalid identifier '{name}' at '{path}': {reason}")
        self.name = name
        self.path = path
        self.reason = reason
