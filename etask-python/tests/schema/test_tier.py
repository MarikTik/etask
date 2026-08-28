# etask-python/tests/schema/test_tier.py
# SPDX-License-Identifier: MIT
"""The task tier: what a task declares itself to be, and what follows from it."""

import pathlib
import tempfile

import pytest

from etask.schema.tree import Tree
from etask.schema.models.tier import Tier
from etask.schema.errors.schema_shape_error import SchemaShapeError


def build(text: str) -> pathlib.Path:
    path = pathlib.Path(tempfile.mktemp(suffix=".yaml"))
    path.write_text(text)
    return path


# ------------------------------------------------------------------ parsing


@pytest.mark.parametrize("tier", list(Tier))
def test_every_tier_name_parses_onto_the_task(tier):
    root = Tree.build(build(f"system:\n  t:\n    type: {tier.value}\n"))
    assert root.children["t"].tier is tier
    assert root.children["t"].is_task


def test_bare_task_is_rejected_and_names_the_tiers():
    with pytest.raises(SchemaShapeError) as excinfo:
        Tree.build(build("system:\n  t:\n    type: task\n"))
    message = str(excinfo.value)
    # The error has to teach the choice, not just refuse: every tier is named,
    # with the distinction that decides between them.
    for tier in Tier:
        assert tier.value in message
    assert "no reply" in message


def test_unknown_type_still_rejected():
    with pytest.raises(SchemaShapeError):
        Tree.build(build("system:\n  t:\n    type: banana\n"))


def test_tier_survives_abstract_scope_expansion():
    root = Tree.build(build(
        "system:\n"
        "  joint:\n"
        "    type: abstract_scope\n"
        "    instances: [base, elbow]\n"
        "    children:\n"
        "      stop:\n        type: instant_task\n"
        "      move:\n        type: stateful_task\n"
    ))
    for instance in ("base", "elbow"):
        assert root.children[instance].children["stop"].tier is Tier.INSTANT
        assert root.children[instance].children["move"].tier is Tier.STATEFUL


# -------------------------------------------------------- instant restrictions


def test_instant_task_cannot_return():
    """An instant command has no on_complete, so a result shape reaches no one."""
    with pytest.raises(SchemaShapeError) as excinfo:
        Tree.build(build("system:\n  t:\n    type: instant_task\n    returns: { ok: bool }\n"))
    assert "sends no reply" in str(excinfo.value)
    assert "oneshot_task" in str(excinfo.value)   # points at the tier that can


def test_instant_task_cannot_declare_concurrency():
    """It occupies no storage, so there are never two instances to bound."""
    with pytest.raises(SchemaShapeError) as excinfo:
        Tree.build(build("system:\n  t:\n    type: instant_task\n    concurrency: 3\n"))
    assert "occupies no storage" in str(excinfo.value)


def test_instant_task_may_still_take_params():
    """Params are constructor arguments - the one thing an instant task does use."""
    root = Tree.build(build("system:\n  t:\n    type: instant_task\n    params: { level: uint8 }\n"))
    assert [p.name for p in root.children["t"].params] == ["level"]


@pytest.mark.parametrize("tier", [Tier.ONESHOT, Tier.POLLED, Tier.STATEFUL])
def test_managed_tiers_may_return(tier):
    root = Tree.build(build(f"system:\n  t:\n    type: {tier.value}\n    returns: {{ ok: bool }}\n"))
    assert root.children["t"].returns


# ------------------------------------------------------------ tier properties


def test_hooks_are_cumulative_across_the_managed_tiers():
    """Each managed tier adds to the one before it; instant carries nothing."""
    assert not Tier.INSTANT.has_execute
    assert not Tier.INSTANT.has_is_finished
    assert not Tier.INSTANT.has_suspension
    assert not Tier.INSTANT.can_return

    # A oneshot task executes but does not decide when it is finished: the base
    # seals that answer, which is the whole point of the tier.
    assert Tier.ONESHOT.has_execute
    assert not Tier.ONESHOT.has_is_finished

    assert Tier.POLLED.has_execute and Tier.POLLED.has_is_finished
    assert not Tier.POLLED.has_suspension

    assert Tier.STATEFUL.has_is_finished and Tier.STATEFUL.has_suspension


def test_only_instant_is_unmanaged():
    assert not Tier.INSTANT.is_managed
    assert all(tier.is_managed for tier in Tier if tier is not Tier.INSTANT)
