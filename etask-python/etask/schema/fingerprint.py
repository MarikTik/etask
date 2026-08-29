from hashlib import sha256
from typing import List

from etask.schema.models.node import Node


#: Prefixes the canonical string so the algorithm itself can be revised without
#: a new version silently colliding with an old peer's hash. Bump this if the
#: canonical form below ever changes shape.
_ALGORITHM = "etask-fingerprint-v1"

#: Bytes of the digest actually carried on the wire. Eight gives collision odds
#: around one in 1.8e19 - far beyond what is needed to catch a version skew -
#: while staying small enough to sit in a handshake preamble.
_WIDTH = 8


class Fingerprint:
    """The wire contract of a schema, reduced to eight bytes.

    Two peers built from the same schema agree on every uid, every argument
    list, every result shape, and every link's frame layout. Two peers built
    from *different* schemas may agree on all of the layout and none of the
    meaning - the frames parse, the checksum passes, and the device runs the
    wrong task with plausible-looking arguments. That is the failure this
    catches, and it is the one that is hardest to diagnose in the field.

    So the fingerprint covers the **whole** contract, not just its shape: the
    uid width, each link's frame parameters, and every task's uid, path, tier,
    parameters and declared results. Any schema edit that changes what the wire
    means changes the fingerprint, and the two ends stop talking rather than
    misunderstanding each other.

    The hash is taken over a **canonical string** rather than over the schema
    file, because the same contract may be written many ways - reordered
    siblings, different comments, YAML versus JSON - and none of those change
    what goes on the wire. Building the string explicitly also means the two
    language implementations have something exact to agree on: the string is
    the specification, and `canonical` is available so a mismatch can be
    diffed rather than guessed at.
    """

    @staticmethod
    def canonical(root: Node) -> str:
        """Renders the schema's wire contract as one canonical string.

        Every element is emitted in a determined order - links by name, tasks by
        uid - so that reordering the schema cannot change the result. Only what
        reaches the wire is included: names that exist purely for C++ (a scope's
        own name, say) appear solely as part of a task's dotted path, which is
        included because renaming a task is a contract change a peer should
        notice.

        @param root The built schema tree.
        @return The canonical string; hash this, or diff it against a peer's.
        """
        lines: List[str] = [_ALGORITHM, f"uid_bytes={root.uid_bytes or 1}"]

        for link in sorted(root.links, key=lambda l: l.name) if root.links else []:
            lines.append(
                f"link {link.name} {link.topology.value} "
                f"{'sequenced' if link.sequenced else 'no_sequence'} "
                f"{link.checksum.value}"
            )

        for task in sorted(Fingerprint.__tasks(root), key=lambda t: t.uid or 0):
            tier = task.tier.value if task.tier else "unknown"
            lines.append(f"task {task.uid} {Fingerprint.__path(task)} {tier}")

            for param in task.params or []:
                lines.append(f"  param {param.name} {param.type}")

            for shape in task.returns or []:
                for value in shape.values:
                    lines.append(f"  return {shape.name} {value.name} {value.type}")

        return "\n".join(lines) + "\n"

    @staticmethod
    def compute(root: Node) -> int:
        """The eight-byte fingerprint, as an unsigned integer.

        @param root The built schema tree.
        @return The first eight bytes of the canonical string's SHA-256, read
                big-endian - so the integer's hex form matches the leading bytes
                of the digest, and a log line can be compared against a manual
                `sha256sum` by eye.
        """
        digest = sha256(Fingerprint.canonical(root).encode("utf-8")).digest()
        return int.from_bytes(digest[:_WIDTH], "big")

    @staticmethod
    def hex(root: Node) -> str:
        """The fingerprint as a fixed-width hex string, for logs and comments.

        @param root The built schema tree.
        @return Sixteen lowercase hex digits, zero-padded.
        """
        return f"{Fingerprint.compute(root):016x}"

    # ------------------------------------------------------------------ parts

    @staticmethod
    def __tasks(node: Node) -> List[Node]:
        """Every task in the tree, in traversal order (the caller sorts).

        @param node The subtree root.
        @return The task nodes beneath it, including itself if it is one.
        """
        found = [node] if node.is_task else []
        for child in node.children.values():
            found.extend(Fingerprint.__tasks(child))
        return found

    @staticmethod
    def __path(task: Node) -> str:
        """A task's dotted schema path, root-relative.

        @param task The task node.
        @return e.g. ``rotors.fl.set_thrust``; a root-level task is just its name.
        """
        parts: List[str] = []
        node = task
        while node is not None and node.name:
            parts.append(node.name)
            node = node.parent
        return ".".join(reversed(parts))
