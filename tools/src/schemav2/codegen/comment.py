def escape_block(text: str) -> str:
    """Make user text safe to drop inside a C ``/* ... */`` doc block.

    C block comments do not nest: a ``*/`` in user-supplied ``brief``/``description``
    text would close the generated doc block early and turn the rest of the file
    into a compile error. A stray ``/*`` is merely a ``-Wcomment`` warning, but is
    escaped too so generated files stay warning-clean. Both delimiters get a space
    inserted, which breaks the token while staying readable.
    """
    return text.replace("*/", "* /").replace("/*", "/ *")
