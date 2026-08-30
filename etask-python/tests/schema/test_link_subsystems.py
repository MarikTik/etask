# tools/tests/etask.schema/test_link_subsystems.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

"""A link's `subsystems:` - what it carries, and so how big its frames are.

The rule under test is that a link carries whole *subsystems*, never individual
tasks. That is what makes the declaration survive a new task being added, and it
is what keeps the schema from describing hardware that is not wired that way.
The one exception is a task at the top level, which belongs to no subsystem.
"""

import json

import pytest

from etask.schema.tree import Tree
from etask.schema.errors import SchemaShapeError


def write(tmp_path, data, name="schema.json"):
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return path


#: A device with two subsystems of different widths, a nested scope, an abstract
#: scope, and a task at the top level - one of each thing the resolution pass has
#: to cope with.
_SYSTEM = {
    "rotors": {"type": "scope", "children": {
        "rotor": {"type": "abstract_scope", "instances": ["fl", "fr"], "children": {
            "spin": {"type": "polled_task", "params": {"level": "float"}},
        }},
    }},
    "sensors": {"type": "scope", "children": {
        "imu": {"type": "scope", "children": {
            "read": {"type": "oneshot_task",
                     "returns": {"x": "float", "y": "float", "z": "float"}},
        }},
    }},
    "nav": {"type": "scope", "children": {
        "fly_to": {"type": "stateful_task",
                   "params": {"x": "float", "y": "float", "z": "float", "speed": "float"}},
    }},
    "failsafe": {"type": "instant_task"},
}


def build(tmp_path, links, system=None):
    data = {"system": system if system is not None else _SYSTEM}
    if links is not None:
        data["links"] = links
    return Tree.build(write(tmp_path, data))


def carried(root, name):
    """The uids a link carries, resolved."""
    return root.links.uids_for(name, frozenset())


def tasks(node):
    found = [node] if node.is_task else []
    for child in node.children.values():
        found.extend(tasks(child))
    return found


def uid_of(root, dotted):
    """The uid of a task named by its dotted path."""
    node = root
    for segment in dotted.split("."):
        node = node.children[segment]
    return node.uid


# --------------------------------------------------------------- the default

def test_a_link_without_subsystems_carries_everything(tmp_path):
    # The key is optional, and its absence has to keep meaning "all" rather than
    # being resolved to today's uids - otherwise a link would quietly stop
    # carrying tasks added after it was written.
    root = build(tmp_path, {"serial": {"transport": "uart"}})
    assert root.links.carries_everything("serial")


def test_carrying_everything_is_not_a_snapshot_of_the_uids(tmp_path):
    # Distinct from a link that happens to list every subsystem: only the
    # unrestricted one keeps its meaning as the schema grows.
    root = build(tmp_path, {
        "open": {"transport": "uart"},
        "listed": {"transport": "uart",
                   "subsystems": ["rotors", "sensors", "nav", "failsafe"]},
    })
    assert root.links.carries_everything("open")
    assert not root.links.carries_everything("listed")
    # ...even though, today, they carry exactly the same tasks.
    every = frozenset(task.uid for task in tasks(root))
    assert carried(root, "listed") == every


def test_a_schema_with_no_links_still_builds(tmp_path):
    root = build(tmp_path, None)
    assert not root.links


# ------------------------------------------------------------- what resolves

def test_a_subsystem_carries_its_tasks(tmp_path):
    root = build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["nav"]}})
    assert carried(root, "esc") == {uid_of(root, "nav.fly_to")}


def test_a_subsystem_carries_nested_scopes_recursively(tmp_path):
    # `sensors` holds no task directly; `sensors.imu.read` is two levels down.
    root = build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["sensors"]}})
    assert carried(root, "esc") == {uid_of(root, "sensors.imu.read")}


def test_a_nested_scope_can_be_named_directly(tmp_path):
    root = build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["sensors.imu"]}})
    assert carried(root, "esc") == {uid_of(root, "sensors.imu.read")}


def test_a_subsystem_carries_every_instance_of_an_abstract_scope(tmp_path):
    # Resolution runs after expansion, so `rotors` reaches the instances the
    # abstract scope became - which do not exist when `links:` is parsed.
    root = build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["rotors"]}})
    assert carried(root, "esc") == {
        uid_of(root, "rotors.fl.spin"),
        uid_of(root, "rotors.fr.spin"),
    }


def test_several_subsystems_union(tmp_path):
    root = build(tmp_path, {
        "esc": {"transport": "uart", "subsystems": ["nav", "sensors"]}})
    assert carried(root, "esc") == {
        uid_of(root, "nav.fly_to"),
        uid_of(root, "sensors.imu.read"),
    }


def test_naming_a_subsystem_twice_carries_it_once(tmp_path):
    root = build(tmp_path, {
        "esc": {"transport": "uart", "subsystems": ["nav", "nav"]}})
    assert carried(root, "esc") == {uid_of(root, "nav.fly_to")}


def test_one_task_may_be_carried_by_several_links(tmp_path):
    # Nothing partitions the device: a failsafe belongs on every link that could
    # need to reach it.
    root = build(tmp_path, {
        "esc": {"transport": "uart", "subsystems": ["rotors", "failsafe"]},
        "radio": {"transport": "wifi", "subsystems": ["nav", "failsafe"]},
    })
    failsafe = uid_of(root, "failsafe")
    assert failsafe in carried(root, "esc")
    assert failsafe in carried(root, "radio")


def test_a_subsystem_on_no_link_is_allowed(tmp_path):
    # An internal-only subsystem is a legitimate design - the tasks are reachable
    # from `internal_channel`, just not from the wire.
    root = build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["nav"]}})
    assert uid_of(root, "sensors.imu.read") not in carried(root, "esc")


# --------------------------------------------------- the top-level exception

def test_a_root_level_task_may_be_named_directly(tmp_path):
    # It belongs to no subsystem, so there is no enclosing scope to name and no
    # sibling it could be split from. Refusing it would make a top-level
    # failsafe unreachable from every link that restricts its subsystems.
    root = build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["failsafe"]}})
    assert carried(root, "esc") == {uid_of(root, "failsafe")}


def test_a_nested_task_may_not_be_named(tmp_path):
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["nav.fly_to"]}})
    message = str(caught.value)
    assert "is a task, not a subsystem" in message
    # The message has to say what to write instead, and the enclosing scope is it.
    assert "nav" in message


# ------------------------------------------------------------- what is wrong

def test_an_unknown_subsystem_is_an_error(tmp_path):
    # A typo would otherwise make the link silently narrower than intended -
    # the failure would appear at runtime, on the one task nobody tested.
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["rotorz"]}})
    assert "names no subsystem" in str(caught.value)


def test_an_unknown_subsystem_lists_what_it_could_have_meant(tmp_path):
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["rotorz"]}})
    message = str(caught.value)
    for name in ("rotors", "sensors", "nav"):
        assert name in message


def test_an_unknown_nested_segment_names_the_part_that_resolved(tmp_path):
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystems": ["sensors.gps"]}})
    message = str(caught.value)
    assert "sensors" in message and "gps" in message


def test_a_scope_with_no_tasks_is_an_error(tmp_path):
    system = dict(_SYSTEM, hollow={"type": "scope", "children": {
        "deeper": {"type": "scope", "children": {}}}})
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path,
              {"esc": {"transport": "uart", "subsystems": ["hollow"]}},
              system=system)
    assert "holds no task" in str(caught.value)


def test_an_empty_subsystem_list_is_an_error(tmp_path):
    # A link that carries nothing can be opened but never used, which is far
    # more likely a mistake than an intent.
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystems": []}})
    assert "carry no task at all" in str(caught.value)


def test_subsystems_must_be_a_list(tmp_path):
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystems": "rotors"}})
    assert "must be a list" in str(caught.value)


@pytest.mark.parametrize("entry", [3, None, True, {"rotors": 1}, ["rotors"], ""])
def test_every_entry_must_be_a_scope_name(tmp_path, entry):
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystems": [entry]}})
    assert "must be a scope name" in str(caught.value)


def test_an_unknown_link_key_is_still_rejected(tmp_path):
    # Adding `subsystems` to the grammar must not open the door to neighbours.
    with pytest.raises(SchemaShapeError) as caught:
        build(tmp_path, {"esc": {"transport": "uart", "subsystem": ["nav"]}})
    assert "unknown link key" in str(caught.value)


# ------------------------------------------------------------------ plumbing

def test_the_declaration_is_kept_verbatim(tmp_path):
    # The resolved uids are what the generator uses, but the declared names are
    # what the generated comments quote back to the reader.
    root = build(tmp_path, {
        "esc": {"transport": "uart", "subsystems": ["nav", "rotors"]}})
    assert root.links.get("esc").subsystems == ("nav", "rotors")


def test_an_unrestricted_link_declares_nothing(tmp_path):
    root = build(tmp_path, {"serial": {"transport": "uart"}})
    assert root.links.get("serial").subsystems is None
