# support/ - software & linking helpers

Software that links parts together lives here: transports (serial, TCP, radio),
buffers, codecs, small protocol glue - as opposed to raw hardware drivers, which
go in `hal/`. This directory is **yours**; the code generator never writes into
it, and it ships empty on purpose - no forced example. (A transport straddles the
two worlds; it belongs here because what it *is* is a communication link. Prefer
it next to the hardware it pokes? Move it to `hal/` - the split is a suggestion,
not a rule.)

## What goes here

Plain C++ in `namespace support`, one thing per header, **nested freely** - the
elib convention is directories-in-directories, and a subdirectory becomes a
nested namespace:

```
support/
  channels/
    uart_channel.hpp   -> namespace support::channels  (class uart_channel)
  codecs/
    cobs.hpp           -> namespace support::codecs     (class cobs)
```

Anything non-trivial can be a `.hpp`/`.cpp` pair; the CMake build compiles every
`support/**/*.cpp`.

## Including from anywhere

The project root is the include root (see `CMakeLists.txt`), so include a helper
by its **path from the project root**, from any file at any depth - never a
`../../` walk:

```cpp
#include "support/channels/uart_channel.hpp"
```

## Writing a transport channel

A transport is an `ecomm::channels::channel<Impl>` (CRTP): the base handles
framing, validation and sealing; your `Impl` supplies only the raw byte I/O. For
a streaming link (UART, TCP byte stream) `Impl` provides three primitives:

```cpp
template<typename Packet> void        do_send(const Packet& p) noexcept;        // write sizeof(Packet) bytes
template<typename Packet> bool        do_try_receive(Packet& p) noexcept;       // read one whole framed packet
                          std::size_t do_receive_raw(std::byte* dst, std::size_t max) noexcept; // raw bytes (ecomm::router)
```

Defining the type instantiates nothing - you create the instance where you wire
it up (`config/wiring.hpp`) and hand it to an `external_channel` and/or an
`ecomm::router`. See the commented example there.
