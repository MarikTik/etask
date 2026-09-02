/**
* @file heap.cpp
*
* @brief Heap track: the claim that etask allocates nothing, put to the test on real hardware.
*
* @ingroup etask_bench
*
* Built instead of main.cpp when `-D BENCH_HEAP` is set (see platformio.ini's `heap_*` envs), so
* the two measurements never perturb each other.
*
* ## What this track measures, and why it changed
*
* It used to measure three costs of a heap-backed design: a startup allocation, the fragmentation
* it left behind, and a *reallocation cliff* - registering more concurrent tasks than
* `max_task_load` forced `std::vector` to grow, and that growth was a real mid-flight `malloc` on
* a heap that by then held the WiFi stack.
*
* **None of those exist any more.** Both managers now hold
* `etools::memory::static_vector<task_info, Budget>`, whose storage is an inline
* `alignas(T) std::byte[Capacity * sizeof(T)]` member. The budget is a template parameter fixed at
* compile time, `task_manager`'s constructor is `= default` and takes no arguments, and there is no
* growth path to fall off. Task objects live in `dispatch_factory`'s in-place `std::optional`
* slots, which were never heap either.
*
* So the honest characterization is now: **etask allocates nothing, ever.** That is a stronger
* claim than the old design could make, and a claim is worth exactly as much as its test - which
* is why this file still exists rather than being deleted. It verifies:
*
*   1. **Construction allocates nothing.** Free heap must not move across building a manager and
*      an internal channel. Under the old design this was two `reserve()` calls.
*   2. **Steady-state traffic allocates nothing.** 400 register/retire cycles must not move the
*      heap - the property that makes cost scale with the declared task set rather than with how
*      many requests arrive.
*   3. **Nothing is leaked**, trivially, since nothing is taken.
*   4. **Budget exhaustion is a clean refusal, not a reallocation.** What replaced the cliff:
*      registering past `Budget` returns `task_budget_exhausted` and leaves the heap untouched.
*      A full manager now fails predictably at the call site instead of quietly mallocing.
*
* Every stage prints its free-heap delta whether or not it is zero, so a regression shows up as a
* number rather than as a silently absent row.
*
* @note ESP8266 reports `getFreeHeap`/`getMaxFreeBlockSize`; ESP32 reports `esp_get_free_heap_size`
*       and `heap_caps_get_largest_free_block`. Both are read through one pair of helpers below.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-27
*
* @copyright
* MIT License
* SPDX-License-Identifier: MIT
*/
// Only this file OR main.cpp compiles into a given firmware: both define setup()/loop().
// platformio.ini sets -D BENCH_HEAP for the heap_* envs and leaves it unset otherwise.
#ifdef BENCH_HEAP

#include <Arduino.h>
#include <etask/core/core.hpp>
#include <etools/meta/typelist.hpp>
#include <cstdint>

#if defined(ESP32)
  #include <esp_heap_caps.h>
#endif

using namespace etask::core;

namespace {

    volatile std::uint32_t sink = 0;

    /// Free heap, in bytes, from whichever API this target offers.
    std::uint32_t free_heap()
    {
    #if defined(ESP32)
        return static_cast<std::uint32_t>(esp_get_free_heap_size());
    #else
        return static_cast<std::uint32_t>(ESP.getFreeHeap());
    #endif
    }

    /// Largest single allocatable block. Free heap minus this is the fragmentation gap: a heap
    /// with plenty free but no large block will still fail a big allocation.
    std::uint32_t largest_block()
    {
    #if defined(ESP32)
        return static_cast<std::uint32_t>(heap_caps_get_largest_free_block(MALLOC_CAP_8BIT));
    #else
        return static_cast<std::uint32_t>(ESP.getMaxFreeBlockSize());
    #endif
    }

    enum class task_id : std::uint8_t {
        p0 = 0x30, p1, p2, p3, p4, p5, p6, p7,
        s0 = 0x40,
    };

    template<task_id Uid>
    struct poll : polled_task<task_id> {
        static constexpr task_id uid = Uid;
        bool done = false;
        explicit poll(etools::memory::buffer_view) {}
        void on_execute() override { sink += 1; done = true; }
        bool is_finished() override { return done; }
        outcome on_complete(completion_reason) override { return {}; }
    };

    struct hold : stateful_task<task_id> {
        static constexpr task_id uid = task_id::s0;
        bool done = false;
        explicit hold(etools::memory::buffer_view) {}
        void on_execute() override { sink += 1; done = true; }
        bool is_finished() override { return done; }
        void on_pause() override {}
        void on_resume() override {}
        outcome on_complete(completion_reason) override { return {}; }
    };

    using polled_pack = etools::meta::typelist<
        poll<task_id::p0>, poll<task_id::p1>, poll<task_id::p2>, poll<task_id::p3>,
        poll<task_id::p4>, poll<task_id::p5>, poll<task_id::p6>, poll<task_id::p7>>;

    /// Budgets left to default: each tier sizes itself to the sum of its per-task caps.
    using manager_t = managers::task_manager_from_t<
        etools::meta::typelist<>, polled_pack, etools::meta::typelist<hold>>;

    /// The same task set with the polled tier deliberately under-budgeted to 2 concurrent tasks.
    /// Registering a third must be refused rather than accommodated - the test that replaced the
    /// old reallocation cliff.
    using tight_manager_t = managers::task_manager_from_t<
        etools::meta::typelist<>, polled_pack, etools::meta::typelist<hold>, 2, 1>;

    void row(const char* label, std::uint32_t free_now, std::uint32_t block_now,
             std::uint32_t free_ref)
    {
        char line[128];
        const long delta = static_cast<long>(free_now) - static_cast<long>(free_ref);
        snprintf(line, sizeof(line), "  %-34s %8lu %+9ld %10lu %9lu",
                 label,
                 static_cast<unsigned long>(free_now),
                 delta,
                 static_cast<unsigned long>(block_now),
                 static_cast<unsigned long>(free_now - block_now));
        Serial.println(line);
    }

    void header()
    {
        Serial.println();
        Serial.println("  stage                              free B    delta B   largest B   frag B");
        Serial.println("  ---------------------------------- ------- ---------- ----------- --------");
    }

    /// Prints PASS or the offending delta. Used for every "must not move" claim, so a regression
    /// reads as a number rather than as an absent line.
    void check(const char* claim, std::uint32_t before, std::uint32_t after)
    {
        if (after == before) {
            Serial.print("  PASS  ");
            Serial.println(claim);
        } else {
            Serial.print("  FAIL  ");
            Serial.print(claim);
            Serial.print(" - heap moved by ");
            Serial.print(static_cast<long>(after) - static_cast<long>(before));
            Serial.println(" B");
        }
    }

} // namespace

void setup()
{
    Serial.begin(115200);
    while (!Serial) {}
    delay(300);

    Serial.println();
    Serial.println("=== etask heap track ===");
    Serial.println();
    Serial.println("etask holds task records in etools::memory::static_vector<task_info, Budget>,");
    Serial.println("whose storage is an inline byte array sized at compile time. There is no heap");
    Serial.println("path at all, so every delta below must be exactly 0. 'frag B' is free-minus-");
    Serial.println("largest-block: how much free heap is unusable for one big allocation.");
    Serial.print("sizeof(manager_t): ");
    Serial.print(static_cast<unsigned long>(sizeof(manager_t)));
    Serial.println(" B, held inline - this is RAM, not heap.");

    const std::uint32_t baseline = free_heap();
    header();
    row("baseline (before manager)", baseline, largest_block(), baseline);

    // ---- 1. construction ------------------------------------------------------------------
    // Scoped, so destruction can be measured too - a leak would show as a permanent delta after
    // the scope exits.
    {
        manager_t manager{};
        const std::uint32_t after_ctor = free_heap();
        row("manager constructed", after_ctor, largest_block(), baseline);

        channels::internal_channel<manager_t> channel{manager};
        const std::uint32_t after_channel = free_heap();
        row("+ internal channel", after_channel, largest_block(), baseline);

        // ---- 2. steady state --------------------------------------------------------------
        // The claim under test: registering and retiring tasks must not move the heap, so cost
        // scales with the declared task set rather than with traffic.
        const std::uint32_t before_traffic = free_heap();

        const task_id uids[8] = { task_id::p0, task_id::p1, task_id::p2, task_id::p3,
                                  task_id::p4, task_id::p5, task_id::p6, task_id::p7 };
        for (int cycle = 0; cycle < 50; ++cycle) {
            for (const task_id uid : uids) {
                sink += static_cast<std::uint32_t>(
                    manager.register_task(&channel, 1, uid,
                                          etools::memory::buffer_view{nullptr, 0}));
            }
            manager.update();   // each poll task finishes on its first tick and is retired
        }

        const std::uint32_t after_traffic = free_heap();
        row("after 400 register/retire cycles", after_traffic, largest_block(), baseline);

        Serial.println();
        check("construction allocated nothing", baseline, after_channel);
        check("steady-state traffic allocated nothing", before_traffic, after_traffic);
        header();
    }

    const std::uint32_t after_scope = free_heap();
    row("manager destroyed", after_scope, largest_block(), baseline);
    Serial.println();
    check("no leak across the manager's lifetime", baseline, after_scope);

    // ---- 3. budget exhaustion, which replaced the reallocation cliff -----------------------
    // The old design grew its vector here, mallocing mid-flight on a heap that by then held the
    // WiFi stack - the one heap behaviour that could fail at runtime. A fixed budget cannot grow,
    // so the interesting question became what it does instead: it must refuse cleanly, and it must
    // not touch the heap while refusing.
    Serial.println();
    Serial.println("== budget exhaustion (polled budget = 2, eight tasks offered) ==");
    Serial.println("  What replaced the reallocation cliff. A fixed budget cannot grow, so the");
    Serial.println("  question is whether it refuses cleanly - and refuses without allocating.");
    header();
    {
        const std::uint32_t before = free_heap();
        tight_manager_t tight{};
        channels::internal_channel<tight_manager_t> channel{tight};
        row("manager<budget=2> constructed", free_heap(), largest_block(), before);

        const task_id uids[8] = { task_id::p0, task_id::p1, task_id::p2, task_id::p3,
                                  task_id::p4, task_id::p5, task_id::p6, task_id::p7 };
        int accepted = 0, refused = 0;
        status_code last = status_code::ok;
        for (const task_id uid : uids) {
            const status_code rc =
                tight.register_task(&channel, 1, uid, etools::memory::buffer_view{nullptr, 0});
            if (rc == status_code::ok) ++accepted; else { ++refused; last = rc; }
            sink += static_cast<std::uint32_t>(rc);
        }
        const std::uint32_t after = free_heap();
        row("after offering 8", after, largest_block(), before);

        Serial.println();
        Serial.print("  accepted ");
        Serial.print(accepted);
        Serial.print(", refused ");
        Serial.print(refused);
        Serial.print(" with status 0x");
        Serial.print(static_cast<int>(last), HEX);
        Serial.println(" (0x18 = task_budget_exhausted)");
        check("refusal allocated nothing", before, after);
        if (accepted == 2)
            Serial.println("  PASS  the budget was honored exactly: 2 accepted, the rest refused.");
        else {
            Serial.print("  FAIL  expected 2 accepted, got ");
            Serial.println(accepted);
        }
    }

    Serial.println();
    Serial.print("checksum (ignore): ");
    Serial.println(static_cast<unsigned long>(sink));
    Serial.println("=== done ===");
}

void loop() {}

#endif // BENCH_HEAP
