from pathlib import Path

from etask.schema.codegen.naming import Naming
from etask.schema.errors.anchor_not_found_error import AnchorNotFoundError


class SignatureUpdater:
    """Rewrites only the constructor parameter list on the anchored line.

    Everything else in the file — docs, members, bodies, the other hooks — is
    left byte-for-byte intact. The anchored line has the shape
    ``<prefix>(<params>)<suffix> //! etask:sig`` and only ``<params>`` changes.
    """

    @staticmethod
    def update_text(text: str, new_params: str, source: str = "<text>") -> str:
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if Naming.anchor in line:
                lines[i] = SignatureUpdater.__rewrite_line(line, new_params)
                return "".join(lines)
        raise AnchorNotFoundError(source, Naming.anchor)

    @staticmethod
    def update_file(path: Path, new_params: str) -> bool:
        original = path.read_text()
        updated = SignatureUpdater.update_text(original, new_params, str(path))
        if updated == original:
            return False
        path.write_text(updated)
        return True

    @staticmethod
    def __rewrite_line(line: str, new_params: str) -> str:
        open_idx = line.find("(")
        if open_idx == -1:
            raise AnchorNotFoundError(line.strip(), Naming.anchor)
        # Parens inside a string or char literal are text, not structure. A
        # default argument like `char sep = ')'` used to close the list early and
        # truncate the declaration - reachable only by hand-editing the anchored
        # line, which is the case the anchor exists to survive.
        depth = 0
        quote = ""          # the literal delimiter currently open, "" outside one
        escaped = False
        for j in range(open_idx, len(line)):
            char = line[j]
            if quote:
                if escaped:
                    escaped = False         # this char is consumed by the escape
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = ""              # literal closed
                continue
            if char in ("'", '"'):
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return f"{line[:open_idx + 1]}{new_params}{line[j:]}"
        raise AnchorNotFoundError(line.strip(), Naming.anchor)
