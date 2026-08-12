# tools/tests/etask.schema/codegen/test_managed_region.py
# SPDX-License-Identifier: MIT

import pytest

from etask.schema.codegen.managed_region import ManagedRegion, ManagedRegionError


def _file(*body_lines):
    """A user file with a managed 'children' region + user content around it."""
    return "\n".join([
        "struct context {",
        "    bool user_state = false;          // USER",
        "    //! etask:managed children - generated",
        *[f"    {ln}" for ln in body_lines],
        "    //! etask:end children",
        "    int more_user = 1;                 // USER",
        "};",
    ])


def _item(code, identity):
    return ManagedRegion.item_line(code, identity).strip()


def test_append_new_item():
    text = _file(_item("a::context a;", "a"))
    out = ManagedRegion.reconcile(text, "children", [("a", "a::context a;"), ("b", "b::context b;")])
    assert "a::context a;  //! etask:item a" in out
    assert "b::context b;  //! etask:item b" in out          # appended
    assert out.count("//! etask:item") == 2


def test_keep_existing_unmodified_is_idempotent():
    desired = [("a", "a::context a;"), ("b", "b::context b;")]
    text = _file(_item("a::context a;", "a"), _item("b::context b;", "b"))
    once = ManagedRegion.reconcile(text, "children", desired)
    twice = ManagedRegion.reconcile(once, "children", desired)
    assert once == text            # nothing to change
    assert twice == once           # idempotent


def test_user_edit_to_an_item_line_is_preserved():
    # user added an initializer to the generated line; identity marker intact
    edited = "    a::context a{ /*hw*/ };  //! etask:item a"
    text = "\n".join([
        "struct context {",
        "    //! etask:managed children - generated",
        edited,
        "    //! etask:end children",
        "};",
    ])
    out = ManagedRegion.reconcile(text, "children", [("a", "a::context a;")])
    assert edited in out           # kept VERBATIM, not replaced with canonical form
    assert "a::context a;  //! etask:item a" not in out


def test_prune_deschematized_item():
    text = _file(_item("a::context a;", "a"), _item("b::context b;", "b"))
    out = ManagedRegion.reconcile(text, "children", [("a", "a::context a;")])   # b removed from schema
    assert "//! etask:item a" in out
    assert "//! etask:item b" not in out


def test_existing_order_preserved_new_appended():
    text = _file(_item("b::context b;", "b"), _item("a::context a;", "a"))
    out = ManagedRegion.reconcile(text, "children",
                                  [("a", "a::context a;"), ("b", "b::context b;"), ("c", "c::context c;")])
    body = [ln for ln in out.splitlines() if "etask:item" in ln]
    assert body[0].endswith("item b")   # original order kept
    assert body[1].endswith("item a")
    assert body[2].endswith("item c")   # new one appended last


def test_user_content_outside_region_untouched():
    text = _file(_item("a::context a;", "a"))
    out = ManagedRegion.reconcile(text, "children", [("a", "a::context a;")])
    assert "bool user_state = false;          // USER" in out
    assert "int more_user = 1;                 // USER" in out


def test_loose_line_inside_region_preserved():
    text = "\n".join([
        "struct context {",
        "    //! etask:managed children - generated",
        "    int hand_added = 7;   // user put this inside",
        "    a::context a;  //! etask:item a",
        "    //! etask:end children",
        "};",
    ])
    out = ManagedRegion.reconcile(text, "children", [("a", "a::context a;")])
    assert "int hand_added = 7;   // user put this inside" in out


def test_missing_region_raises():
    with pytest.raises(ManagedRegionError):
        ManagedRegion.reconcile("struct context {};", "children", [("a", "a::context a;")])


def test_render_block_fresh():
    block = ManagedRegion.render_block("children", "generated",
                                       [("a", "a::context a;"), ("b", "b::context b;")], indent="    ")
    text = "\n".join(block)
    assert "//! etask:managed children - generated" in text
    assert "a::context a;  //! etask:item a" in text
    assert "b::context b;  //! etask:item b" in text
    assert "//! etask:end children" in text
