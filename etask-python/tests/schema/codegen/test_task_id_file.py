import re

import pytest

from etask.schema.models.node import Node, Kind
from etask.schema.codegen.task_id_file import TaskIdFile


def _task(name, parent, uid, brief=None, description=None):
    t = Node(name=name, kind=Kind.TASK, parent=parent, uid=uid, brief=brief, description=description)
    parent.children[name] = t
    return t


def _scope(name, parent):
    s = Node(name=name, kind=Kind.SCOPE, parent=parent)
    parent.children[name] = s
    return s


def _tree(uid_bytes=1):
    root = Node(name="", kind=Kind.ROOT)
    root.uid_bytes = uid_bytes
    gripper = _scope("gripper", root)
    _task("calibrate", gripper, 42)
    _task("reboot", root, 255)
    return root


def test_enum_symbols_are_underscore_joined_paths_with_values():
    out = TaskIdFile.render(_tree())
    assert "enum class task_id : std::uint8_t {" in out
    assert "gripper_calibrate = 42," in out
    assert "reboot = 255," in out


def test_namespace_and_guard():
    out = TaskIdFile.render(_tree())
    assert "namespace global {" in out
    assert "#ifndef GLOBAL_TASK_ID_HPP_" in out
    assert "#define GLOBAL_TASK_ID_HPP_" in out
    assert "#include <cstdint>" in out


def test_underlying_type_follows_uid_bytes():
    assert "enum class task_id : std::uint16_t" in TaskIdFile.render(_tree(uid_bytes=2))
    assert "enum class task_id : std::uint32_t" in TaskIdFile.render(_tree(uid_bytes=4))
    assert "enum class task_id : std::uint64_t" in TaskIdFile.render(_tree(uid_bytes=8))


def test_marked_generated_do_not_edit():
    assert "DO NOT EDIT" in TaskIdFile.render(_tree())


def test_one_enumerator_per_task():
    out = TaskIdFile.render(_tree())
    enumerators = re.findall(r"^\s+\w+ = \d+,", out, flags=re.MULTILINE)
    assert len(enumerators) == 2


def _documented_tree():
    root = Node(name="", kind=Kind.ROOT)
    root.uid_bytes = 1
    _task("blink", root, 10, brief="toggle the status LED")
    _task("only_desc", root, 20, description="polls a sensor")
    _task("bare", root, 30)
    return root


def test_brief_becomes_member_doc_comment():
    out = TaskIdFile.render(_documented_tree())
    assert "blink = 10," in out
    assert "///< toggle the status LED" in out


def test_description_is_used_when_no_brief():
    out = TaskIdFile.render(_documented_tree())
    assert "///< polls a sensor" in out


def test_undocumented_enumerator_has_no_comment():
    out = TaskIdFile.render(_documented_tree())
    bare_line = next(ln for ln in out.splitlines() if "bare = 30" in ln)
    assert "///<" not in bare_line


def test_brief_collapsed_to_one_line():
    root = Node(name="", kind=Kind.ROOT)
    root.uid_bytes = 1
    _task("t", root, 1, description="first line\nsecond line")
    out = TaskIdFile.render(root)
    assert "///< first line" in out
    assert "second line" not in out


# ------------------------------------------------------- enumerator collisions

def test_two_paths_folding_to_one_enumerator_are_rejected(tmp_path):
    # `a_b.c` and `a.b_c` both flatten to `a_b_c`, so the enum would declare one
    # name twice. Left to the compiler this is `redeclaration of 'a_b_c'` in a
    # generated file the user did not write, naming neither schema path.
    import yaml
    from etask.schema.tree import Tree
    from etask.schema.errors import SchemaShapeError

    path = tmp_path / "schema.yaml"
    path.write_text(yaml.dump({"system": {
        "a_b": {"type": "scope", "children": {"c": {"type": "polled_task"}}},
        "a": {"type": "scope", "children": {"b_c": {"type": "polled_task"}}},
    }}))

    with pytest.raises(SchemaShapeError) as caught:
        TaskIdFile.render(Tree.build(path))

    message = str(caught.value)
    assert "a.b_c" in message and "a_b.c" in message, "both paths must be named"
    assert "a_b_c" in message, "the colliding symbol must be named"


def test_distinct_paths_that_merely_look_alike_are_fine(tmp_path):
    # The check must key on the flattened symbol, not on a resemblance: these
    # two are `a_b_c1` and `a_b_c2` and collide with nothing.
    import yaml
    from etask.schema.tree import Tree

    path = tmp_path / "schema.yaml"
    path.write_text(yaml.dump({"system": {
        "a_b": {"type": "scope", "children": {"c1": {"type": "polled_task"}}},
        "a": {"type": "scope", "children": {"b_c2": {"type": "polled_task"}}},
    }}))

    out = TaskIdFile.render(Tree.build(path))
    assert "a_b_c1" in out and "a_b_c2" in out
