import argparse
import sys
from pathlib import Path

from etask.schema.tree import Tree
from etask.schema.freshness import Freshness
from etask.schema.uid_ledger import UidLedger
from etask.schema.codegen.emitter import Emitter
from etask.schema.codegen.renamer import Renamer
from etask.schema.codegen.scaffold import Scaffold


class Cli:
    """The single entry point every integration (CMake, PlatformIO, zipapp) wraps."""

    @staticmethod
    def main(argv=None) -> int:
        parser = Cli.__build_parser()
        args = parser.parse_args(argv)
        if not getattr(args, "handler", None):
            parser.print_help()
            return 2
        return args.handler(args)

    @staticmethod
    def __build_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="etask",
            description="etask schema -> C++ project + Python client bindings",
        )
        sub = parser.add_subparsers(dest="command")

        # `generate` and `check` name the same schema and the same outputs - one
        # emits them, the other asks whether they are current - so the options are
        # declared once and shared. A build system passes the identical arguments
        # to both, which is what keeps the check honest.
        outputs = Cli.__output_options()

        gen = sub.add_parser("generate", parents=[outputs],
                             help="emit/update the task-file tree from a schema")
        gen.add_argument("--uid-ledger", type=Path, default=None, dest="uid_ledger",
                         help="path of the uid ledger, the committed record that keeps every "
                              "task's wire uid stable across regenerations "
                              "(default: .<schema>.uids.json next to the schema)")
        gen.add_argument("--no-uid-ledger", action="store_true", dest="no_uid_ledger",
                         help="derive uids from the schema alone, ignoring and not writing the "
                              "ledger. Uids may then change when tasks are added or removed - "
                              "for throwaway inspection, not for a deployed protocol")
        gen.set_defaults(handler=Cli.__generate)

        chk = sub.add_parser("check", parents=[outputs],
                             help="report whether generated code is current with the schema")
        chk.add_argument("--hint", default="etask generate ...", dest="hint",
                         help="the regeneration command to name in the failure message, "
                              "phrased for the caller's build system (a user pasting the "
                              "wrong one is a bad first experience)")
        chk.set_defaults(handler=Cli.__check)

        scf = sub.add_parser("scaffold", help="lay down the non-generated app layer "
                                              "(app, config, hal, support, main, CMake) into a project")
        scf.add_argument("--out", type=Path, required=True,
                         help="project directory to scaffold into (files that already exist are kept)")
        scf.set_defaults(handler=Cli.__scaffold)

        ren = sub.add_parser("rename", help="rename a concrete task in the schema and its files")
        ren.add_argument("schema", type=Path, help="path to schema.yaml or schema.json")
        ren.add_argument("--out", type=Path, required=True, help="output tasks/ directory")
        ren.add_argument("task", help="dotted schema path of the task, e.g. system.reboot")
        ren.add_argument("new_name", help="new task name")
        ren.add_argument("--uid-ledger", type=Path, default=None, dest="uid_ledger",
                         help="path of the uid ledger to carry the task's uid over to its new "
                              "path (default: .<schema>.uids.json next to the schema)")
        ren.add_argument("--no-uid-ledger", action="store_true", dest="no_uid_ledger",
                         help="do not touch the uid ledger; the renamed task is then treated as "
                              "a new one and gets a new wire uid on the next generate")
        ren.set_defaults(handler=Cli.__rename)

        return parser

    @staticmethod
    def __output_options() -> argparse.ArgumentParser:
        """The schema and the output paths, shared by ``generate`` and ``check``."""
        shared = argparse.ArgumentParser(add_help=False)
        shared.add_argument("schema", type=Path, help="path to schema.yaml or schema.json")
        shared.add_argument("--out", type=Path, required=True, help="output tasks/ directory")
        shared.add_argument("--task-id", type=Path, default=None, dest="task_id",
                            help="path of the generated global::task_id enum, "
                                 "e.g. generated/task_id.hpp (always overwritten)")
        shared.add_argument("--task-list", type=Path, default=None, dest="task_list",
                            help="path of the generated per-tier task typelists, "
                                 "e.g. generated/task_list.hpp (always overwritten)")
        shared.add_argument("--scopes", type=Path, default=None, dest="scopes",
                            help="path of the generated scope accessors, "
                                 "e.g. generated/scopes.hpp (always overwritten). Required "
                                 "for any task that belongs to a scope.")
        shared.add_argument("--python", type=Path, default=None, dest="python",
                            help="path of the generated Python client bindings, "
                                 "e.g. python/tasks.py (always overwritten). Needs the etask "
                                 "Python package (etask-python/) at runtime")
        return shared

    @staticmethod
    def __generated_outputs(args) -> "list[Path]":
        """Every always-regenerated output the caller named.

        Scaffolds are deliberately absent: they are generate-once and user-owned,
        so being older than the schema is their normal, correct state.
        """
        named = (args.task_id, args.task_list, args.scopes, args.python)
        return [path for path in named if path is not None]

    @staticmethod
    def __check(args) -> int:
        """Reports whether generated code is current, without writing anything.

        This is what a build runs. It never regenerates: rewriting a user's tree
        as a side effect of building is how a half-finished edit gets clobbered,
        and a build system cannot prompt (no TTY under CI, an IDE, or a
        background build). So it stops and says what to run.
        """
        state = Freshness.check(args.schema, Cli.__generated_outputs(args))
        if state.is_fresh:
            return 0
        print(state.report(args.hint), file=sys.stderr)
        return 1

    @staticmethod
    def __generate(args) -> int:
        ledger_path = None if args.no_uid_ledger else Cli.__ledger_path(args)
        ledger = UidLedger.load(ledger_path) if ledger_path else None

        root = Tree.build(args.schema, ledger)
        # Emission is prepare-then-commit, so a failure here leaves the tree
        # untouched - and the ledger unwritten, matching it.
        report = Emitter.generate(root, args.out, args.task_id, args.task_list,
                                  args.python, args.scopes)
        if ledger is not None:
            ledger.save(ledger_path)

        print(f"created {len(report.created)}, updated {len(report.updated)}, "
              f"unchanged {len(report.unchanged)}")
        for path in report.created:
            print(f"  + {path}")
        for path in report.updated:
            print(f"  ~ {path}")
        for note in report.notes:
            print(f"  ! {note}", file=sys.stderr)
        if ledger is not None:
            for warning in ledger.warnings:
                print(f"  ! {warning}", file=sys.stderr)
        return 0

    @staticmethod
    def __ledger_path(args) -> Path:
        """Where the uid ledger lives when the caller does not say.

        A dotfile beside the schema: it is generator-maintained bookkeeping, not
        a file to hand-edit, so it stays out of the way of the project root -
        while still being named after its schema, so a repo with several schemas
        gets one ledger each.
        """
        if args.uid_ledger is not None:
            return args.uid_ledger
        return args.schema.with_name(f".{args.schema.stem}.uids.json")

    @staticmethod
    def __scaffold(args) -> int:
        report = Scaffold.write(args.out)
        print(f"created {len(report.created)}, kept {len(report.skipped)}")
        for path in report.created:
            print(f"  + {path}")
        for path in report.skipped:
            print(f"  = {path}  (kept)")
        return 0

    @staticmethod
    def __rename(args) -> int:
        old, new = Renamer.rename(args.schema, args.out, args.task, args.new_name)
        print(f"renamed {args.task}: {old} -> {new}")

        # A rename changes the task's path, which is the ledger's key - so the
        # entry moves with it. Otherwise the task would look brand new on the
        # next generate and be handed a different wire uid.
        if not args.no_uid_ledger:
            ledger_path = Cli.__ledger_path(args)
            ledger = UidLedger.load(ledger_path)
            new_path = ".".join(args.task.split(".")[:-1] + [new])
            if ledger.rekey(args.task, new_path):
                ledger.save(ledger_path)
                print(f"  uid ledger: {args.task} -> {new_path}")
        return 0


def main(argv=None) -> int:
    return Cli.main(argv)


if __name__ == "__main__":
    sys.exit(main())
