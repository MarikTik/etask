# tools/tests/etask.schema/codegen/test_signature_updater.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import pytest

from etask.schema.codegen.signature_updater import SignatureUpdater
from etask.schema.errors.anchor_not_found_error import AnchorNotFoundError


def test_rewrites_only_param_list():
    text = (
        "class t {\n"
        "public:\n"
        "    t(int a); //! etask:sig\n"
        "    void on_start() override;\n"
        "};\n"
    )
    out = SignatureUpdater.update_text(text, "int a, float b")
    assert "t(int a, float b); //! etask:sig" in out
    # surrounding lines untouched
    assert "void on_start() override;" in out
    assert out.count("//! etask:sig") == 1


def test_preserves_body_below_cpp_signature():
    text = (
        "t::t(int a) //! etask:sig\n"
        "{\n"
        "    keep_me();\n"
        "}\n"
    )
    out = SignatureUpdater.update_text(text, "int a, bool flag")
    assert "t::t(int a, bool flag) //! etask:sig" in out
    assert "keep_me();" in out


def test_empty_param_list():
    text = "t::t(int a) //! etask:sig\n{\n}\n"
    out = SignatureUpdater.update_text(text, "")
    assert "t::t() //! etask:sig" in out


def test_idempotent_update_file(tmp_path):
    p = tmp_path / "t.hpp"
    p.write_text("    t(int a); //! etask:sig\n")
    assert SignatureUpdater.update_file(p, "int a, float b") is True
    # second identical update is a no-op
    assert SignatureUpdater.update_file(p, "int a, float b") is False


def test_missing_anchor_raises():
    with pytest.raises(AnchorNotFoundError):
        SignatureUpdater.update_text("t(int a);\n", "int a")


def test_paren_counting_ignores_parens_inside_literals():
    """A paren inside a string or char literal is not structure.

    The depth counter treated every `(` and `)` as structural, so a default
    argument containing an unbalanced literal paren - `char sep = ')'` - closed
    the parameter list early and the rewrite truncated the declaration.

    Reachable only through a hand-edited anchored line, which is exactly the
    case the anchor exists to survive.
    """
    line = "        probe(int n, char sep = ')'); //! etask:sig\n"
    out = SignatureUpdater.update_text(line, "int n, float gain", "probe.hpp")
    assert out == "        probe(int n, float gain); //! etask:sig\n", out


def test_paren_counting_ignores_an_escaped_quote_in_a_literal():
    """An escaped quote must not be read as the literal's end.

    `'\\''` closes on the *second* quote; treating the escaped one as the
    terminator would put the scanner back into structure mode mid-literal and
    make the following `)` count.
    """
    line = "        probe(char q = '\\'', int n = (1)); //! etask:sig\n"
    out = SignatureUpdater.update_text(line, "int n", "probe.hpp")
    assert out == "        probe(int n); //! etask:sig\n", out
