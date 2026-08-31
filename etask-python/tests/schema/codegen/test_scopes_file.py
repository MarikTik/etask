# etask-python/tests/schema/codegen/test_scopes_file.py
# SPDX-License-Identifier: MIT
"""The scope accessors, and the context tree they index into."""

import pathlib
import re

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter


def generate(tmp_path: pathlib.Path, schema: str):
    tmp_path.mkdir(parents=True, exist_ok=True)
    sp = tmp_path / "schema.yaml"
    sp.write_text(schema)
    out = tmp_path / "sys"
    scopes = tmp_path / "generated" / "scopes.hpp"
    report = Emitter.generate(Tree.build(sp), out, scopes_path=scopes)
    return scopes.read_text(), out, report


NESTED = (
    "system:\n"
    "  rotors:\n"
    "    type: scope\n"
    "    children:\n"
    "      fl:\n"
    "        type: scope\n"
    "        children:\n"
    "          spin:\n            type: polled_task\n            params: { duty: uint8 }\n"
    "  top:\n    type: polled_task\n"
)


def test_every_scope_gets_an_accessor(tmp_path):
    text, _, _ = generate(tmp_path, NESTED)
    assert "sys::context& system() noexcept" in text
    assert "sys::rotors::context& rotors() noexcept" in text
    assert "sys::rotors::fl::context& rotors_fl() noexcept" in text


def test_accessors_index_into_one_tree_by_member_path(tmp_path):
    """A scope's context is a member of its parent's, so the path is mechanical."""
    text, _, _ = generate(tmp_path, NESTED)
    assert "return detail::tree();" in text            # the top-level scope
    assert "return detail::tree().rotors;" in text
    assert "return detail::tree().rotors.fl;" in text


def test_the_tree_is_a_function_local_static(tmp_path):
    """Not a namespace-scope object: contexts hold hardware, so construction
    must happen on first use, not before main()."""
    text, _, _ = generate(tmp_path, NESTED)
    assert "static sys::context instance;" in text
    assert "inline sys::context& tree() noexcept" in text
    # and it must not be reachable as a plain variable
    assert "inline sys::context tree" not in text
    assert "inline sys::context root" not in text


def test_the_tree_is_hidden_from_the_user(tmp_path):
    """A root you can name is one you can duplicate or partially alias."""
    text, _, _ = generate(tmp_path, NESTED)
    tree_ns = text.split("namespace generated::detail")[1].split("} // namespace generated::detail")[0]
    assert "tree()" in tree_ns
    # the public namespace exposes accessors only - never the tree itself
    public = text.split("namespace generated::scopes")[1]
    assert "static sys::context" not in public


def test_tasks_name_their_scope_by_index(tmp_path):
    """The declaration the manager reads to inject a task's context.

    An index rather than the accessor's address: that value is a template
    argument of the unpacking adapter, so it ends up inside the adapter's
    mangled type name, and a function pointer mangles as the entire function -
    tens of bytes of typeinfo string per task.
    """
    _, out, _ = generate(tmp_path, NESTED)
    spin = (out / "rotors" / "fl" / "spin.hpp").read_text()
    assert re.search(
        r"static constexpr etask::core::scope_index_t scope = \d+;", spin
    ), "a task must name its scope with an index"
    assert "&generated::scopes::" not in spin, "the accessor's address must not be a template argument"
    assert "using params = etools::meta::typelist<std::uint8_t>;" in spin
    assert '#include "../../../generated/scopes.hpp"' in spin


def test_a_tasks_index_resolves_to_its_own_scope(tmp_path):
    """The index and the binding must agree, or a task gets another's context.

    This is the one thing the split between the two files can get wrong, and it
    would get it wrong silently: every index resolves to *some* scope, so a
    mismatch compiles and hands the task a context of the wrong type only if the
    types happen to differ. Two scopes with identically-shaped contexts would
    not even fail to build.
    """
    text, out, _ = generate(tmp_path, NESTED)

    spin = (out / "rotors" / "fl" / "spin.hpp").read_text()
    index = int(re.search(
        r"static constexpr etask::core::scope_index_t scope = (\d+);", spin).group(1))

    binding = re.search(
        rf"template<> struct scope_binding<{index}> \{{.*?\}};", text, re.S)
    assert binding, f"no scope_binding<{index}> for the index the task names"
    assert "generated::scopes::rotors_fl()" in binding.group(0)


def test_every_scope_gets_a_binding(tmp_path):
    """A task whose index has no binding fails to compile, so none may be missed."""
    text, _, _ = generate(tmp_path, NESTED)
    # Only the public accessors: `detail::tree()` is the tree itself, not a
    # scope, and deliberately has no binding.
    public = text.split("namespace generated::scopes {")[1].split("} // namespace")[0]
    accessors = set(re.findall(r"inline [\w:]+& (\w+)\(\) noexcept", public))
    bound = set(re.findall(r"return generated::scopes::(\w+)\(\);", text))
    assert accessors, "no accessors found - the regex has drifted from the emitter"
    assert accessors == bound, f"unbound scopes: {accessors - bound}"


def test_binding_indices_are_dense_and_start_at_zero(tmp_path):
    """Positions in one list, so a gap would mean the two emitters disagree."""
    text, _, _ = generate(tmp_path, NESTED)
    indices = sorted(int(n) for n in re.findall(r"struct scope_binding<(\d+)>", text))
    assert indices == list(range(len(indices)))


def test_a_task_with_no_params_declares_an_empty_list(tmp_path):
    """`params` is always present - an empty pack is a real answer, not a gap."""
    _, out, _ = generate(tmp_path, "system:\n  stop:\n    type: instant_task\n")
    assert "using params = etools::meta::typelist<>;" in (out / "stop.hpp").read_text()


def test_scopes_file_is_always_regenerated(tmp_path):
    text, out, _ = generate(tmp_path, NESTED)
    scopes = tmp_path / "generated" / "scopes.hpp"
    scopes.write_text("// hand edit\n")
    sp = tmp_path / "schema.yaml"
    report = Emitter.generate(Tree.build(sp), out, scopes_path=scopes)
    assert "// hand edit" not in scopes.read_text()
    assert str(scopes) in report.updated
