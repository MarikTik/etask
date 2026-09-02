/**
* @file main.cpp
*
* @brief Runtime benchmark: what an etask task costs against the same work invoked directly.
*
* @ingroup etask_bench
*
* Prints a table over serial at 115200 baud. Flash it and read the numbers; nothing needs to be
* attached beyond the board itself.
*
* ## The question this answers
*
* Every case here is a **paired comparison**: identical work, reached two ways.
*
*   - `raw`  - the work behind a hand-written `if`/`switch` on a uid, calling through a plain
*              function pointer. This is what a project writes when it does not use a framework.
*   - `task` - the same work as an etask task, dispatched through the manager.
*
* The delta between the two is the framework's cost, and it is the only number worth publishing.
* An absolute figure for either column is dominated by the work itself, which is the point of the
* workload ladder below.
*
* ## Why the workload ladder exists
*
* Abstraction overhead is a *fixed* per-invocation cost. Its significance is entirely relative to
* the work it wraps, so a single workload size cannot answer "does this matter". Each case runs at
* three sizes:
*
*   - `w0` **state write** - one store. The framework cost is the whole cost; this is the
*                            worst case for etask and the honest upper bound on relative overhead.
*   - `w1` **light**        - ~20 flops. A plausible sensor conversion or PID step.
*   - `w2` **heavy**        - ~500 flops. A filter update or a matrix step.
*
* Read the table by column: `w0` says how expensive the abstraction is, `w2` says whether anyone
* should care.
*
* ## Measurement hygiene (all four matter; each one, omitted, flatters the framework)
*
*  1. **N iterations per timed region.** One dispatch is far below one clock tick.
*  2. **Calibration subtracted.** An empty loop of identical shape (counter, store, sink fold) is
*     timed first and removed, so the figure is marginal cost, not loop scaffolding.
*  3. **A `volatile` sink, fed by every result.** Without it the optimizer deletes the measurement
*     outright and reports absurdly low numbers.
*  4. **Inputs that vary per iteration**, so no computation can be hoisted out of the loop.
*
* A fifth, specific to a paired comparison: **the raw path must not be devirtualizable**. Its
* function pointer is fetched through a `volatile` table, otherwise the compiler inlines the whole
* raw call and the comparison becomes "inlined work vs virtual work" rather than
* "indirect call vs virtual call".
*
* @note All figures are ns/operation at `-O2`. `-Os` is measured separately by the static suite;
*       relative overhead differs between them and both are reported in RESULTS.md.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-27
*
* @copyright
* MIT License
* SPDX-License-Identifier: MIT
*/
// See heap.cpp: exactly one of the two compiles, selected by BENCH_HEAP.
#ifndef BENCH_HEAP

#include <Arduino.h>
#include <etask/core/core.hpp>
#include <etools/meta/typelist.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <cstdint>

using namespace etask::core;

namespace {

    /// Repetitions per timed region; large enough that clock granularity is negligible.
    constexpr uint32_t iterations = 20000;

    /// Sink the optimizer cannot prove unused, anchoring every measured loop.
    volatile uint32_t sink = 0;

    /// Microseconds since boot, from the most precise counter the target offers.
    inline uint64_t now_us()
    {
    #if defined(ESP32)
        return static_cast<uint64_t>(esp_timer_get_time());
    #else
        return static_cast<uint64_t>(micros());
    #endif
    }

    // ---------------------------------------------------------------- the workloads
    //
    // Three sizes, each a plain function of one varying input so the raw and task paths can run
    // *byte-identical* work. They are deliberately not templates on the size: the task tiers below
    // call these same functions, so any difference in the measurement cannot come from the work.

    /// w0: a state write. One store - the smallest thing a real command does.
    volatile uint32_t w0_state = 0;
    inline uint32_t work_state(uint32_t i)
    {
        w0_state = i;
        return i;
    }

    /// w1: ~20 flops. A sensor conversion or one PID step.
    inline uint32_t work_light(uint32_t i)
    {
        float acc = static_cast<float>(i);
        for (int k = 0; k < 5; ++k)
            acc = acc * 1.0009f + 0.5f;
        return static_cast<uint32_t>(acc);
    }

    /// w2: ~500 flops. A filter update or a small matrix step.
    inline uint32_t work_heavy(uint32_t i)
    {
        float acc = static_cast<float>(i);
        for (int k = 0; k < 125; ++k)
            acc = acc * 1.0009f + 0.5f;
        return static_cast<uint32_t>(acc);
    }

    /// The three workloads, addressed by index so every table row can sweep them uniformly.
    enum class workload : uint8_t { state = 0, light = 1, heavy = 2 };
    constexpr const char* workload_name[] = { "w0 state-write", "w1 light ~20fl", "w2 heavy ~500fl" };

    inline uint32_t run_workload(workload w, uint32_t i)
    {
        switch (w) {
            case workload::state: return work_state(i);
            case workload::light: return work_light(i);
            case workload::heavy: return work_heavy(i);
        }
        return 0;
    }

    // ------------------------------------------------------- the raw reference path
    //
    // What a project writes without a framework: a uid arrives, an if/switch selects a handler,
    // the handler runs. Two variants, because "raw" is not one thing and the honest comparison
    // needs both:
    //
    //   raw_switch  - a switch on the uid calling a *direct* function. The compiler may inline
    //                 the callee entirely. This is the fastest possible hand-written dispatch and
    //                 the fairest floor for "how much does etask cost me".
    //   raw_fnptr   - a switch selecting a function *pointer* from a volatile table, then calling
    //                 it. The indirect call cannot be devirtualized, which is the same constraint
    //                 a virtual call operates under - so this isolates etask's overhead from the
    //                 mere fact of an indirect call.
    //
    // Reporting only raw_switch overstates etask's cost (it charges etask for indirection the
    // programmer would also pay on any extensible design); reporting only raw_fnptr understates
    // it. Both are in the table.

    using handler_t = uint32_t (*)(uint32_t);

    uint32_t handler_state(uint32_t i) { return work_state(i); }
    uint32_t handler_light(uint32_t i) { return work_light(i); }
    uint32_t handler_heavy(uint32_t i) { return work_heavy(i); }

    /// Volatile so the pointer cannot be constant-folded back into a direct (inlinable) call.
    handler_t volatile handler_table[3] = { &handler_state, &handler_light, &handler_heavy };

    /// Hand-written dispatch, direct call. The compiler is free to inline the work.
    inline uint32_t raw_switch(uint8_t uid, uint32_t i)
    {
        switch (uid) {
            case 0: return handler_state(i);
            case 1: return handler_light(i);
            case 2: return handler_heavy(i);
        }
        return 0;
    }

    /// Hand-written dispatch, indirect call through a volatile table. Not devirtualizable.
    inline uint32_t raw_fnptr(uint8_t uid, uint32_t i)
    {
        if (uid > 2) return 0;
        const handler_t fn = handler_table[uid];
        return fn(i);
    }

    // ---------------------------------------------------------------- the etask path
    //
    // One task per tier per workload. The uid encodes both, so a single manager owns the whole
    // matrix and each case addresses exactly the task it means to measure.
    //
    // Every task's work is a call to the *same* work_* function the raw path uses. That is what
    // makes the delta attributable to the framework rather than to differently-written work.

    enum class task_id : uint8_t {
        // instant tier: 0x1_
        instant_state = 0x10, instant_light = 0x11, instant_heavy = 0x12,
        // oneshot (polled tier, finishes on the first tick): 0x2_
        oneshot_state = 0x20, oneshot_light = 0x21, oneshot_heavy = 0x22,
        // polled tier, runs for a fixed number of ticks: 0x3_
        polled_state  = 0x30, polled_light  = 0x31, polled_heavy  = 0x32,
        // stateful tier, same but pausable: 0x4_
        stateful_state = 0x40, stateful_light = 0x41, stateful_heavy = 0x42,
        // the tick-scaling sweep's task: one uid, many concurrent slots (see scale_case)
        scale = 0x50,
        // never registered; exists only to give a manager a budget (see ballast_case)
        ballast = 0x60,
    };

    /// Iteration counter handed to the tasks, so their work varies exactly as the raw path's does.
    volatile uint32_t task_input = 0;

    // -- instant tier: no vtable at all. The constructor *is* the task.
    template<task_id Uid, workload W>
    struct instant_case : instant_task {
        static constexpr task_id uid = Uid;
        explicit instant_case(etools::memory::buffer_view)
        {
            sink += run_workload(W, task_input);
        }
    };

    // -- oneshot: one execute, then finished. The cheapest managed lifecycle.
    template<task_id Uid, workload W>
    struct oneshot_case : polled_task<task_id> {
        static constexpr task_id uid = Uid;
        bool done = false;
        explicit oneshot_case(etools::memory::buffer_view) {}
        void on_execute() override { sink += run_workload(W, task_input); done = true; }
        bool is_finished() override { return done; }
        outcome on_complete(completion_reason) override { return {}; }
    };

    // -- polled: runs for `ticks_to_run` updates. Measures the steady-state tick, not the setup.
    constexpr uint32_t ticks_to_run = 1000000;  // effectively never finishes during a timed region

    template<task_id Uid, workload W>
    struct polled_case : polled_task<task_id> {
        static constexpr task_id uid = Uid;
        uint32_t remaining = ticks_to_run;
        explicit polled_case(etools::memory::buffer_view) {}
        void on_execute() override { sink += run_workload(W, task_input); --remaining; }
        bool is_finished() override { return remaining == 0; }
        outcome on_complete(completion_reason) override { return {}; }
    };

    // -- stateful: identical work, plus the pause/resume machinery in the manager's update loop.
    //    The delta against polled_case is the price of suspendability.
    template<task_id Uid, workload W>
    struct stateful_case : stateful_task<task_id> {
        static constexpr task_id uid = Uid;
        uint32_t remaining = ticks_to_run;
        explicit stateful_case(etools::memory::buffer_view) {}
        void on_execute() override { sink += run_workload(W, task_input); --remaining; }
        bool is_finished() override { return remaining == 0; }
        void on_pause() override {}
        void on_resume() override {}
        outcome on_complete(completion_reason) override { return {}; }
    };

    // -- the scaling task: one type, many concurrent instances.
    //
    // The tick-scaling sweep needs N *live* tasks, and each task type reserves one slot by
    // default - so a sweep over distinct types is bounded by how many types are declared, which is
    // what capped the earlier ladder at 2 points. `capacity<T, N>` reserves N slots for a single
    // type instead, so one uid can be registered N times over and the ladder is bounded by the
    // budget rather than by the type count.
    //
    // w0 work only: this row isolates the framework's per-task tick cost, and any real workload
    // would swamp it. The per-task cost of the work itself is already in case 2.
    struct scale_case : polled_task<task_id> {
        static constexpr task_id uid = task_id::scale;
        uint32_t remaining = ticks_to_run;
        explicit scale_case(etools::memory::buffer_view) {}
        void on_execute() override { sink += work_state(task_input); --remaining; }
        bool is_finished() override { return remaining == 0; }
        outcome on_complete(completion_reason) override { return {}; }
    };

    /// How many concurrent instances of `scale_case` the sweep can hold live at once.
    constexpr std::size_t scale_slots = 32;

    using instant_list = etools::meta::typelist<
        instant_case<task_id::instant_state, workload::state>,
        instant_case<task_id::instant_light, workload::light>,
        instant_case<task_id::instant_heavy, workload::heavy>>;

    using polled_list = etools::meta::typelist<
        oneshot_case<task_id::oneshot_state, workload::state>,
        oneshot_case<task_id::oneshot_light, workload::light>,
        oneshot_case<task_id::oneshot_heavy, workload::heavy>,
        polled_case<task_id::polled_state, workload::state>,
        polled_case<task_id::polled_light, workload::light>,
        polled_case<task_id::polled_heavy, workload::heavy>>;

    using stateful_list = etools::meta::typelist<
        stateful_case<task_id::stateful_state, workload::state>,
        stateful_case<task_id::stateful_light, workload::light>,
        stateful_case<task_id::stateful_heavy, workload::heavy>>;

    using manager_t = managers::task_manager_from_t<instant_list, polled_list, stateful_list>;

    manager_t manager{};
    channels::internal_channel<manager_t> channel{manager};

    // The scaling sweep gets its OWN manager, and this is load-bearing rather than tidiness.
    //
    // Both `update()` loops reset a `std::bitset<Budget>` and sweep the erase range every tick, so
    // part of the per-tick cost scales with the tier's *budget* - the compile-time slot count -
    // and not with how many tasks are actually live. Putting capacity<scale_case,32> into the
    // shared pack therefore raised the polled tier's budget to 38 against the stateful tier's 3,
    // and case 3's paired comparison silently stopped being like-for-like: it reported the
    // stateful tier as 8 ns *faster* than polled, which is not a thing that can be true of a tier
    // doing strictly more work per task.
    //
    // Keeping the sweep separate leaves cases 1-3 with the matched budgets they were written for,
    // and the budget-sensitivity itself is reported in RESULTS.md as a finding in its own right.
    using scale_manager_t = managers::task_manager_from_t<
        etools::meta::typelist<>,
        etools::meta::typelist<etools::factories::utils::capacity<scale_case, scale_slots>>,
        etools::meta::typelist<>>;

    scale_manager_t scale_manager{};
    channels::internal_channel<scale_manager_t> scale_channel{scale_manager};

    // ------------------------------------------------------------------- reporting

    uint64_t overhead_us = 0;

    /// Formats one paired row: raw cost, task cost, and the framework's share.
    void report_pair(const char* label, uint64_t raw_us, uint64_t task_us)
    {
        const double raw_ns  = ((raw_us  > overhead_us) ? (raw_us  - overhead_us) : 0) * 1000.0 / iterations;
        const double task_ns = ((task_us > overhead_us) ? (task_us - overhead_us) : 0) * 1000.0 / iterations;
        const double delta   = task_ns - raw_ns;
        // A ratio is only meaningful when the reference is measurable; below ~1 ns it is noise.
        const double ratio   = (raw_ns > 1.0) ? (task_ns / raw_ns) : 0.0;

        char raw_t[16], task_t[16], delta_t[16], ratio_t[16];
        dtostrf(raw_ns, 0, 1, raw_t);
        dtostrf(task_ns, 0, 1, task_t);
        dtostrf(delta, 0, 1, delta_t);
        if (ratio > 0.0) dtostrf(ratio, 0, 2, ratio_t); else strcpy(ratio_t, "n/a");

        char line[128];
        snprintf(line, sizeof(line), "  %-26s %9s %9s %9s %8s",
                 label, raw_t, task_t, delta_t, ratio_t);
        Serial.println(line);
    }

    void header(const char* title)
    {
        Serial.println();
        Serial.println(title);
        Serial.println("  case                             raw ns   task ns     delta    ratio");
        Serial.println("  -------------------------- ---------- --------- --------- --------");
    }

    /// Times the calibration loop: the exact scaffolding every measured loop below shares.
    void calibrate()
    {
        const uint64_t t0 = now_us();
        for (uint32_t i = 0; i < iterations; ++i) {
            task_input = i;
            sink += i;
        }
        overhead_us = now_us() - t0;
    }

    // ------------------------------------------------- case 1: dispatch (instant vs raw)
    //
    // An instant task is constructed, run, and destroyed inside the dispatch call. It declares no
    // virtuals, so this measures etask's *dispatch* - the uid fold in instant_task_manager plus a
    // non-virtual construction - against a hand-written switch. If the brief's guess is right,
    // this row is where etask looks closest to free.

    void measure_instant()
    {
        header("== instant task vs raw dispatch (no vtable, no storage, no reply) ==");

        const task_id uids[3] = { task_id::instant_state, task_id::instant_light, task_id::instant_heavy };
        const uint8_t raw_uids[3] = { 0, 1, 2 };

        for (int w = 0; w < 3; ++w) {
            // raw: switch + direct call
            uint64_t t0 = now_us();
            for (uint32_t i = 0; i < iterations; ++i) {
                task_input = i;
                sink += raw_switch(raw_uids[w], i);
            }
            const uint64_t raw_direct = now_us() - t0;

            // raw: switch + indirect call through a volatile table
            t0 = now_us();
            for (uint32_t i = 0; i < iterations; ++i) {
                task_input = i;
                sink += raw_fnptr(raw_uids[w], i);
            }
            const uint64_t raw_indirect = now_us() - t0;

            // etask: full manager dispatch
            t0 = now_us();
            for (uint32_t i = 0; i < iterations; ++i) {
                task_input = i;
                (void)manager.register_task(&channel, 1, uids[w], etools::memory::buffer_view{nullptr, 0});
                sink += i;
            }
            const uint64_t etask_us = now_us() - t0;

            char label[40];
            snprintf(label, sizeof(label), "%s [direct]", workload_name[w]);
            report_pair(label, raw_direct, etask_us);
            snprintf(label, sizeof(label), "%s [fnptr]", workload_name[w]);
            report_pair(label, raw_indirect, etask_us);
        }
    }

    // --------------------------------------- case 2: steady-state tick (polled vs raw loop)
    //
    // The number that decides whether a control loop fits its budget. One task is registered, then
    // `update()` is called in the timed region - so this is the per-tick cost of a live task
    // (virtual on_execute + virtual is_finished + the manager's bookkeeping) against a
    // hand-written loop doing the same work through a function pointer.

    void measure_polled_tick()
    {
        header("== polled task update() tick vs raw loop, 1 live task ==");

        const task_id uids[3] = { task_id::polled_state, task_id::polled_light, task_id::polled_heavy };

        for (int w = 0; w < 3; ++w) {
            // raw: what the same work costs called through an indirect pointer, no framework
            uint64_t t0 = now_us();
            for (uint32_t i = 0; i < iterations; ++i) {
                task_input = i;
                sink += raw_fnptr(static_cast<uint8_t>(w), i);
            }
            const uint64_t raw_us = now_us() - t0;

            // etask: one live task, driven by update()
            const status_code rc = manager.register_task(
                &channel, 1, uids[w], etools::memory::buffer_view{nullptr, 0});
            if (rc != status_code::ok) {
                Serial.print("  !! register failed for polled case, code ");
                Serial.println(static_cast<int>(rc));
                continue;
            }

            t0 = now_us();
            for (uint32_t i = 0; i < iterations; ++i) {
                task_input = i;
                manager.update();
                sink += i;
            }
            const uint64_t etask_us = now_us() - t0;

            (void)manager.complete_task(uids[w], completion_reason::aborted);
            manager.update();   // let the abort retire the task before the next case

            report_pair(workload_name[w], raw_us, etask_us);
        }
    }

    // ------------------------------- case 3: stateful vs polled (the price of suspendability)
    //
    // Identical work and identical tier shape; the only difference is the pause/resume state the
    // stateful manager carries and branches on each tick. Isolates that machinery's cost.

    void measure_stateful_tick()
    {
        header("== stateful vs polled tick (delta = cost of pause/resume machinery) ==");

        const task_id polled_uids[3]   = { task_id::polled_state, task_id::polled_light, task_id::polled_heavy };
        const task_id stateful_uids[3] = { task_id::stateful_state, task_id::stateful_light, task_id::stateful_heavy };

        for (int w = 0; w < 3; ++w) {
            uint64_t polled_us = 0, stateful_us = 0;

            for (int variant = 0; variant < 2; ++variant) {
                const task_id uid = (variant == 0) ? polled_uids[w] : stateful_uids[w];
                const status_code rc = manager.register_task(
                    &channel, 1, uid, etools::memory::buffer_view{nullptr, 0});
                if (rc != status_code::ok) {
                    Serial.print("  !! register failed, code ");
                    Serial.println(static_cast<int>(rc));
                    continue;
                }

                const uint64_t t0 = now_us();
                for (uint32_t i = 0; i < iterations; ++i) {
                    task_input = i;
                    manager.update();
                    sink += i;
                }
                const uint64_t elapsed = now_us() - t0;

                (void)manager.complete_task(uid, completion_reason::aborted);
                manager.update();

                if (variant == 0) polled_us = elapsed; else stateful_us = elapsed;
            }

            // Here the "raw" column is the polled tier, so the delta reads as the extra cost of
            // being suspendable rather than as framework overhead against hand-written code.
            report_pair(workload_name[w], polled_us, stateful_us);
        }
    }

    // ------------------------------------------- case 4: the tick scaling curve (per-task slope)
    //
    // The idle floor and the marginal per-task cost. Both are needed for the tick-budget
    // projection in RESULTS.md, and the slope is what says whether update() is O(1) or O(n).
    //
    // Run at w0 only: the point is the *framework's* per-task cost, and a heavy workload would
    // swamp it. The per-task work cost is already known from case 2.

    /// Times `iterations` calls to `update()` and returns the per-tick cost in ns, calibration
    /// already subtracted. Factored out because the scaling sweep calls it once per rung.
    double time_tick()
    {
        const uint64_t t0 = now_us();
        for (uint32_t i = 0; i < iterations; ++i) {
            task_input = i;
            scale_manager.update();
            sink += i;
        }
        const uint64_t elapsed = now_us() - t0;
        return ((elapsed > overhead_us) ? (elapsed - overhead_us) : 0) * 1000.0 / iterations;
    }

    void measure_tick_scaling()
    {
        Serial.println();
        Serial.println("== update() tick vs live task count (w0, framework cost only) ==");
        Serial.println("  All rungs are instances of ONE task type, registered into the slots its");
        Serial.println("  capacity<scale_case,32> reserves - so the ladder is bounded by the budget");
        Serial.println("  rather than by how many task types happen to be declared. This runs on a");
        Serial.println("  SEPARATE manager, so its 32-slot budget does not perturb cases 1-3.");
        Serial.println();
        Serial.println("  live tasks                     tick ns   per-task    marginal");
        Serial.println("  -------------------------- ---------- ---------- -----------");

        // Rungs to report. Intermediate registrations still happen; these are the points printed.
        const int rungs[] = { 0, 1, 2, 4, 8, 16, 32 };
        constexpr int rung_count = sizeof(rungs) / sizeof(rungs[0]);

        double first_ns = 0.0, prev_ns = 0.0;
        int prev_live = 0;
        int live = 0;

        for (int r = 0; r < rung_count; ++r) {
            // Register up to this rung's task count before timing it.
            while (live < rungs[r]) {
                if (scale_manager.register_task(&scale_channel, 1, task_id::scale,
                                                etools::memory::buffer_view{nullptr, 0})
                    != status_code::ok) {
                    Serial.print("  !! could not reach ");
                    Serial.print(rungs[r]);
                    Serial.println(" live tasks; stopping the ladder here.");
                    r = rung_count;   // stop the outer loop too
                    break;
                }
                ++live;
            }
            if (r >= rung_count) break;

            const double ns = time_tick();

            char t[16], per[16], marg[16];
            dtostrf(ns, 0, 1, t);
            // Per-task: the whole tick divided by the live count - what each task costs on
            // average, idle floor included.
            if (live > 0) dtostrf(ns / live, 0, 1, per); else strcpy(per, "-");
            // Marginal: the slope between this rung and the previous one. This is the figure a
            // tick budget extrapolates from, and the one that says whether update() is O(1) or
            // O(n) per task.
            if (r > 0 && live > prev_live)
                dtostrf((ns - prev_ns) / (live - prev_live), 0, 1, marg);
            else
                strcpy(marg, "-");

            char line[96];
            snprintf(line, sizeof(line), "  %-26d %10s %10s %11s", live, t, per, marg);
            Serial.println(line);

            if (r == 0) first_ns = ns;
            prev_ns = ns;
            prev_live = live;
        }

        // The overall slope across the whole measured range, which is what RESULTS.md quotes.
        // Reported alongside the per-rung marginals so a reader can see whether it is linear
        // rather than taking the average on trust.
        if (prev_live > 0) {
            char slope[16];
            dtostrf((prev_ns - first_ns) / prev_live, 0, 1, slope);
            Serial.println();
            Serial.print("  idle floor (0 live): ");
            char f[16]; dtostrf(first_ns, 0, 1, f);
            Serial.print(f);
            Serial.print(" ns   mean slope over 0..");
            Serial.print(prev_live);
            Serial.print(": ");
            Serial.print(slope);
            Serial.println(" ns/task");
        }
    }

    // ------------------------------- case 5: does an unused budget cost anything per tick?
    //
    // Found while investigating a nonsensical result in case 3: raising one tier's budget made its
    // ticks measurably slower even with the same number of tasks live. `update()` calls
    // `_garbage.reset()` on a `std::bitset<Budget>` and runs its erase sweep over the task range
    // every tick, so some of the per-tick cost tracks the compile-time slot count rather than the
    // live count.
    //
    // That matters to a user: `capacity<T, N>` and a generous `budget:` look free, and this says
    // what they actually cost when the slots sit empty. Measured with ZERO tasks live in each
    // manager, so the only difference between the rows is the budget itself.

    /// A task type used only to give a manager a budget; never registered.
    template<std::size_t Slot>
    struct ballast_case : polled_task<task_id> {
        static constexpr task_id uid = task_id::ballast;
        explicit ballast_case(etools::memory::buffer_view) {}
        void on_execute() override {}
        bool is_finished() override { return true; }
        outcome on_complete(completion_reason) override { return {}; }
    };

    template<std::size_t Budget>
    using ballast_manager_t = managers::task_manager_from_t<
        etools::meta::typelist<>,
        etools::meta::typelist<etools::factories::utils::capacity<ballast_case<Budget>, Budget>>,
        etools::meta::typelist<>>;

    /// Times an idle `update()` on a manager of the given budget, nothing live.
    template<std::size_t Budget>
    double idle_tick_for()
    {
        static ballast_manager_t<Budget> m{};
        const uint64_t t0 = now_us();
        for (uint32_t i = 0; i < iterations; ++i) {
            task_input = i;
            m.update();
            sink += i;
        }
        const uint64_t elapsed = now_us() - t0;
        return ((elapsed > overhead_us) ? (elapsed - overhead_us) : 0) * 1000.0 / iterations;
    }

    void measure_budget_cost()
    {
        Serial.println();
        Serial.println("== idle tick vs declared budget, ZERO tasks live ==");
        Serial.println("  What an unused slot costs every tick. Only the compile-time budget");
        Serial.println("  differs between these rows; every manager is empty.");
        Serial.println();
        Serial.println("  budget                        idle ns");
        Serial.println("  -------------------------- ----------");

        const std::size_t budgets[] = { 1, 8, 32, 128 };
        const double ns[] = {
            idle_tick_for<1>(), idle_tick_for<8>(),
            idle_tick_for<32>(), idle_tick_for<128>(),
        };

        for (int i = 0; i < 4; ++i) {
            char t[16]; dtostrf(ns[i], 0, 1, t);
            char line[96];
            snprintf(line, sizeof(line), "  %-26u %10s",
                     static_cast<unsigned>(budgets[i]), t);
            Serial.println(line);
        }

        Serial.println();
        Serial.println("  A flat column means an unused slot is free and a generous budget costs");
        Serial.println("  only RAM. A rising one means the idle floor is paid per declared slot.");
    }

} // namespace

void setup()
{
    Serial.begin(115200);
    while (!Serial) { /* wait for USB CDC on boards that need it */ }
    delay(300);

    Serial.println();
    Serial.println("=== etask runtime benchmark ===");
    Serial.print("iterations per case: ");
    Serial.println(iterations);
#if defined(ESP32)
    Serial.print("chip: ESP32 family, CPU MHz: ");
    Serial.println(getCpuFrequencyMhz());
#else
    Serial.println("chip: ESP8266");
#endif

    calibrate();
    Serial.print("loop overhead subtracted: ");
    Serial.print(static_cast<uint32_t>(overhead_us));
    Serial.println(" us total");
    Serial.println();
    Serial.println("Columns: 'raw' = hand-written dispatch, 'task' = via etask,");
    Serial.println("'delta' = framework cost, 'ratio' = task/raw.");

    measure_instant();
    measure_polled_tick();
    measure_stateful_tick();
    measure_tick_scaling();
    measure_budget_cost();

    Serial.println();
    Serial.print("checksum (ignore): ");
    Serial.println(static_cast<uint32_t>(sink));
    Serial.println("=== done ===");
}

void loop() {}

#endif // BENCH_HEAP
