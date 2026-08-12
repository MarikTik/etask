import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from etask.schema.models.node import Node
from etask.schema.codegen.naming import Naming
from etask.schema.codegen.task_file import TaskFile
from etask.schema.codegen.task_id_file import TaskIdFile
from etask.schema.codegen.task_list_file import TaskListFile
from etask.schema.codegen.python_file import PythonFile
from etask.schema.codegen.context_file import ContextFile
from etask.schema.codegen.task_base_file import TaskBaseFile
from etask.schema.codegen.doc_region import DocRegion
from etask.schema.codegen.signature_updater import SignatureUpdater


@dataclass
class EmitReport:
    """What the emitter did, for CLI reporting and tests."""

    created: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)
    #: Things the emitter cannot fix by itself and will not silently ignore.
    notes: List[str] = field(default_factory=list)


@dataclass
class _Write:
    """One file the emitter intends to write, with its full final content."""

    path: Path
    text: str
    existed: bool


class Emitter:
    """Materializes a task tree into a directory of ``.hpp``/``.cpp`` files.

    Scopes (and expanded abstract-scope instances) become directories. A task
    file that does not exist is created in full; one that already exists is
    *updated* — only its constructor signature is rewritten, never its bodies.

    ``task_id.hpp`` (the ``global::task_id`` enum) and ``task_list.hpp`` (the
    ``generated::task_list`` typelist) are different in kind: they are pure
    projections of the schema and are *always* (re)written when their path is
    given — they carry no user code to preserve.

    ## Prepare, then commit

    A run happens in two phases. The **plan** phase reads the tree and every
    existing file and computes each file's full final content in memory; the
    **commit** phase then writes. Nothing touches the output directory until
    every file has been rendered and reconciled successfully, so a failure that
    only shows up part-way through a tree — a mangled ``//! etask:sig`` anchor
    raising ``AnchorNotFoundError`` in the twentieth task, say — aborts the run
    with the project exactly as it was, instead of leaving it half-regenerated
    (a task's ``.hpp`` rewritten but its ``.cpp`` not).

    Each individual file is committed via a temp file plus an atomic rename, so
    no file is ever observed half-written. (A commit interrupted by an I/O error
    or a kill *can* still leave earlier files written and later ones not: the
    guarantee is against *emitter* errors, which is what the whole plan phase is
    validated for, not against media failure mid-write.)
    """

    @staticmethod
    def generate(
        root: Node,
        out_dir: Path,
        task_id_path: Optional[Path] = None,
        task_list_path: Optional[Path] = None,
        python_path: Optional[Path] = None,
    ) -> EmitReport:
        report = EmitReport()
        writes = Emitter.__plan(
            root, out_dir, task_id_path, task_list_path, python_path, report
        )
        Emitter.__commit(writes, report)
        return report

    # ----------------------------------------------------------------- planning

    @staticmethod
    def __plan(
        root: Node,
        out_dir: Path,
        task_id_path: Optional[Path],
        task_list_path: Optional[Path],
        python_path: Optional[Path],
        report: EmitReport,
    ) -> List[_Write]:
        """Render everything in memory. Raises before any file is touched."""
        writes: List[_Write] = []
        Emitter.__plan_task_base(out_dir, writes, report)     # task.hpp - the base alias
        Emitter.__plan_context(root, out_dir, writes, report) # the system (root) context
        Emitter.__walk(root, out_dir, writes, report)
        if task_id_path is not None:
            Emitter.__plan_generated(task_id_path, TaskIdFile.render(root), writes, report)
        if task_list_path is not None:
            fresh = TaskListFile.render(Emitter.__task_list_entries(root, out_dir, task_list_path))
            Emitter.__plan_generated(task_list_path, fresh, writes, report)
        if python_path is not None:
            # The Python client is the same projection of the schema the C++ side
            # is, aimed at the other end of the wire - so it is always rewritten
            # too, and carries no user code.
            fresh = PythonFile.render(root, root.uid_bytes or 1, python_path.stem)
            Emitter.__plan_generated(python_path, fresh, writes, report)
        return writes

    @staticmethod
    def __commit(writes: List[_Write], report: EmitReport) -> None:
        """Write the planned files; only reached once the whole plan succeeded."""
        for write in writes:
            write.path.parent.mkdir(parents=True, exist_ok=True)
            Emitter.__write_atomic(write.path, write.text)
            (report.updated if write.existed else report.created).append(str(write.path))

    @staticmethod
    def __write_atomic(path: Path, text: str) -> None:
        """Write via a sibling temp file + rename, so readers never see a partial file."""
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as handle:
                handle.write(text)
            os.replace(tmp, path)
        except BaseException:
            # Best effort: never leave the stray temp file behind.
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    @staticmethod
    def __plan_generated(path: Path, fresh: str, writes: List[_Write], report: EmitReport) -> None:
        """Plan an always-generated file; record it as unchanged if identical."""
        existed = path.exists()
        if existed and path.read_text() == fresh:
            report.unchanged.append(str(path))
            return
        writes.append(_Write(path, fresh, existed))

    @staticmethod
    def __task_list_entries(root: Node, out_dir: Path, list_path: Path) -> List[Tuple[str, str]]:
        """One (include, type_expr) pair per task, includes relative to list_path.

        ``type_expr`` is the bare qualified type, or - when the task declares a
        ``concurrency`` greater than 1 - the type wrapped in a ``capacity<T, N>``
        tag so the manager reserves N concurrent slots for that uid.
        """
        list_dir = list_path.parent
        entries: List[Tuple[str, str]] = []
        for task in Emitter.__collect_tasks(root):
            hpp = out_dir / Naming.relative_dir(task) / f"{Naming.class_name(task)}.hpp"
            include = os.path.relpath(hpp, list_dir).replace(os.sep, "/")
            qualified = f"{Naming.namespace(task)}::{Naming.class_name(task)}"
            if task.concurrency and task.concurrency > 1:
                type_expr = f"etools::factories::utils::capacity<{qualified}, {task.concurrency}>"
            else:
                type_expr = qualified
            entries.append((include, type_expr))
        return entries

    @staticmethod
    def __collect_tasks(node: Node) -> List[Node]:
        tasks = [node] if node.is_task else []
        for child in node.children.values():
            tasks.extend(Emitter.__collect_tasks(child))
        return tasks

    @staticmethod
    def __walk(node: Node, out_dir: Path, writes: List[_Write], report: EmitReport) -> None:
        for child in node.children.values():
            if child.is_task:
                Emitter.__plan_task(child, out_dir, writes, report)
            else:
                # The scope's directory is created when its context is committed.
                Emitter.__plan_context(child, out_dir, writes, report)  # every scope gets a context
                Emitter.__walk(child, out_dir, writes, report)

    @staticmethod
    def __plan_task_base(out_dir: Path, writes: List[_Write], report: EmitReport) -> None:
        """Plan ``task.hpp`` at the tree root once; never overwrite a user's edits."""
        path = out_dir / Naming.task_base_include()
        if path.exists():
            report.unchanged.append(str(path))
            return
        writes.append(_Write(path, TaskBaseFile.render(), existed=False))

    @staticmethod
    def __plan_context(scope: Node, out_dir: Path, writes: List[_Write], report: EmitReport) -> None:
        """Plan a scope's context. Its own state is user-owned; the child
        contexts it composes are reconciled to the schema (see ContextFile)."""
        path = out_dir / Naming.scope_dir(scope) / Naming.context_include()
        if path.exists():
            original = path.read_text()
            updated = ContextFile.reconcile(original, scope)
            if updated == original:
                report.unchanged.append(str(path))
            else:
                writes.append(_Write(path, updated, existed=True))
            return
        writes.append(_Write(path, ContextFile.render(scope), existed=False))

    @staticmethod
    def __plan_task(task: Node, out_dir: Path, writes: List[_Write], report: EmitReport) -> None:
        task_dir = out_dir / Naming.relative_dir(task)
        cls = Naming.class_name(task)
        hpp = task_dir / f"{cls}.hpp"

        Emitter.__note_missing_on_complete(task, hpp, report)
        Emitter.__plan_one(hpp, TaskFile.render_hpp(task),
                           TaskFile.hpp_params(task), writes, report)
        Emitter.__plan_one(task_dir / f"{cls}.cpp", TaskFile.render_cpp(task),
                           TaskFile.cpp_params(task), writes, report)

    @staticmethod
    def __note_missing_on_complete(task: Node, hpp: Path, report: EmitReport) -> None:
        """Reports a task that gained ``returns:`` after its files were generated.

        Only the constructor signature is reconciled in an existing task file -
        everything else, ``on_complete`` included, is the user's. So adding
        ``returns:`` to a task that already exists produces no C++ at all, and
        the task keeps replying with the base class's empty result. That is a
        silent mismatch between schema and firmware, which is exactly the kind of
        thing this generator exists to prevent, so it is called out instead.
        """
        if not task.returns or not hpp.exists():
            return
        # The declaration, not the word: every generated class doc *mentions*
        # on_complete() in its lifecycle paragraph.
        if "on_complete(etask::core::completion_reason" in hpp.read_text():
            return
        path = ".".join(Naming.path_parts(task))
        report.notes.append(
            f"{path} declares returns but {hpp} has no on_complete override, so the "
            f"task still replies with an empty result. Add it (the generator will not "
            f"touch an existing file's body):\n"
            f"        etask::core::outcome on_complete("
            f"etask::core::completion_reason reason) override;\n"
            f"      ...or delete {hpp.name}/{hpp.stem}.cpp to have them regenerated in full."
        )

    @staticmethod
    def __plan_one(
        path: Path, fresh: str, params: str, writes: List[_Write], report: EmitReport
    ) -> None:
        """Plan the file's creation, or its in-place update: the signature is
        reconciled to the schema, and each schema-derived doc block is re-synced
        unless the user has edited it (see DocRegion). Bodies stay untouched."""
        rel = str(path)
        if not path.exists():
            writes.append(_Write(path, fresh, existed=False))
            return
        original = path.read_text()
        text = original
        for name in DocRegion.names(fresh):
            text = DocRegion.reconcile(text, name, DocRegion.extract(fresh, name))
        text = SignatureUpdater.update_text(text, params, rel)
        if text != original:
            writes.append(_Write(path, text, existed=True))
        else:
            report.unchanged.append(rel)
