import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from schemav2.models.node import Node
from schemav2.codegen.naming import Naming
from schemav2.codegen.task_file import TaskFile
from schemav2.codegen.task_id_file import TaskIdFile
from schemav2.codegen.task_list_file import TaskListFile
from schemav2.codegen.context_file import ContextFile
from schemav2.codegen.signature_updater import SignatureUpdater


@dataclass
class EmitReport:
    """What the emitter did, for CLI reporting and tests."""

    created: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)


class Emitter:
    """Materializes a task tree into a directory of ``.hpp``/``.cpp`` files.

    Scopes (and expanded abstract-scope instances) become directories. A task
    file that does not exist is created in full; one that already exists is
    *updated* — only its constructor signature is rewritten, never its bodies.

    ``task_id.hpp`` (the ``global::task_id`` enum) and ``task_list.hpp`` (the
    ``generated::task_list`` typelist) are different in kind: they are pure
    projections of the schema and are *always* (re)written when their path is
    given — they carry no user code to preserve.
    """

    @staticmethod
    def generate(
        root: Node,
        out_dir: Path,
        task_id_path: Optional[Path] = None,
        task_list_path: Optional[Path] = None,
    ) -> EmitReport:
        report = EmitReport()
        Emitter.__walk(root, out_dir, report)
        if task_id_path is not None:
            Emitter.__emit_generated(task_id_path, TaskIdFile.render(root), report)
        if task_list_path is not None:
            fresh = TaskListFile.render(Emitter.__task_list_entries(root, out_dir, task_list_path))
            Emitter.__emit_generated(task_list_path, fresh, report)
        return report

    @staticmethod
    def __emit_generated(path: Path, fresh: str, report: EmitReport) -> None:
        """(Re)write an always-generated file; record created/updated/unchanged."""
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        if existed and path.read_text() == fresh:
            report.unchanged.append(str(path))
            return
        path.write_text(fresh)
        (report.updated if existed else report.created).append(str(path))

    @staticmethod
    def __task_list_entries(root: Node, out_dir: Path, list_path: Path) -> List[Tuple[str, str]]:
        """One (include, qualified_type) pair per task, includes relative to list_path."""
        list_dir = list_path.parent
        entries: List[Tuple[str, str]] = []
        for task in Emitter.__collect_tasks(root):
            hpp = out_dir / Naming.relative_dir(task) / f"{Naming.class_name(task)}.hpp"
            include = os.path.relpath(hpp, list_dir).replace(os.sep, "/")
            qualified = f"{Naming.namespace(task)}::{Naming.class_name(task)}"
            entries.append((include, qualified))
        return entries

    @staticmethod
    def __collect_tasks(node: Node) -> List[Node]:
        tasks = [node] if node.is_task else []
        for child in node.children.values():
            tasks.extend(Emitter.__collect_tasks(child))
        return tasks

    @staticmethod
    def __walk(node: Node, out_dir: Path, report: EmitReport) -> None:
        for child in node.children.values():
            if child.is_task:
                Emitter.__emit_task(child, out_dir, report)
            else:
                (out_dir / Naming.scope_dir(child)).mkdir(parents=True, exist_ok=True)
                if Emitter.__owns_tasks(child):
                    Emitter.__emit_context(child, out_dir, report)
                Emitter.__walk(child, out_dir, report)

    @staticmethod
    def __owns_tasks(scope: Node) -> bool:
        return any(child.is_task for child in scope.children.values())

    @staticmethod
    def __emit_context(scope: Node, out_dir: Path, report: EmitReport) -> None:
        path = out_dir / Naming.scope_dir(scope) / Naming.context_include()
        if path.exists():
            report.unchanged.append(str(path))
            return
        path.write_text(ContextFile.render(scope))
        report.created.append(str(path))

    @staticmethod
    def __emit_task(task: Node, out_dir: Path, report: EmitReport) -> None:
        task_dir = out_dir / Naming.relative_dir(task)
        task_dir.mkdir(parents=True, exist_ok=True)
        cls = Naming.class_name(task)

        Emitter.__emit_one(task_dir / f"{cls}.hpp", TaskFile.render_hpp(task),
                           TaskFile.hpp_params(task), report)
        Emitter.__emit_one(task_dir / f"{cls}.cpp", TaskFile.render_cpp(task),
                           TaskFile.cpp_params(task), report)

    @staticmethod
    def __emit_one(path: Path, fresh: str, params: str, report: EmitReport) -> None:
        rel = str(path)
        if not path.exists():
            path.write_text(fresh)
            report.created.append(rel)
            return
        if SignatureUpdater.update_file(path, params):
            report.updated.append(rel)
        else:
            report.unchanged.append(rel)
