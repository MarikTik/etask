from pathlib import Path

from schemav2.codegen.naming import Naming
from schemav2.errors.anchor_not_found_error import AnchorNotFoundError


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
        depth = 0
        for j in range(open_idx, len(line)):
            if line[j] == "(":
                depth += 1
            elif line[j] == ")":
                depth -= 1
                if depth == 0:
                    return f"{line[:open_idx + 1]}{new_params}{line[j:]}"
        raise AnchorNotFoundError(line.strip(), Naming.anchor)
