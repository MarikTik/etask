class AnchorNotFoundError(ValueError):
    """Raised when an existing task file lacks the constructor signature anchor.

    Without the anchor the updater cannot know which line to rewrite, so it
    refuses to touch the file rather than guess.
    """

    def __init__(self, path: str, anchor: str):
        super().__init__(f"no '{anchor}' anchor found in '{path}'")
        self.path = path
        self.anchor = anchor
