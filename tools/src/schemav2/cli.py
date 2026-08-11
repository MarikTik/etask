import argparse
import sys
from pathlib import Path

from schemav2.tree import Tree
from schemav2.uid_ledger import UidLedger
from schemav2.codegen.emitter import Emitter
from schemav2.codegen.renamer import Renamer
from schemav2.codegen.scaffold import Scaffold


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
        parser = argparse.ArgumentParser(prog="etask-gen", description="etask schema -> C++ codegen")
        sub = parser.add_subparsers(dest="command")

        gen = sub.add_parser("generate", help="emit/update the task-file tree from a schema")
        gen.add_argument("schema", type=Path, help="path to schema.yaml or schema.json")
        gen.add_argument("--out", type=Path, required=True, help="output tasks/ directory")
        gen.add_argument("--task-id", type=Path, default=None, dest="task_id",
                         help="path to (re)write the generated global::task_id enum, "
                              "e.g. generated/task_id.hpp (always overwritten)")
        gen.add_argument("--task-list", type=Path, default=None, dest="task_list",
                         help="path to (re)write the generated generated::task_list typelist, "
                              "e.g. generated/task_list.hpp (always overwritten)")
        gen.add_argument("--uid-ledger", type=Path, default=None, dest="uid_ledger",
                         help="path of the uid ledger, the committed record that keeps every "
                              "task's wire uid stable across regenerations "
                              "(default: .<schema>.uids.json next to the schema)")
        gen.add_argument("--no-uid-ledger", action="store_true", dest="no_uid_ledger",
                         help="derive uids from the schema alone, ignoring and not writing the "
                              "ledger. Uids may then change when tasks are added or removed - "
                              "for throwaway inspection, not for a deployed protocol")
        gen.set_defaults(handler=Cli.__generate)

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
    def __generate(args) -> int:
        ledger_path = None if args.no_uid_ledger else Cli.__ledger_path(args)
        ledger = UidLedger.load(ledger_path) if ledger_path else None

        root = Tree.build(args.schema, ledger)
        # Emission is prepare-then-commit, so a failure here leaves the tree
        # untouched - and the ledger unwritten, matching it.
        report = Emitter.generate(root, args.out, args.task_id, args.task_list)
        if ledger is not None:
            ledger.save(ledger_path)

        print(f"created {len(report.created)}, updated {len(report.updated)}, "
              f"unchanged {len(report.unchanged)}")
        for path in report.created:
            print(f"  + {path}")
        for path in report.updated:
            print(f"  ~ {path}")
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
