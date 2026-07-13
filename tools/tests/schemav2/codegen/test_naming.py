# tools/tests/schemav2/codegen/test_naming.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-

from schemav2.models.node import Node, Kind
from schemav2.codegen.naming import Naming


def make_task():
    root = Node(name="", kind=Kind.ROOT)
    arm = Node(name="arm", kind=Kind.SCOPE, parent=root)
    shoulder = Node(name="shoulder", kind=Kind.SCOPE, parent=arm)
    task = Node(name="move", kind=Kind.TASK, parent=shoulder)
    root.children["arm"] = arm
    arm.children["shoulder"] = shoulder
    shoulder.children["move"] = task
    return task


def test_names_and_paths():
    task = make_task()
    assert Naming.class_name(task) == "move"
    assert Naming.namespace(task) == "tasks::arm::shoulder"
    assert Naming.uid_symbol(task) == "arm_shoulder_move"
    assert Naming.relative_dir(task) == "arm/shoulder"
    assert Naming.include_guard(task, "hpp") == "TASKS_ARM_SHOULDER_MOVE_HPP_"
    assert Naming.base_include(task) == "../../task.hpp"


def test_root_level_task():
    root = Node(name="", kind=Kind.ROOT)
    task = Node(name="reboot", kind=Kind.TASK, parent=root)
    root.children["reboot"] = task
    assert Naming.namespace(task) == "tasks"
    assert Naming.relative_dir(task) == ""
    assert Naming.base_include(task) == "task.hpp"
