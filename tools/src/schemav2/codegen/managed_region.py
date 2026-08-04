import re
from typing import List, Tuple


class ManagedRegionError(Exception):
    """Raised when a file that should carry a managed region does not."""


class ManagedRegion:
    """Reconciles a generator-owned list embedded in a user-owned file.

    A *managed region* is a run of lines a user file hands to the generator:
    ``//! etask:managed <name>`` opens it, ``//! etask:end <name>`` closes it, and
    each generated line inside carries ``//! etask:item <identity>``. Everything
    outside the region is user-owned and never touched.

    On each run the region is reconciled against the schema-desired item set *by
    identity* - never by wholesale replacement:

    - an item present in both file and schema keeps the file's line **verbatim**
      (so a user's edit to that line survives);
    - an item in the schema but not the file is **appended**;
    - an item in the file but no longer in the schema is **removed**.

    Existing line order is preserved and new items are appended, so the result is
    stable under reordering and under user edits. This is the list-shaped sibling
    of the single-line ``//! etask:sig`` updater, and is reusable for any
    "schema drives part of a user file" need, not just contexts.
    """

    _OPEN = r"//!\s*etask:managed\s+{name}\b"
    _CLOSE = r"//!\s*etask:end\s+{name}\b"
    _ITEM = re.compile(r"//!\s*etask:item\s+(\S+)\s*$")

    @staticmethod
    def item_line(code: str, identity: str, indent: str = "") -> str:
        """Format one canonical managed item line (code + identity marker)."""
        return f"{indent}{code}  //! etask:item {identity}"

    @staticmethod
    def reconcile(text: str, name: str, desired: List[Tuple[str, str]]) -> str:
        """Return ``text`` with the ``name`` region reconciled to ``desired``.

        @param desired Ordered ``(identity, code)`` pairs - the schema's wanted
                       items. ``code`` is the member text without the marker
                       (e.g. ``"leg::context leg;"``); a newly-appended line is
                       formatted from it, an existing line is kept as written.
        @raises ManagedRegionError if the region markers are absent.
        """
        newline = "\n"
        lines = text.split(newline)

        open_re = re.compile(ManagedRegion._OPEN.format(name=re.escape(name)))
        close_re = re.compile(ManagedRegion._CLOSE.format(name=re.escape(name)))
        open_i = next((i for i, ln in enumerate(lines) if open_re.search(ln)), None)
        close_i = next((i for i, ln in enumerate(lines) if close_re.search(ln)), None)
        if open_i is None or close_i is None or close_i <= open_i:
            raise ManagedRegionError(
                f"managed region '{name}' not found (need '//! etask:managed {name}' "
                f"... '//! etask:end {name}')"
            )

        indent = re.match(r"\s*", lines[open_i]).group(0)
        body = lines[open_i + 1:close_i]
        desired_map = dict(desired)

        new_body: List[str] = []
        emitted = set()
        for ln in body:
            m = ManagedRegion._ITEM.search(ln)
            if m:
                identity = m.group(1)
                if identity in desired_map:
                    new_body.append(ln)      # keep verbatim (never replace)
                    emitted.add(identity)
                # else: item left the schema -> drop
            else:
                new_body.append(ln)          # loose user line -> preserve
        for identity, code in desired:       # append items new to the schema
            if identity not in emitted:
                new_body.append(ManagedRegion.item_line(code, identity, indent))

        result = lines[:open_i + 1] + new_body + lines[close_i:]
        return newline.join(result)

    @staticmethod
    def render_block(name: str, header: str, desired: List[Tuple[str, str]], indent: str = "") -> List[str]:
        """Render a fresh region block (for first-time file generation).

        @return The region's lines: the open marker (with a short header note),
                one item line per desired entry, and the close marker.
        """
        lines = [f"{indent}//! etask:managed {name} - {header}"]
        for identity, code in desired:
            lines.append(ManagedRegion.item_line(code, identity, indent))
        lines.append(f"{indent}//! etask:end {name}")
        return lines
