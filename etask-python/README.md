# etask (Python)

**Both Python halves of [etask](https://github.com/MarikTik/etask) in one
distribution: the client that drives a device, and the generator that produces
the project in the first place.**

```sh
pip install etask              # the runtime: an async client, nothing else
pip install etask[codegen]     # + the `etask` CLI that generates projects
```

```python
from etask import Client                  # runtime
from etask.schema import Tree             # generator
```

```sh
etask generate schema.yaml --out sys --python python/tasks.py
```

## Why one package

The two halves share one thing that must never drift: the wire contract. The
status codes the generator validates a schema against are the status codes the
client decodes replies with; the value types it lowers to C++ are the ones the
client unpacks. Splitting them into separate distributions means two copies of
those tables and a version matrix to keep them compatible. Keeping them together
means one source and a test that checks both against the C++ header.

What is *not* shared is dependencies. A Raspberry Pi driving a device runs tasks;
it does not read schemas, so PyYAML and jsonschema live behind the `codegen`
extra rather than in the runtime's dependency list. Importing `etask.schema`
without them raises a message telling you to install the extra, instead of a bare
`ModuleNotFoundError` for a package you never asked for.

## The runtime — `etask`

A byte-exact transcription of the wire surface, the way
[ecomm-python](https://github.com/MarikTik/ecomm/tree/main/ecomm-python) is for
`ecomm`. Every layout comes from the corresponding C++ header, so a request built
here decodes on the device and a reply built by the device decodes here.

| module | mirrors | what it is |
|---|---|---|
| `etask.status_code` | `status_code.hpp` | the status byte, and its three ranges |
| `etask.directive` | `directive.hpp`, `completion_reason.hpp` | the packed command+reason byte |
| `etask.codec` | `eser::flat` | the flat, tagless, little-endian value codec |
| `etask.protocol` | `request.hpp`, `reply.hpp` | request/reply payload layout |
| `etask.client` | — | an async client that keeps many tasks in flight |
| `etask.binding` | — | the base types generated per-task bindings are built from |

Your project's *tasks* — their uids, argument names, and result shapes — are not
here. They are generated into your project as `python/tasks.py`.

```python
import asyncio
from ecomm.protocol import PacketSchema, Topology
from ecomm.channels import AsyncTcpChannel
from etask import Client

from tasks import Tasks                    # generated from schema.yaml

async def main():
    schema = PacketSchema(packet_size=32, topology=Topology.NETWORK, board_id=2)
    async with AsyncTcpChannel(schema, host="192.168.1.50", port=5000) as channel:
        async with Client(channel, uid_bytes=Tasks.UID_BYTES, receiver_id=1) as client:
            tasks = Tasks(client)

            # Launching does not block, so these fly together.
            fix, altitude = await asyncio.gather(
                tasks.sensors.gps.fix(timeout_ms=5000),
                tasks.sensors.baro.read_altitude(),
            )

            match fix:
                case tasks.sensors.gps.fix.Finished(lat=lat, lon=lon, sats=sats):
                    print(f"fix: {lat},{lon} on {sats} satellites")
                case tasks.sensors.gps.fix.Timeout(waited_ms=waited, sats_seen=seen):
                    print(f"no fix after {waited}ms, saw {seen} satellites")

asyncio.run(main())
```

A task's result type is chosen by the status byte its reply carries — that is
what the schema's status-keyed `returns:` declares, and what
`outcome::with_status(...)` sets on the device. A completion whose status the
schema does not describe comes back as `UndeclaredResult` (raw bytes, not an
error); a *manager* rejection — unknown uid, concurrency cap reached — raises
`TaskRejected`, because in that case no task ran and there is no result at all.

### Two things the wire cannot tell you

A reply is `[uid][status][result…]`. There is **no invocation id**, which has two
consequences the client handles explicitly rather than hiding:

- Replies are matched to launches **FIFO per uid**. With `concurrency: 1` (the
  default) that is exact. With `concurrency: N`, several instances of one uid can
  be alive and nothing on the wire says which finished, so the oldest outstanding
  launch is the one resolved.
- `pause`/`resume`/`complete` **succeed silently** — the firmware replies to those
  only when they fail. They are fire-and-forget here, and a failure arrives as a
  manager-range reply routed to the client's `on_error` callback.

## The generator — `etask.schema`

Reads a `schema.yaml` and emits/maintains the C++ project around it, plus the
Python bindings above. Installed as the `etask` command:

| command | purpose |
|---|---|
| `etask scaffold --out <dir>` | Lay down the non-generated half of a project once. Existing files are kept. |
| `etask generate <schema> --out <dir>/sys …` | Produce/update the generated half: the `sys/` tree, `task_id.hpp`/`task_list.hpp`, and (with `--python`) the client bindings. |
| `etask rename <schema> --out <dir>/sys <task> <new>` | Rename a task across schema and files, carrying its wire uid along. |

Full documentation of the schema format, the ownership model, and the uid ledger
lives in the [top-level README](../README.md).

The C++ side's CMake target runs the generator **without installing anything**,
straight from a checkout:

```cmake
PYTHONPATH=${etask_SOURCE_DIR}/etask-python ${Python3_EXECUTABLE} -m etask.schema.cli generate …
```

## Install from a checkout

`ecomm` is not on PyPI yet, so install it from its checkout first:

```sh
pip install -e ../ecomm/ecomm-python     # or: pip install "ecomm @ git+https://github.com/MarikTik/ecomm#subdirectory=ecomm-python"
pip install -e ".[codegen]"
```

## Tests

```sh
python -m pytest            # from the repo root, or from here
```

`tests/` covers both halves: `tests/` for the runtime, `tests/schema/` for the
generator. `tests/test_cpp_golden_bytes.py` decodes packets captured from the
**real C++ runtime**, and `tests/schema/test_wire_tables_agree.py` parses
`status_code.hpp` itself — so the transcriptions are checked against the
firmware, not against each other.

## License

MIT — see [LICENSE](LICENSE).
