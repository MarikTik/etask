# tools/tests/schemav2/codegen/test_signature_updater.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

import pytest

from schemav2.codegen.signature_updater import SignatureUpdater
from schemav2.errors.anchor_not_found_error import AnchorNotFoundError


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
