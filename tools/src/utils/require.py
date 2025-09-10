
def require(cond: bool, exc: Exception) -> None:
    if not cond:
        raise exc