"""PlatformIO integration for etask: freshness checking and a regeneration target.

Add to ``platformio.ini``:

    [env:esp32dev]
    platform = espressif32
    framework = arduino
    lib_deps = MarikTik/etask
    extra_scripts = pre:$PROJECT_LIBDEPS_DIR/$PIOENV/etask/scripts/platformio/etask_build.py

    ; where the schema lives, relative to the project root (default: schema.yaml)
    custom_etask_schema = schema.yaml
    ; where task scaffolds go (default: src/sys)
    custom_etask_src = src/sys
    ; where always-regenerated output goes (default: src/generated)
    custom_etask_generated = src/generated
    ; optional: Python client bindings for a PC/Pi peer. Omitted = not generated.
    custom_etask_python = python/tasks.py

## What it does on a build

Nothing, if the generated code is current - it checks and gets out of the way.

If the schema is newer than what was generated from it, the build **fails** with
the command to run. It does not regenerate: a build that rewrites your source
tree as a side effect can clobber a half-finished edit, and there is no way to
ask - a build has no terminal to prompt from under CI, an IDE, or a background
run.

## Regenerating

    pio run -t etask-generate

Only generated sections are rewritten. Task bodies, contexts, and config are
created once and then yours; the generator will not touch them, and reports what
it cannot fix itself rather than guessing.
"""

import os
import subprocess
import sys
from pathlib import Path

from SCons.Script import COMMAND_LINE_TARGETS  # type: ignore

Import("env")  # noqa: F821 - injected by SCons/PlatformIO


#: platformio.ini key -> (attribute, default). All paths are project-relative.
_OPTIONS = (
    ("custom_etask_schema", "schema", "schema.yaml"),
    ("custom_etask_src", "src", "src/sys"),
    ("custom_etask_generated", "generated", "src/generated"),
    ("custom_etask_python", "python", None),
)

#: The target that rewrites generated code, and the command naming it.
_REGEN_TARGET = "etask-generate"
_REGEN_HINT = f"pio run -t {_REGEN_TARGET}"


class EtaskConfig:
    """Where this project's schema and generated code live."""

    def __init__(self, environment):
        self._env = environment
        self.project_dir = Path(environment.subst("$PROJECT_DIR"))
        for key, attr, default in _OPTIONS:
            raw = environment.GetProjectOption(key, default)
            setattr(self, attr, self.project_dir / raw if raw else None)

    @property
    def generated_outputs(self):
        """The always-regenerated files, in CLI argument form.

        These are the ones a staleness check looks at. Scaffolds are excluded on
        purpose: they are generate-once and user-owned, so being older than the
        schema is their normal state.
        """
        args = [
            "--task-id", str(self.generated / "task_id.hpp"),
            "--task-list", str(self.generated / "task_list.hpp"),
            "--links", str(self.generated / "links.hpp"),
            "--scopes", str(self.generated / "scopes.hpp"),
        ]
        if self.python is not None:
            args += ["--python", str(self.python)]
        return args

    @property
    def cli_args(self):
        """The arguments shared by ``generate`` and ``check``."""
        return [str(self.schema), "--out", str(self.src)] + self.generated_outputs


class Generator:
    """Locates and runs the etask code generator.

    The generator ships *inside* the etask library, so a PlatformIO project that
    declares ``lib_deps = MarikTik/etask`` already has it - no pip, no venv, no
    second version to keep in step with the headers. An installed ``etask``
    package is accepted as a fallback for a developer working from a checkout.
    """

    def __init__(self, config: EtaskConfig, script_path: Path):
        self._config = config
        self._package_root = Generator.__find_package_root(script_path)

    @staticmethod
    def __find_package_root(script_path: Path):
        """The directory to put on PYTHONPATH so ``import etask.schema`` works.

        Looked for beside this script first - that is the copy that shipped with
        these headers, and using it is what makes generator and runtime
        impossible to skew. Falls back to whatever is already importable.

        @param script_path This file's location. Passed in rather than read from
               ``__file__``, which does not exist here: PlatformIO runs an
               ``extra_scripts`` hook through ``SConscript``, which ``exec``s the
               source without setting it.
        """
        # scripts/platformio/etask_build.py -> the library root -> etask-python/
        library_root = script_path.resolve().parents[2]
        vendored = library_root / "etask-python"
        if (vendored / "etask" / "schema" / "cli.py").exists():
            return vendored
        return None

    def __environment(self):
        """A subprocess environment that can import the generator."""
        merged = dict(os.environ)
        if self._package_root is not None:
            existing = merged.get("PYTHONPATH", "")
            merged["PYTHONPATH"] = (
                f"{self._package_root}{os.pathsep}{existing}" if existing else str(self._package_root)
            )
        return merged

    def run(self, command, extra=()):
        """Runs one generator subcommand.

        @param command The subcommand (``generate`` or ``check``).
        @param extra   Arguments appended after the shared ones.

        @return The generator's exit status.
        """
        argv = [
            sys.executable, "-m", "etask.schema.cli", command,
            *self._config.cli_args, *extra,
        ]
        try:
            completed = subprocess.run(argv, env=self.__environment(), cwd=str(self._config.project_dir))
        except FileNotFoundError:
            print(
                "etask: could not run the code generator - no usable Python interpreter.\n"
                f"       tried: {sys.executable}",
                file=sys.stderr,
            )
            return 1
        return completed.returncode

    @property
    def available(self):
        """Whether the generator can be imported at all."""
        return self._package_root is not None or Generator.__importable()

    @staticmethod
    def __importable():
        try:
            __import__("etask.schema.cli")
            return True
        except ImportError:
            return False

    def missing_dependency(self):
        """The generator's one dependency, if this interpreter lacks it.

        The generator itself ships with the library, but it parses YAML, and the
        interpreter running a PlatformIO build is PlatformIO's own - which has no
        reason to carry PyYAML. That is an ordinary first-run condition, not a
        fault, so it gets an instruction rather than a traceback.

        @return The pip requirement to install, or ``None`` if satisfied.
        """
        probe = subprocess.run(
            [sys.executable, "-c", "import yaml"],
            env=self.__environment(),
            capture_output=True,
        )
        return "pyyaml" if probe.returncode != 0 else None


def _regenerate(target, source, env):  # noqa: ARG001 - SCons action signature
    """The ``etask-generate`` target: rewrite the generated sections."""
    config = EtaskConfig(env)
    status = Generator(config, _this_script()).run("generate")
    if status != 0:
        print("etask: generation failed; nothing was written.", file=sys.stderr)
    return status


def _check_freshness(config: EtaskConfig, generator: Generator) -> None:
    """Stops the build unless the generated code matches the schema."""
    if not config.schema.exists():
        print(
            f"etask: no schema at {config.schema}.\n"
            "       Set custom_etask_schema in platformio.ini, or create one - see\n"
            "       the etask template project for a starting point.",
            file=sys.stderr,
        )
        env.Exit(1)  # noqa: F821

    if generator.run("check", extra=["--hint", _REGEN_HINT]) != 0:
        env.Exit(1)  # noqa: F821


def _this_script() -> Path:
    """Where this file lives on disk.

    ``__file__`` is unset here - PlatformIO runs an ``extra_scripts`` hook through
    SCons's ``SConscript``, which ``exec``s the source. SCons tracks the script
    it is executing, so ask it; the ``extra_scripts`` entry in platformio.ini is
    the last resort, since that is literally the path the user wrote.
    """
    try:
        from SCons.Script import SConscript_current_file  # type: ignore
        return Path(str(SConscript_current_file()))
    except Exception:
        pass
    # SCons exposes the executing SConscript through the call stack it keeps.
    try:
        import SCons.Script.SConscript as sconscript  # type: ignore
        stack = sconscript.call_stack
        if stack and getattr(stack[-1], "sconscript", None):
            return Path(str(stack[-1].sconscript))
    except Exception:
        pass
    # Whatever platformio.ini named, with the `pre:` marker stripped.
    for entry in env.GetProjectOption("extra_scripts", []):  # noqa: F821
        candidate = entry.split(":", 1)[-1] if entry.startswith(("pre:", "post:")) else entry
        resolved = Path(env.subst(candidate))  # noqa: F821
        if resolved.name == "etask_build.py":
            return resolved
    raise RuntimeError("etask: cannot locate etask_build.py to find its bundled generator")


def _main() -> None:
    config = EtaskConfig(env)  # noqa: F821
    generator = Generator(config, _this_script())

    # The regeneration target exists whether or not the check passes - it is the
    # thing a failing check tells the user to run.
    env.AddCustomTarget(  # noqa: F821
        name=_REGEN_TARGET,
        dependencies=None,
        actions=[_regenerate],
        title="etask: regenerate",
        description="Rewrite the generated code sections from schema.yaml "
                    "(task bodies and contexts are never touched)",
        always_build=True,
    )

    if not generator.available:
        print(
            "etask: the code generator is not importable.\n"
            "       It normally ships inside the etask library, so this means the\n"
            "       library was installed without its etask-python/ directory.\n"
            "       Install the generator directly as a workaround:\n"
            "         pip install etask[codegen]",
            file=sys.stderr,
        )
        env.Exit(1)  # noqa: F821

    dependency = generator.missing_dependency()
    if dependency is not None:
        print(
            f"etask: the code generator needs {dependency}, and the Python running\n"
            f"       this build does not have it.\n"
            f"\n"
            f"         {sys.executable} -m pip install {dependency}\n"
            f"\n"
            f"       That is the only dependency it has - the generator itself ships\n"
            f"       inside the etask library, so it never falls out of step with the\n"
            f"       headers you are compiling against.",
            file=sys.stderr,
        )
        env.Exit(1)  # noqa: F821

    # Generated sources live under src/, so PlatformIO compiles them with no
    # extra configuration; the project root is added so `#include "config/..."`
    # and `#include "generated/..."` resolve from any depth, matching the CMake
    # side's single-include-root rule.
    env.Append(CPPPATH=[str(config.project_dir / "src")])  # noqa: F821

    # Not when regeneration is the thing being asked for: the check's own advice
    # is to run `etask-generate`, so failing that target on a failed check would
    # make the fix unreachable.
    if _REGEN_TARGET not in COMMAND_LINE_TARGETS:
        _check_freshness(config, generator)


_main()
