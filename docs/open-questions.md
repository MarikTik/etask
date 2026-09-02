# Open questions

Design decisions that are deferred rather than forgotten. Each states what was
found, why it was not simply fixed, and what a decision would have to settle.

Distinct from `benchmarking-plan.md`'s open-work list, which is work whose
*shape* is already agreed. These are the ones where the answer is a judgement
call, not an implementation.

---

## 1. The handshake chapter — `begin_handshake` and the `Hub` contract

**Status:** deferred by the user on 2026-09-02, to be resolved together with the
rest of the handshake design rather than patched in isolation.

### What was found

`external_channel::begin_handshake()` sends the preamble like this:

```cpp
struct frame { std::byte bytes[protocol::preamble::size]; };  // 14 bytes
frame out{};
_handshake.local_preamble(out.bytes);
(void)_hub.send(out);
```

That calls `Hub::send` with a **14-byte preamble struct**, not with either of the
link's packet types. Whether it compiles depends entirely on how the hub declares
`send`:

| Hub | `send` signature | `begin_handshake()` |
|---|---|---|
| ecomm's `arduino_serial_channel` | `do_send` is a **member template over `Packet`** (`arduino_serial_channel.tpp:52`) | compiles - accepts any trivially-copyable frame |
| A hand-written hub | `send_result send(ReplyPacket&)` - the documented shape | **does not compile** |

So a real transport is fine and the bug bites hand-written hubs, which is why it
went unnoticed: the test harnesses are exactly the hubs that break.

### What it cost already

`integration/many_returns` could not call `begin_handshake()` at all. Its
loopback hub declares `send(ReplyPacket&)`, so the preamble frame does not fit
the signature. The harness had to encode the preamble itself and call
`accept_handshake()` directly:

```cpp
std::byte preamble[etask::core::protocol::preamble::size]{};
etask::core::protocol::preamble::encode(preamble, generated::schema_fingerprint);
(void)config::external.accept_handshake(preamble);
```

Identical bytes by the same encoder, so it is correct - but it bypasses the API
that exists for the job, and nothing tells a hub author that their hub cannot
drive a handshake until they try.

Until that was added, every reply in that project was silently dropped:
`complete()` refuses to send while `is_ready()` is false, and `is_ready()` is
false on a fingerprinted link until the exchange happens. Sixteen cases returned
empty frames and the driver reported "the task never completed, or never
started" - both halves wrong.

### What a decision has to settle

1. **Is a `Hub` required to accept any trivially-copyable frame, or only the
   link's packet types?** ecomm's transport already does the former; the
   documented contract implies the latter. Whichever is intended, both
   `external_channel`'s docs and the hub-writing guidance should say it.
2. **If the narrower contract stands**, `begin_handshake()` needs a way to emit
   14 bytes through a packet-typed `send` - padding into a request packet, or a
   separate `send_preamble` the hub opts into.
3. **Should a hub that cannot carry a preamble be a compile error** at channel
   instantiation, rather than only when someone calls `begin_handshake()`?
4. **Should `accept_handshake`-only usage be blessed** as the documented path for
   in-process and loopback hubs, since the exchange there is with itself?

### Where the pieces are

- `etask/core/channels/external_channel.tpp:162` - `begin_handshake()`
- `etask/core/channels/external_channel.tpp:185` - `accept_handshake()`
- `etask/core/channels/external_channel.tpp:199` - `is_ready()`, the gate
- `etask/core/channels/external_channel.tpp:40` - `complete()` returning early
- `integration/many_returns/src/support/harness.cpp` - the workaround
- `integration/many_returns/src/support/loopback_hub.hpp:101` - the narrow `send`
- `integration/multi_link` - the project that drives a handshake properly
