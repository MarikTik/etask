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
        trailing = text.endswith("\n")
        lines = text.splitlines()
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
        rebuilt = lines[:begin] + DocRegion.render(name, fresh_body, indent) + lines[end + 1:]
        out = "\n".join(rebuilt)
        return out + "\n" if trailing else out

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
