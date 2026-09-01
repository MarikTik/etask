/**
* @file heap.cpp
*
* @brief Heap track: what etask allocates, when, and how fragmented it leaves the heap.
*
* @ingroup etask_bench
*
* Built instead of main.cpp when `-D BENCH_HEAP` is set (see platformio.ini's `heap_*` envs), so
* the two measurements never perturb each other.
*
* ## What is actually on the heap
*
* etask has exactly **two** dynamic allocations, and it is worth being precise about them because
* "the managers use heap" is easy to read as worse than it is:
*
*   - `polled_task_manager::_tasks`   - `std::vector<task_info>`
*   - `stateful_task_manager::_tasks` - `std::vector<task_info>`
*
* Both are `reserve()`d **once, in the manager's constructor**, to `max_task_load` (default: the
* sum of every task's declared concurrency). Registering and completing tasks after that is
* `emplace_back` / `erase` **within the reserved capacity** - no reallocation, no per-task malloc.
* Task objects themselves live in `dispatch_factory`'s in-place `std::optional` slots, which are
* not heap at all.
*
* So the honest characterization is: **two allocations at construction, then a steady state.** The
* costs that remain, and that this file measures:
*
*   1. **Startup allocation** - two blocks whose size scales with the task count. Measured as
*      free-heap delta across construction.
*   2. **Fragmentation** - those two blocks are allocated early and never freed, which is the
*      benign case; but they are sized by `max_task_load`, so an over-declared load wastes RAM
*      permanently. Measured as the gap between free heap and largest free block.
*   3. **The reallocation cliff** - if a project registers more concurrent tasks than
*      `max_task_load`, the vector grows and *does* malloc mid-flight, on a heap that by then holds
*      the WiFi stack. Measured explicitly, because it is the one case that can fail at runtime.
*
* A static `std::array`-backed manager would remove all three; this file is the measurement that
* says how much that is worth.
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

    using manager_t = managers::task_manager_from_t<
        etools::meta::typelist<>,
        etools::meta::typelist<poll<task_id::p0>, poll<task_id::p1>, poll<task_id::p2>,
                               poll<task_id::p3>, poll<task_id::p4>, poll<task_id::p5>,
                               poll<task_id::p6>, poll<task_id::p7>>,
        etools::meta::typelist<hold>>;

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

} // namespace

void setup()
{
    Serial.begin(115200);
    while (!Serial) {}
    delay(300);

    Serial.println();
    Serial.println("=== etask heap track ===");
    Serial.println();
    Serial.println("etask's only dynamic allocations are two std::vector<task_info> - one in the");
    Serial.println("polled manager, one in the stateful - each reserve()d ONCE at construction.");
    Serial.println("'frag B' is free-minus-largest-block: how much free heap is unusable for one");
    Serial.println("big allocation.");

    const std::uint32_t baseline = free_heap();
    header();
    row("baseline (before manager)", baseline, largest_block(), baseline);

    // ---- 1. startup allocation ------------------------------------------------------------
    // Scoped, so the manager's destruction can be measured too - a leak would show as a
    // permanent delta after the scope exits.
    {
        // Default construction reserves total_capacity (9 here: 8 polled + 1 stateful).
        manager_t manager{};
        const std::uint32_t after_ctor = free_heap();
        row("manager constructed (reserve)", after_ctor, largest_block(), baseline);

        channels::internal_channel<manager_t> channel{manager};
        row("+ internal channel", free_heap(), largest_block(), baseline);

        // ---- 2. steady state: register and retire, within reserved capacity ----------------
        // The claim under test: this must NOT move the heap. Any delta here means a task
        // registration is allocating, which would make cost scale with traffic rather than with
        // the declared task set.
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
        if (after_traffic == before_traffic) {
            Serial.println("  PASS  steady-state traffic allocated nothing: registration reuses the");
            Serial.println("        reserved capacity, so heap cost scales with the declared task");
            Serial.println("        set, not with how many requests arrive.");
        } else {
            Serial.print("  NOTE  steady-state traffic moved the heap by ");
            Serial.print(static_cast<long>(after_traffic) - static_cast<long>(before_traffic));
            Serial.println(" B - registration is allocating.");
        }
        header();
    }

    const std::uint32_t after_scope = free_heap();
    row("manager destroyed", after_scope, largest_block(), baseline);
    Serial.println();
    if (after_scope >= baseline) {
        Serial.println("  PASS  heap fully returned; no leak across the manager's lifetime.");
    } else {
        Serial.print("  NOTE  ");
        Serial.print(baseline - after_scope);
        Serial.println(" B not returned after the manager was destroyed.");
    }

    // ---- 3. the reallocation cliff ---------------------------------------------------------
    // A manager told to expect fewer concurrent tasks than it is given. The vector must grow, and
    // that growth is a real mid-flight malloc. This is the one heap behaviour that can fail at
    // runtime on a fragmented heap, so it is measured rather than assumed away.
    Serial.println();
    Serial.println("== the reallocation cliff: max_task_load under-declared ==");
    header();
    {
        const std::uint32_t before = free_heap();
        // Reserve for 2, then register 8. Growth is forced.
        manager_t tight{2};
        channels::internal_channel<manager_t> channel{tight};
        row("manager{2} constructed", free_heap(), largest_block(), before);

        const task_id uids[8] = { task_id::p0, task_id::p1, task_id::p2, task_id::p3,
                                  task_id::p4, task_id::p5, task_id::p6, task_id::p7 };
        for (const task_id uid : uids) {
            sink += static_cast<std::uint32_t>(
                tight.register_task(&channel, 1, uid, etools::memory::buffer_view{nullptr, 0}));
        }
        row("after registering 8 (grew)", free_heap(), largest_block(), before);
        Serial.println();
        Serial.println("  A delta here is the vector reallocating past its reserve. It is avoidable:");
        Serial.println("  declare max_task_load >= peak concurrent tasks, which is the default.");
    }

    Serial.println();
    Serial.print("checksum (ignore): ");
    Serial.println(static_cast<unsigned long>(sink));
    Serial.println("=== done ===");
}

void loop() {}

#endif // BENCH_HEAP
