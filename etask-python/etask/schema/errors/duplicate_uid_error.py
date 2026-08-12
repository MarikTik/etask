class DuplicateUidError(ValueError):
    def __init__(self, uid: int, first_path: str, second_path: str):
        super().__init__(
            f"duplicate uid {uid}: already assigned to '{first_path}', "
            f"redefined at '{second_path}'"
        )
        self.uid = uid
        self.first_path = first_path
        self.second_path = second_path
