# tools/tests/etask.schema/codegen/test_task_list_file.py
# SPDX-License-Identifier: MIT

from etask.schema.tree import Tree
from etask.schema.codegen.emitter import Emitter
from etask.schema.codegen.task_list_file import TaskListFile
from etask.schema.models.tier import Tier


def test_render_typelist_no_trailing_comma():
    out = TaskListFile.render([
        ("../tasks/blink.hpp", "sys::blink", Tier.POLLED, 1),
        ("../tasks/motor/spin.hpp", "sys::motor::spin", Tier.POLLED, 1),
    ])
    assert "using polled_tasks = etools::meta::typelist<" in out
    assert "sys::blink," in out          # non-last has comma
    assert "sys::motor::spin" in out
    assert "sys::motor::spin," not in out  # last has NO trailing comma (ill-formed)
    assert '#include "../tasks/blink.hpp"' in out
    assert "namespace generated {" in out
    assert "DO NOT EDIT" in out


def test_render_empty_is_wellformed():
    out = TaskListFile.render([])
    # Every tier is emitted even when empty: the facade needs all three names,
    # and an empty list is what tells it to instantiate nothing for that tier.
    assert "using instant_tasks = etools::meta::typelist<>;" in out
    assert "using polled_tasks = etools::meta::typelist<>;" in out
    assert "using stateful_tasks = etools::meta::typelist<>;" in out


def test_tasks_are_split_by_tier():
    out = TaskListFile.render([
        ("a.hpp", "sys::cmd", Tier.INSTANT, 1),
        ("b.hpp", "sys::once", Tier.ONESHOT, 1),
        ("c.hpp", "sys::poll", Tier.POLLED, 1),
        ("d.hpp", "sys::hold", Tier.STATEFUL, 1),
    ])
    # Split on the declarations, not the header comment that also names them.
    instant = out.split("using instant_tasks")[1].split(">;")[0]
    polled = out.split("using polled_tasks")[1].split(">;")[0]
    stateful = out.split("using stateful_tasks")[1].split(">;")[0]
    assert "sys::cmd" in instant
    # A oneshot task IS a polled task - same manager, same list.
    assert "sys::once" in polled and "sys::poll" in polled
    assert "sys::hold" in stateful
    assert "sys::hold" not in polled


def test_emit_task_list_relative_includes(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n"
        "  blink:\n    type: polled_task\n"
        "  motor:\n    type: scope\n    children:\n"
        "      spin:\n        type: polled_task\n        params: { duty: uint8 }\n"
    )
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    report = Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    text = list_path.read_text()
    # includes are relative from generated/ to tasks/
    assert '#include "../tasks/blink.hpp"' in text
    assert '#include "../tasks/motor/spin.hpp"' in text
    assert "sys::blink," in text
    assert "sys::motor::spin" in text
    assert str(list_path) in report.created


def test_task_list_always_regenerated(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("system:\n  blink:\n    type: polled_task\n")
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    list_path.write_text("// hand edit\n")
    report = Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    assert "// hand edit" not in list_path.read_text()   # overwritten
    assert str(list_path) in report.updated


def test_concurrency_lowers_to_capacity(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n"
        "  blink:\n    type: polled_task\n"                        # default 1 -> bare
        "  mover:\n    type: polled_task\n    concurrency: 3\n"   # -> capacity<..., 3>
    )
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    text = list_path.read_text()
    assert "sys::blink," in text                        # bare, unchanged
    assert "etools::factories::utils::capacity<sys::mover, 3>" in text
    assert "#include <etools/factories/utils/capacity.hpp>" in text


def test_no_capacity_include_when_all_bare(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text("system:\n  blink:\n    type: polled_task\n    concurrency: 1\n")  # explicit 1 == bare
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    text = list_path.read_text()
    assert "capacity<" not in text
    assert "factories/utils/capacity.hpp" not in text


def test_budgets_sum_each_tier_capacity():
    out = TaskListFile.render([
        ("a.hpp", "sys::cmd", Tier.INSTANT, 1),      # no budget for instant
        ("b.hpp", "sys::once", Tier.ONESHOT, 2),     # oneshot counts toward polled
        ("c.hpp", "sys::poll", Tier.POLLED, 3),
        ("d.hpp", "sys::hold", Tier.STATEFUL, 4),
    ])
    assert "inline constexpr std::size_t polled_budget = 5;" in out     # 2 + 3
    assert "inline constexpr std::size_t stateful_budget = 4;" in out
    # An instant command occupies no storage, so bounding it would be meaningless.
    assert "instant_budget" not in out


def test_budgets_emitted_for_empty_tiers():
    out = TaskListFile.render([])
    # The facade reads both names unconditionally, and a zero budget is what
    # selects the inert stand-in for a tier with nothing in it.
    assert "inline constexpr std::size_t polled_budget = 0;" in out
    assert "inline constexpr std::size_t stateful_budget = 0;" in out
    assert "#include <cstddef>" in out


def test_budget_follows_concurrency(tmp_path):
    sp = tmp_path / "schema.yaml"
    sp.write_text(
        "system:\n"
        "  blink:\n    type: polled_task\n"                      # 1 slot
        "  mover:\n    type: polled_task\n    concurrency: 3\n"  # 3 slots
        "  hold:\n    type: stateful_task\n    concurrency: 2\n" # 2 slots, other tier
    )
    tasks_dir = tmp_path / "tasks"
    list_path = tmp_path / "generated" / "task_list.hpp"
    Emitter.generate(Tree.build(sp), tasks_dir, task_list_path=list_path)
    text = list_path.read_text()
    assert "inline constexpr std::size_t polled_budget = 4;" in text     # 1 + 3
    assert "inline constexpr std::size_t stateful_budget = 2;" in text
