import argparse
import sys
from pathlib import Path

from schemav2.tree import Tree
from schemav2.codegen.emitter import Emitter
from schemav2.codegen.renamer import Renamer


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
        gen.set_defaults(handler=Cli.__generate)

        ren = sub.add_parser("rename", help="rename a concrete task in the schema and its files")
        ren.add_argument("schema", type=Path, help="path to schema.yaml or schema.json")
        ren.add_argument("--out", type=Path, required=True, help="output tasks/ directory")
        ren.add_argument("task", help="dotted schema path of the task, e.g. system.reboot")
        ren.add_argument("new_name", help="new task name")
        ren.set_defaults(handler=Cli.__rename)

        return parser

    @staticmethod
    def __generate(args) -> int:
        root = Tree.build(args.schema)
        report = Emitter.generate(root, args.out)
        print(f"created {len(report.created)}, updated {len(report.updated)}, "
              f"unchanged {len(report.unchanged)}")
        for path in report.created:
            print(f"  + {path}")
        for path in report.updated:
            print(f"  ~ {path}")
        return 0

    @staticmethod
    def __rename(args) -> int:
        old, new = Renamer.rename(args.schema, args.out, args.task, args.new_name)
        print(f"renamed {args.task}: {old} -> {new}")
        return 0


def main(argv=None) -> int:
    return Cli.main(argv)


if __name__ == "__main__":
    sys.exit(main())
