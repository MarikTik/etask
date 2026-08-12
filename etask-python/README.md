# etask-python

**The Python side of [etask](https://github.com/MarikTik/etask): drive an etask
device from a PC or Raspberry Pi, over Wi-Fi or serial.**

This package is to `etask/core` what
[ecomm-python](https://github.com/MarikTik/ecomm/tree/main/ecomm-python) is to
`ecomm`: a byte-exact transcription of the wire surface. Every layout here comes
from the corresponding C++ header, so a request built in Python decodes on the
device and a reply built by the device decodes here.

It contains only what is **not** project-specific:

| module | mirrors | what it is |
|---|---|---|
| `etask.status_code` | `status_code.hpp` | the status byte, and its three ranges |
| `etask.directive` | `directive.hpp`, `completion_reason.hpp` | the packed command+reason byte |
| `etask.codec` | `eser::flat` | the flat, tagless, little-endian value codec |
| `etask.protocol` | `request.hpp`, `reply.hpp` | request/reply payload layout |
| `etask.client` | — | an async client that keeps many tasks in flight |
| `etask.binding` | — | the base types generated per-task bindings are built from |

Your project's *tasks* — their uids, argument names, and result shapes — are not
here. They are generated from your `schema.yaml`:

```sh
python -m schemav2.cli generate schema.yaml --out sys --python python/tasks.py
```

## Install

`ecomm` is not on PyPI yet, so install it from a checkout first:

```sh
pip install -e ../ecomm/ecomm-python     # or: pip install "ecomm @ git+https://github.com/MarikTik/ecomm#subdirectory=ecomm-python"
pip install -e etask-python
```

## Use

```python
import asyncio
from ecomm.protocol import PacketSchema, Topology
from ecomm.channels import AsyncTcpChannel
from etask import Client

from tasks import Tasks, TaskId          # generated from schema.yaml

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

## Two things the wire cannot tell you

A reply is `[uid][status][result…]`. There is **no invocation id**, which has two
consequences the client handles explicitly rather than hiding:

- Replies are matched to launches **FIFO per uid**. With `concurrency: 1` (the
  default) that is exact. With `concurrency: N`, several instances of one uid can
  be alive and nothing on the wire says which finished, so the oldest outstanding
  launch is the one resolved.
- `pause`/`resume`/`complete` **succeed silently** — the firmware replies to those
  only when they fail. They are fire-and-forget here, and a failure arrives as a
  manager-range reply routed to the client's `on_error` callback.

## Tests

```sh
PYTHONPATH=src python -m pytest tests
```

`tests/test_cpp_golden_bytes.py` decodes packets captured from the **real C++
runtime**, so the two transcriptions are checked against the firmware rather than
against each other.

## License

MIT — see [LICENSE](LICENSE).
