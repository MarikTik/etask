# etask-python/tests/schema/codegen/test_scopes_file.py
# SPDX-License-Identifier: MIT
"""The scope accessors, and the context tree they index into."""

import pathlib

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
    "rotors:\n"
    "  type: scope\n"
    "  children:\n"
    "    fl:\n"
    "      type: scope\n"
    "      children:\n"
    "        spin:\n          type: polled_task\n          params: { duty: uint8 }\n"
    "top:\n  type: polled_task\n"
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


def test_tasks_name_their_scope_accessor(tmp_path):
    """The declaration the manager reads to inject a task's context."""
    _, out, _ = generate(tmp_path, NESTED)
    spin = (out / "rotors" / "fl" / "spin.hpp").read_text()
    assert "static constexpr auto scope = &generated::scopes::rotors_fl;" in spin
    assert "using params = etools::meta::typelist<std::uint8_t>;" in spin
    assert '#include "../../../generated/scopes.hpp"' in spin


def test_a_task_with_no_params_declares_an_empty_list(tmp_path):
    """`params` is always present - an empty pack is a real answer, not a gap."""
    _, out, _ = generate(tmp_path, "stop:\n  type: instant_task\n")
    assert "using params = etools::meta::typelist<>;" in (out / "stop.hpp").read_text()


def test_scopes_file_is_always_regenerated(tmp_path):
    text, out, _ = generate(tmp_path, NESTED)
    scopes = tmp_path / "generated" / "scopes.hpp"
    scopes.write_text("// hand edit\n")
    sp = tmp_path / "schema.yaml"
    report = Emitter.generate(Tree.build(sp), out, scopes_path=scopes)
    assert "// hand edit" not in scopes.read_text()
    assert str(scopes) in report.updated
