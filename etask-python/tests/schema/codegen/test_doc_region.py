# tools/tests/etask.schema/codegen/test_doc_region.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

from etask.schema.codegen.doc_region import DocRegion


def _wrap(name, body, indent=""):
    return "\n".join(DocRegion.render(name, body, indent)) + "\n"


def test_render_wraps_body_in_named_markers_with_digest():
    body = ["/**", "* @brief hello", "*/"]
    out = DocRegion.render("file", body)
    assert out[0] == f"//! etask:doc file {DocRegion.digest(body)}"
    assert out[1:-1] == body
    assert out[-1] == "//! etask:end doc file"


def test_names_and_extract_roundtrip():
    text = _wrap("file", ["/**", "* a", "*/"]) + _wrap("class", ["    /**", "    * b", "    */"], "    ")
    assert DocRegion.names(text) == ["file", "class"]
    assert DocRegion.extract(text, "file") == ["/**", "* a", "*/"]
    assert DocRegion.extract(text, "class") == ["    /**", "    * b", "    */"]


def test_reconcile_resyncs_when_untouched():
    text = _wrap("file", ["/**", "* @brief old", "*/"])
    fresh = ["/**", "* @brief new", "*/"]
    out = DocRegion.reconcile(text, "file", fresh)
    assert "* @brief new" in out
    assert "* @brief old" not in out
    # digest was refreshed so a subsequent untouched regen keeps working
    assert DocRegion.extract(out, "file") == fresh
    again = DocRegion.reconcile(out, "file", ["/**", "* @brief newer", "*/"])
    assert "* @brief newer" in again


def test_reconcile_leaves_user_edited_block_alone():
    text = _wrap("file", ["/**", "* @brief old", "*/"])
    edited = text.replace("* @brief old", "* @brief MINE")   # user hand-edit
    out = DocRegion.reconcile(edited, "file", ["/**", "* @brief regenerated", "*/"])
    assert "* @brief MINE" in out            # kept
    assert "* @brief regenerated" not in out  # not clobbered


def test_reconcile_is_noop_without_markers():
    plain = "/**\n* @brief no markers here\n*/\n"
    assert DocRegion.reconcile(plain, "file", ["/**", "* @brief x", "*/"]) == plain


def test_edited_block_stays_frozen_across_further_regens():
    text = _wrap("file", ["/**", "* @brief v1", "*/"])
    edited = text.replace("* @brief v1", "* @brief mine")
    once = DocRegion.reconcile(edited, "file", ["/**", "* @brief v2", "*/"])
    twice = DocRegion.reconcile(once, "file", ["/**", "* @brief v3", "*/"])
    assert "* @brief mine" in twice
    assert "v2" not in twice and "v3" not in twice


def test_independent_blocks_freeze_independently():
    text = _wrap("file", ["/**", "* @brief file old", "*/"]) \
        + _wrap("class", ["/**", "* @brief class old", "*/"])
    # user edits only the class block
    text = text.replace("* @brief class old", "* @brief class MINE")
    text = DocRegion.reconcile(text, "file", ["/**", "* @brief file new", "*/"])
    text = DocRegion.reconcile(text, "class", ["/**", "* @brief class new", "*/"])
    assert "* @brief file new" in text       # untouched file block re-synced
    assert "* @brief class MINE" in text      # edited class block kept
    assert "* @brief class new" not in text
