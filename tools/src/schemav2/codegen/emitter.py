from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from schemav2.models.node import Node
from schemav2.codegen.naming import Naming
from schemav2.codegen.task_file import TaskFile
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
    """

    @staticmethod
    def generate(root: Node, out_dir: Path) -> EmitReport:
        report = EmitReport()
        Emitter.__walk(root, out_dir, report)
        return report

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
