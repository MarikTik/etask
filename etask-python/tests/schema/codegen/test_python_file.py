# tools/tests/etask.schema/codegen/test_python_file.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""The generated Python bindings: what they say, and that they actually run."""

import asyncio
import importlib.util
import sys

import pytest

from etask.schema.codegen.emitter import Emitter
from etask.schema.codegen.python_file import PythonFile
from etask.schema.models.type_map import TypeMap
from etask.schema.tree import Tree

_SCHEMA = """
sensors:
  type: scope
  brief: the sensor pod
  children:
    gps:
      type: scope
      children:
        fix:
          type: polled_task
          brief: acquire a GPS fix
          params: { timeout_ms: uint32 }
          returns:
            finished:     { lat: float, lon: float, sats: uint8 }
            task_timeout: { waited_ms: uint32 }
            aborted:      {}
            custom(0x71): { almanac_age_s: uint32 }
reboot:
  type: polled_task
  params: {}
"""


def render(tmp_path, text=_SCHEMA):
    schema = tmp_path / "schema.yaml"
    schema.write_text(text)
    root = Tree.build(schema)
    return PythonFile.render(root, root.uid_bytes or 1), root


def load(tmp_path, text=_SCHEMA):
    """Renders the module, imports it for real, and hands back the module."""
    source, root = render(tmp_path, text)
    path = tmp_path / "generated_tasks.py"
    path.write_text(source)
    spec = importlib.util.spec_from_file_location("generated_tasks", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["generated_tasks"] = module
    spec.loader.exec_module(module)
    return module, root


# -----------------------
# Content
# -----------------------

def test_uids_match_the_schema(tmp_path):
    module, root = load(tmp_path)
    assert module.TaskId.SENSORS_GPS_FIX == root.children["sensors"].children["gps"].children["fix"].uid
    assert module.TaskId.REBOOT == root.children["reboot"].uid
    assert module.UID_BYTES == root.uid_bytes


def test_one_dataclass_per_declared_shape(tmp_path):
    module, _ = load(tmp_path)
    fix = module._SensorsGpsFix

    assert [f for f in fix.Finished.__dataclass_fields__] == ["lat", "lon", "sats"]
    assert [f for f in fix.Timeout.__dataclass_fields__] == ["waited_ms"]
    assert list(fix.Aborted.__dataclass_fields__) == []          # a shape may carry nothing
    assert [f for f in fix.Custom71.__dataclass_fields__] == ["almanac_age_s"]


def test_shapes_are_keyed_by_status_code(tmp_path):
    module, _ = load(tmp_path)
    assert sorted(module._SensorsGpsFix.SHAPES) == [0x20, 0x21, 0x22, 0x71]


def test_a_task_without_returns_declares_no_shapes(tmp_path):
    module, _ = load(tmp_path)
    assert module._Reboot.SHAPES == {}
    assert module._Reboot.PARAMS == ()


def test_the_tree_mirrors_the_schema_paths(tmp_path):
    module, _ = load(tmp_path)
    tasks = module.Tasks(client=None)
    assert tasks.sensors.gps.fix.PATH == "sensors.gps.fix"
    assert tasks.reboot.PATH == "reboot"


def test_generated_source_is_stable(tmp_path):
    # It is a pure projection of the schema: same schema, same bytes, so a
    # regeneration never shows up as a spurious diff.
    first, _ = render(tmp_path)
    second, _ = render(tmp_path)
    assert first == second


def test_annotations_cover_every_schema_type(tmp_path):
    # A type the schema accepts but the Python emitter has no annotation for
    # would fail at generation time, not at use time - so check the tables agree.
    from etask.schema.codegen.python_file import _ANNOTATIONS
    assert sorted(_ANNOTATIONS) == sorted(TypeMap.allowed())


# -----------------------
# Behavior, against the real runtime
# -----------------------

etask = pytest.importorskip("etask", reason="etask-python not installed")


class FakeClient:
    """Stands in for etask.Client: records launches, replies on demand."""

    def __init__(self, reply):
        self._reply = reply
        self.launched = []

    def launch(self, uid, args=b""):
        self.launched.append((uid, args))
        future = asyncio.get_running_loop().create_future()
        future.set_result(self._reply)
        return future


def test_a_call_packs_its_arguments_and_decodes_its_shape(tmp_path):
    from etask.protocol import Reply
    from etask import codec

    module, _ = load(tmp_path)

    async def scenario():
        result = codec.pack(("float", "float", "uint8"), (12.5, -3.25, 9))
        client = FakeClient(Reply(uid=module.TaskId.SENSORS_GPS_FIX, status=0x20, result=result))
        tasks = module.Tasks(client)
        got = await tasks.sensors.gps.fix(timeout_ms=5000)
        return client.launched, got

    launched, got = asyncio.run(scenario())
    assert launched == [(module.TaskId.SENSORS_GPS_FIX, codec.pack(("uint32",), (5000,)))]
    assert got == module._SensorsGpsFix.Finished(lat=12.5, lon=-3.25, sats=9)


def test_the_status_byte_picks_the_shape(tmp_path):
    from etask.protocol import Reply
    from etask import codec

    module, _ = load(tmp_path)

    async def scenario():
        client = FakeClient(Reply(uid=1, status=0x22, result=codec.pack(("uint32",), (5000,))))
        return await module.Tasks(client).sensors.gps.fix(timeout_ms=1)

    assert asyncio.run(scenario()) == module._SensorsGpsFix.Timeout(waited_ms=5000)


def test_an_undeclared_status_comes_back_raw(tmp_path):
    from etask.binding import UndeclaredResult
    from etask.protocol import Reply

    module, _ = load(tmp_path)

    async def scenario():
        client = FakeClient(Reply(uid=1, status=0x26, result=b"\x01\x02"))
        return await module.Tasks(client).sensors.gps.fix(timeout_ms=1)

    got = asyncio.run(scenario())
    assert isinstance(got, UndeclaredResult)
    assert got.status == 0x26 and got.status_name == "task_busy"


def test_a_manager_rejection_raises(tmp_path):
    from etask.binding import TaskRejected
    from etask.protocol import Reply

    module, _ = load(tmp_path)

    async def scenario():
        client = FakeClient(Reply(uid=1, status=0x14, result=b""))
        return await module.Tasks(client).sensors.gps.fix(timeout_ms=1)

    with pytest.raises(TaskRejected, match="task_unknown"):
        asyncio.run(scenario())


def test_generate_writes_the_python_module(tmp_path):
    schema = tmp_path / "schema.yaml"
    schema.write_text(_SCHEMA)
    out = tmp_path / "sys"
    python = tmp_path / "python" / "tasks.py"
    report = Emitter.generate(Tree.build(schema), out, python_path=python)

    assert python.exists()
    assert str(python) in report.created
    assert "class Tasks(Scope):" in python.read_text()
