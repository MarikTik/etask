class UnknownTypeError(ValueError):
    """Raised when a param/return declares a type outside the allowed set."""

    def __init__(self, type_name: str, path: str, allowed: "list[str]"):
        super().__init__(
            f"unknown type '{type_name}' at '{path}'; allowed types: {', '.join(allowed)}"
        )
        self.type_name = type_name
        self.path = path
        self.allowed = allowed
