# etask codegen example

`schema.yaml` (and its `schema.json` twin) is an expanded showcase schema
describing a small manipulator robot (gripper, arm joints, IMU).
`robot/` is the `.hpp`/`.cpp` tree produced from it by:

```
etask-gen generate examples/schema.yaml --out examples/robot
```

It is **illustrative, not compile-ready** — the deferred wiring pass is what makes
it build. Known gaps to keep in mind while reviewing:

- References `../task.hpp` (the `using task = …` alias) and `global::task_id::*`
  enumerators that are **not generated yet** (deferred enum/wiring pass).
- Tasks with `returns:` get an `on_complete()` override returning
  `etools::memory::buffer<>`, but the actual result **packing** is left as a
  `// TODO` for you to fill (the schema fixes the return *shape*, not the values).
- Abstract-scope instances (`arm/base`, `arm/elbow`) are **fully duplicated**
  rather than sharing one template — the DRY-abstract pass is still pending.
