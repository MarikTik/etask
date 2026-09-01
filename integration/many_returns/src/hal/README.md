# hal/ - hardware drivers

The hardware this node drives lives here: motors, sensors, GPIO, ADCs, radios -
anything that pokes a register or a pin. This directory is **yours**; the code
generator never writes into it. It ships empty on purpose - no forced example.

## What goes here

A driver is plain C++ (a class exposing the device's operations) in
`namespace hal`. Keep one device per header, and **nest freely** - the elib
convention is directories-in-directories, and a subdirectory becomes a nested
namespace:

```
hal/
  imu/
    mpu6050.hpp        -> namespace hal::imu     (class mpu6050)
  motor/
    brushless.hpp      -> namespace hal::motor   (class brushless)
```

Purely-software helpers (transports, buffers, codecs) belong in `support/`
instead - the split is a suggestion, not a rule; put things where they read best.
Anything non-trivial can be a `.hpp`/`.cpp` pair; the CMake build compiles every
`hal/**/*.cpp`.

## Including from anywhere

The project root is the include root (see `CMakeLists.txt`), so include a driver
by its **path from the project root**, from any file at any depth - never a
`../../` walk:

```cpp
#include "hal/motor/brushless.hpp"
```

## How a driver reaches a task

A driver is owned by a *context*, not a task. Put an instance in the user-owned
area of the scope's generated context (`sys/<scope>/context.hpp`):

```cpp
// in sys/arm/context.hpp, in the "add your own state" area:
#include "hal/motor/brushless.hpp"
...
struct context {
    hal::motor::brushless motor;   // owned here, shared by the scope's tasks
    ...
};
```

Every task in that scope receives `context&` and drives `ctx.motor`. Hardware is
constructed once, with the context, top-down - never inside a task.
