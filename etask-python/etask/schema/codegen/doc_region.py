import hashlib
from typing import List, Optional, Tuple

_BEGIN = "//! etask:doc"
_END = "//! etask:end doc"


class DocRegion:
    """A schema-derived doc block that stays in sync until the user edits it.

    The generator wraps each *narrative* doc comment - the ``@file`` / ``@brief``
    / ``@description`` prose seeded from a node's schema ``brief``/``description`` -
    in a pair of anchors carrying a digest of the exact text the generator wrote::

        //! etask:doc <name> <digest>
        /** ... */
        //! etask:end doc <name>

    On regeneration the block is refreshed from the schema **only while its
    current content still hashes to <digest>** - i.e. the user has not touched
    it. The moment the prose is hand-edited the digest no longer matches, and the
    block is left byte-for-byte alone from then on ("sync until you touch it").

    This governs only prose. Constructor signatures (``//! etask:sig``) and
    child-context lists (``//! etask:managed``) are reconciled by their own
    mechanisms; per-hook boilerplate docs are written once and never marked.
    A file with no markers (e.g. generated before this feature) is left untouched.
    """

    @staticmethod
    def digest(body: List[str]) -> str:
        return hashlib.blake2b("\n".join(body).encode("utf-8"), digest_size=6).hexdigest()

    @staticmethod
    def render(name: str, body: List[str], indent: str = "") -> List[str]:
        """Marker-wrapped ``body`` (the doc block lines), digest computed over it."""
        return [f"{indent}{_BEGIN} {name} {DocRegion.digest(body)}", *body, f"{indent}{_END} {name}"]

    @staticmethod
    def names(text: str) -> List[str]:
        """The region names present in ``text``, in order of appearance."""
        out: List[str] = []
        for line in text.splitlines():
            parts = line.strip().split()
            if len(parts) >= 4 and f"{parts[0]} {parts[1]}" == _BEGIN:
                out.append(parts[2])
        return out

    @staticmethod
    def extract(text: str, name: str) -> List[str]:
        """The body lines of region ``name`` (between the markers), or ``[]``."""
        lines = text.splitlines()
        loc = DocRegion.__locate(lines, name)
        if loc is None:
            return []
        begin, end = loc
        return lines[begin + 1:end]

    @staticmethod
    def reconcile(text: str, name: str, fresh_body: List[str]) -> str:
        """Refresh region ``name`` to ``fresh_body`` iff the user has not edited it.

        No marker for ``name`` -> ``text`` unchanged. Current content edited (its
        digest no longer matches the stored one) -> left verbatim. Otherwise the
        whole region is rewritten with ``fresh_body`` and a new digest.
        """
        # keepends, so every line carries its own terminator and the lines this
        # does not touch keep theirs. Splitting bare and rejoining with "\n"
        # rewrote CRLF to LF across the whole file - refreshing one region then
        # showed up as a whole-file diff. signature_updater already does this.
        raw = text.splitlines(keepends=True)
        lines = [line.rstrip("\r\n") for line in raw]
        loc = DocRegion.__locate(lines, name)
        if loc is None:
            return text
        begin, end = loc
        marker = lines[begin]
        stored = marker.strip().split()[-1]
        current_body = lines[begin + 1:end]
        if DocRegion.digest(current_body) != stored:
            return text  # user-edited: hands off from here on
        indent = marker[:len(marker) - len(marker.lstrip())]

        # The replacement region adopts the ending of the line it replaces, so a
        # CRLF file stays CRLF and an LF file stays LF. The region's own last
        # line takes the old region's, which is what followed it before.
        def ending(index: int) -> str:
            line = raw[index]
            return line[len(line.rstrip("\r\n")):]

        rendered = DocRegion.render(name, fresh_body, indent)
        body_ending = ending(begin) or ("\n" if len(raw) > 1 else "")
        rebuilt = (
            raw[:begin]
            + [line + body_ending for line in rendered[:-1]]
            + [rendered[-1] + ending(end)]
            + raw[end + 1:]
        )
        return "".join(rebuilt)

    @staticmethod
    def __locate(lines: List[str], name: str) -> Optional[Tuple[int, int]]:
        begin = None
        for i, line in enumerate(lines):
            s = line.strip()
            if begin is None and s.startswith(f"{_BEGIN} {name} "):
                begin = i
            elif begin is not None and s == f"{_END} {name}":
                return begin, i
        return None
