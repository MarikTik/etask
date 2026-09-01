#!/usr/bin/env python3
"""Writes the identifying body into each scaffolded task in this project.

## Why a script rather than 294 hand-edited files

Every task in `deep_tree` has the *same* one-line body: report the uid it was
compiled with. That is deliberate - the project's subject is whether 294 tasks
the generator produced from a handful of definitions are genuinely distinct, and
the sharpest way to ask is to give them identical source and see whether they
still behave differently. Writing that same line 294 times by hand would add no
information and would guarantee a typo somewhere in the middle.

So the bodies are filled mechanically, once, and then they are ordinary
user-owned source: `etask generate` will not touch them again, and neither will
this script unless it is re-run after a schema change adds tasks.

## What it does and does not touch

Only the *inside* of a function the scaffold left with a `// TODO`. It matches
each body by the function's own opening line, so:

- the `//! etask:sig` constructor signature is never rewritten - the generator
  owns that region, and it is matched, not replaced;
- the `//! etask:doc` blocks are not touched, so they stay in sync with the
  schema until someone edits them deliberately;
- a body that has already been filled no longer carries its `// TODO` and is
  left exactly as it is, so a re-run after adding a task fills only the new one.

A file it cannot fill is reported rather than skipped: a task whose body stayed
empty would pass every assertion in verify.py by never reporting at all.

Usage: `python3 fill_bodies.py [--check]`, from this directory. `--check`
reports what would change and writes nothing.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYS_DIR = HERE / "src" / "sys"

#: The include every filled body needs, and the line it is inserted after.
WITNESS_INCLUDE = '#include "support/witness.hpp"'

#: `on_complete` bodies: report the uid, then return it as the schema's result.
#:
#: Both, not either. The return proves the value can travel the ordinary result
#: path (it is what an external channel would put on the wire); the witness is
#: what the host driver can actually read back, since an internal channel
#: discards results. A task that only returned would be unobservable here, and
#: one that only recorded would not exercise `outcome` at all.
COMPLETE_BODY = """        // Identity, not a measurement: `uid` is this class's own
        // `global::task_id`, fixed at compile time from its schema path. A task
        // running under another's registration would report that other number.
        const auto self = static_cast<std::uint16_t>(uid);
        support::witness::record(self, support::phase::completed);
        return {self};"""

#: An instant command's whole body. It has no `on_complete` and sends no reply,
#: so the witness is its only way to say it ran at all.
INSTANT_BODY = """        // An instant command's constructor *is* the task. There is no result
        // to return and no reply to send, so reporting to the witness is the
        // only evidence this specific uid ran.
        support::witness::record(
            static_cast<std::uint16_t>(uid), support::phase::ran);"""

#: `is_finished` on a polled/stateful task: conclude on the first tick.
#:
#: These tasks are polled tiers only so that the widened uid type is exercised
#: through each manager's registry; none of them models real work, so making
#: them run for more ticks would only slow the driver down.
FINISHED_BODY = """        // Nothing here models real work - the tier is what is being
        // exercised, not the duration - so one tick is the whole task.
        return true;"""


def replace_body(text, opener, body):
    """Replaces the body of the function whose signature line ends with `opener`.

    @param text The file's full contents.
    @param opener The function's opening source line, without indentation.
    @param body The replacement body, already indented.
    @return The new text, or None if that function is absent or already filled.
    """
    pattern = re.compile(
        r"(^[ \t]*" + re.escape(opener) + r"\n[ \t]*\{\n)(.*?)(^[ \t]*\}\n)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        return None
    if "TODO" not in match.group(2) and match.group(2).strip():
        return None  # already filled, or hand-edited: leave it alone
    return text[: match.start()] + match.group(1) + body + "\n" + match.group(3) + text[match.end():]


def add_include(text):
    """Inserts the witness include after the task's own header include.

    @param text The file's full contents.
    @return The new text, unchanged if the include is already present.
    """
    if WITNESS_INCLUDE in text:
        return text
    return re.sub(
        r'(^#include "[a-z_0-9]+\.hpp"\n)',
        r"\1" + WITNESS_INCLUDE + "\n",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def fill(path, check):
    """Fills one task's `.cpp`.

    @param path The task body to fill.
    @param check Report only; write nothing.
    @return "filled", "unchanged", or an error string.
    """
    original = text = path.read_text()
    name = path.stem

    # Which functions exist is decided by the task's tier, so rather than
    # re-deriving the tier here, each candidate is attempted and a miss is fine.
    # What is *not* fine is a file where none of them matched: that is a task
    # whose body would stay empty, and it is reported below.
    touched = False
    for opener, body in (
        (f"etask::core::outcome {name}::on_complete([[maybe_unused]] "
         "etask::core::completion_reason reason)", COMPLETE_BODY),
        (f"bool {name}::is_finished()", FINISHED_BODY),
    ):
        updated = replace_body(text, opener, body)
        if updated is not None:
            text, touched = updated, True

    # An instant command is recognized by having no on_complete: its whole body
    # is the constructor, which the scaffold leaves with its own TODO.
    if "on_complete" not in text:
        for opener in (
            f"{name}::{name}([[maybe_unused]] context& ctx) //! etask:sig",
            f"{name}::{name}() //! etask:sig",
        ):
            updated = replace_body(text, opener, INSTANT_BODY)
            if updated is not None:
                text, touched = updated, True
                break

    if not touched:
        if WITNESS_INCLUDE in original:
            return "unchanged"
        return f"no fillable body found in {path}"

    text = add_include(text)
    if not check and text != original:
        path.write_text(text)
    return "filled" if text != original else "unchanged"


def main():
    """@return Process exit status: non-zero if any task could not be filled."""
    check = "--check" in sys.argv
    filled = unchanged = 0
    errors = []
    for path in sorted(SYS_DIR.rglob("*.cpp")):
        result = fill(path, check)
        if result == "filled":
            filled += 1
        elif result == "unchanged":
            unchanged += 1
        else:
            errors.append(result)

    print(f"filled {filled}, unchanged {unchanged}, errors {len(errors)}")
    for error in errors:
        print(f"  ! {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
