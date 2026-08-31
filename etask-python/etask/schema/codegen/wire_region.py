from typing import List, Optional

from etask.schema.codegen.naming import Naming


class WireRegion:
    """The generated block of a task class that the framework reads, not the user.

    A task file is written once and then belongs to its author - bodies, extra
    members, comments. Three declarations inside it are not theirs, because the
    framework reads them off the class and they are projections of the schema:

    - ``uid``    - which task this is on the wire.
    - ``params`` - the constructor's parameter types, in wire order.
    - ``scope``  - the context the task is injected with.

    Those were emitted once and never refreshed, which is a wire-contract bug:
    adding a parameter to an existing task rewrote its constructor (the
    ``etask:sig`` anchor) and left ``params`` naming the *old* argument list. The
    manager unpacks a payload according to ``params``, so the device then decoded
    a different argument list than the peer encoded - and it compiled, and the
    generated Python client had the new signature, so the two ends disagreed
    silently. That is precisely the failure the schema fingerprint exists to
    catch, arriving from inside the generator where the fingerprint cannot see it.

    So the block is delimited and rewritten in full on every generate. Unlike
    :class:`DocRegion` there is no digest and no "until the user edits it": these
    lines have exactly one correct value, and a hand edit to them is a bug rather
    than a preference to preserve.
    """

    @staticmethod
    def extract(text: str) -> Optional[List[str]]:
        """The wire block of a rendered file, markers included.

        @param text A rendered or on-disk task header.
        @return The block's lines, or ``None`` if the file has no wire region -
                which is what an older generated file looks like.
        """
        lines = text.splitlines(keepends=True)
        begin = WireRegion.__find(lines, Naming.wire_begin)
        end = WireRegion.__find(lines, Naming.wire_end)
        if begin is None or end is None or end < begin:
            return None
        return lines[begin:end + 1]

    @staticmethod
    def reconcile(text: str, fresh: str) -> str:
        """Replaces a file's wire block with the one the schema now implies.

        @param text The file as it exists.
        @param fresh The freshly rendered file, to take the new block from.
        @return The file with its wire block replaced. Unchanged if either side
                has no wire region: a file predating the markers is left for
                :meth:`migrate` to deal with, since replacing a block that is not
                delimited would mean guessing where it starts.
        """
        replacement = WireRegion.extract(fresh)
        if replacement is None:
            return text

        lines = text.splitlines(keepends=True)
        begin = WireRegion.__find(lines, Naming.wire_begin)
        end = WireRegion.__find(lines, Naming.wire_end)
        if begin is None or end is None or end < begin:
            return text

        return "".join(lines[:begin] + replacement + lines[end + 1:])

    @staticmethod
    def needs_migration(text: str) -> bool:
        """Whether a task file predates the wire markers.

        Such a file carries the three declarations undelimited, so there is no
        block to replace. Detected by the marker's absence plus a ``uid`` line,
        so an unrelated file is not mistaken for one.

        @param text The file as it exists.
        @return Whether the file has the declarations but not the markers.
        """
        return Naming.wire_begin not in text and "static constexpr global::task_id uid" in text

    @staticmethod
    def migrate(text: str, fresh: str) -> Optional[str]:
        """Adds the markers to a file that predates them, and refreshes the block.

        Done automatically rather than asked of the user. The alternative is a
        note per task file telling them to delete a block by hand, which for a
        real project is dozens of identical edits - and until they are made, the
        declarations stay stale, which is the bug this whole region exists to
        stop. A migration that nobody performs is not a migration.

        The old block is located by its bounds rather than by matching its text:
        it begins at the ``uid`` declaration and ends before the class's closing
        brace, and everything in between is generator-authored. Bounded that way,
        a user's own member declared *after* the block is preserved, while the
        three declarations and their doc comments are replaced wholesale.

        @param text The file as it exists, without markers.
        @param fresh The freshly rendered file, to take the new block from.
        @return The migrated file, or ``None`` if the old block's bounds could
                not be found - in which case the caller should report rather than
                guess, since a wrong cut would delete the user's code.
        """
        replacement = WireRegion.extract(fresh)
        if replacement is None:
            return None

        lines = text.splitlines(keepends=True)

        begin = None
        for index, line in enumerate(lines):
            if "static constexpr global::task_id uid" in line:
                begin = index
                break
        if begin is None:
            return None

        # Walk back over the `uid` declaration's own doc comment, so migrating
        # does not leave an orphaned `/// @brief` above the new block.
        while begin > 0 and lines[begin - 1].lstrip().startswith(("///", "*", "/**", "*/")):
            begin -= 1

        # The block ends after the LAST of the three declarations that is
        # actually present - not at the class's closing brace. Cutting to the
        # brace would be simpler and would delete anything the user added below
        # the block, which some projects do (a private member, a helper). So the
        # end is found from the declarations themselves, and one line of a user's
        # is worth more than the tidiness of the cut.
        end = None
        for index in range(begin, len(lines)):
            stripped = lines[index].lstrip()
            if stripped.startswith(("static constexpr global::task_id uid",
                                    "using params =",
                                    "static constexpr auto scope =",
                                    "static constexpr etask::core::scope_index_t scope =")):
                end = index
        if end is None:
            return None

        return "".join(lines[:begin] + replacement + lines[end + 1:])

    @staticmethod
    def __find(lines: List[str], marker: str) -> Optional[int]:
        """The index of the line carrying `marker`.

        @param lines The file's lines.
        @param marker The marker to find.
        @return Its line index, or ``None``.
        """
        for index, line in enumerate(lines):
            if marker in line:
                return index
        return None
