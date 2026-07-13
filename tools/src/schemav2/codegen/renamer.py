from pathlib import Path
from typing import List, Optional, Tuple
import re

import yaml

from schemav2.tree import _SchemaLoader, Tree
from schemav2.errors.rename_error import RenameError
from schemav2.errors.invalid_identifier_error import InvalidIdentifierError

_ROOT_NAMESPACE = "tasks"


class Renamer:
    """Renames a concrete task across the schema and its generated files.

    The schema key is edited surgically (PyYAML node marks locate the exact
    token, so formatting and comments survive); the ``.hpp``/``.cpp`` pair is
    renamed and its structural tokens (class, guards, include, uid symbol) are
    rewritten, leaving user bodies untouched.
    """

    @staticmethod
    def rename(schema_path: Path, out_dir: Path, task_path: str, new_name: str) -> Tuple[str, str]:
        parts = task_path.split(".")
        old_name = parts[-1]
        Renamer.__validate_new_name(new_name, task_path)

        text = schema_path.read_text()
        key_node = Renamer.__locate_key(text, parts, schema_path)
        Renamer.__reject_sibling_collision(schema_path, parts, new_name)

        schema_path.write_text(Renamer.__rename_key(text, key_node, old_name, new_name))
        Renamer.__rename_files(out_dir, parts, old_name, new_name)
        return old_name, new_name

    # -------------------------------------------------------------- validation

    @staticmethod
    def __validate_new_name(new_name: str, task_path: str) -> None:
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", new_name):
            raise InvalidIdentifierError(new_name, task_path, "must be a valid C++ identifier")

    @staticmethod
    def __reject_sibling_collision(schema_path: Path, parts: List[str], new_name: str) -> None:
        # Re-parse the (still-original) schema and check the target's siblings.
        root = Tree.build(schema_path)
        node = root
        for part in parts[:-1]:
            node = node.children[part]
        if new_name in node.children:
            raise RenameError(f"'{new_name}' already exists next to '{'.'.join(parts)}'")

    # ------------------------------------------------------ schema key editing

    @staticmethod
    def __locate_key(text: str, parts: List[str], schema_path: Path):
        root = yaml.compose(text, Loader=_SchemaLoader)
        node = root
        key_node = None
        for i, part in enumerate(parts):
            mapping = node if i == 0 else Renamer.__child_of(node, "children")
            if mapping is None:
                raise RenameError(f"task path '{'.'.join(parts)}' not found in {schema_path}")
            found = Renamer.__entry(mapping, part)
            if found is None:
                raise RenameError(f"task path '{'.'.join(parts)}' not found in {schema_path}")
            key_node, node = found
            if Renamer.__type_of(node) == "abstract_scope" and i < len(parts) - 1:
                raise RenameError(
                    "renaming through an abstract scope is not supported yet "
                    "(rides with abstract-scope codegen)"
                )
        return key_node

    @staticmethod
    def __entry(mapping, key: str):
        if not isinstance(mapping, yaml.MappingNode):
            return None
        for key_node, value_node in mapping.value:
            if key_node.value == key:
                return key_node, value_node
        return None

    @staticmethod
    def __child_of(node, key: str):
        entry = Renamer.__entry(node, key)
        return entry[1] if entry else None

    @staticmethod
    def __type_of(node) -> Optional[str]:
        entry = Renamer.__entry(node, "type")
        return entry[1].value if entry else None

    @staticmethod
    def __rename_key(text: str, key_node, old_name: str, new_name: str) -> str:
        lines = text.splitlines(keepends=True)
        line_idx = key_node.start_mark.line
        col = key_node.start_mark.column
        line = lines[line_idx]
        if line[col:col + len(old_name)] != old_name:
            raise RenameError("schema key location mismatch; refusing to edit")
        lines[line_idx] = line[:col] + new_name + line[col + len(old_name):]
        return "".join(lines)

    # -------------------------------------------------------- file renaming

    @staticmethod
    def __rename_files(out_dir: Path, parts: List[str], old_name: str, new_name: str) -> None:
        scope_parts = parts[:-1]
        task_dir = out_dir.joinpath(*scope_parts) if scope_parts else out_dir
        for ext in ("hpp", "cpp"):
            old_path = task_dir / f"{old_name}.{ext}"
            if not old_path.exists():
                continue
            content = old_path.read_text()
            content = Renamer.__rewrite_content(content, scope_parts, old_name, new_name, ext)
            old_path.write_text(content)
            old_path.rename(task_dir / f"{new_name}.{ext}")

    @staticmethod
    def __rewrite_content(
        content: str, scope_parts: List[str], old: str, new: str, ext: str
    ) -> str:
        old_guard = Renamer.__guard(scope_parts, old, ext)
        new_guard = Renamer.__guard(scope_parts, new, ext)
        old_sym = "_".join([*scope_parts, old])
        new_sym = "_".join([*scope_parts, new])

        content = content.replace(old_guard, new_guard)
        content = content.replace(f"@file {old}.{ext}", f"@file {new}.{ext}")
        content = content.replace(f"task_id::{old_sym}", f"task_id::{new_sym}")
        if ext == "hpp":
            content = content.replace(f"class {old} :", f"class {new} :")
            content = re.sub(rf"\b{re.escape(old)}\s*\(", f"{new}(", content, count=1)
        else:
            content = content.replace(f'#include "{old}.hpp"', f'#include "{new}.hpp"')
            content = content.replace(f"{old}::", f"{new}::")
            content = content.replace(f"{new}::{old}(", f"{new}::{new}(")
        return content

    @staticmethod
    def __guard(scope_parts: List[str], leaf: str, ext: str) -> str:
        return "_".join([_ROOT_NAMESPACE, *scope_parts, leaf, ext]).upper() + "_"
