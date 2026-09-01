/**
* @file main.cpp
*
* @brief Static-footprint ladder: one translation unit, one feature tier per build.
*
* @ingroup etask_bench
*
* Compiled once per `-D BENCH_TIER=n`. Consecutive tiers differ by exactly one feature, so
* subtracting their ELF section sizes gives that feature's incremental flash and RAM cost.
*
* Two independent ladders live here:
*
*  - **Feature ladder** (`BENCH_TIER` 0..8): what each layer of etask costs to add. Tier 1 is the
*    honesty check - etask claims header-only, so including it while instantiating nothing must
*    cost 0 bytes.
*  - **Task-count ladder** (`BENCH_TASKS=n` at tier 5): the marginal cost of one more registered
*    task. This is the number that answers "how does it scale", and the static suite for eser had
*    no equivalent.
*
* Every tier folds its work into a `volatile` sink and takes input from a `volatile` source. A tier
* whose result is unused is dead code the linker removes, which would report the feature as free.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-27
*
* @copyright
* MIT License
* SPDX-License-Identifier: MIT
*/
#include <Arduino.h>

#ifndef BENCH_TIER
#define BENCH_TIER 0
#endif

/// How many tasks the task-count ladder registers. Only read at tier 5.
#ifndef BENCH_TASKS
#define BENCH_TASKS 1
#endif

namespace {
    /// Sink the optimizer cannot prove unused: without it every tier below is dead code.
    volatile uint32_t sink = 0;
    /// Varying input, so no tier's work can be constant-folded at compile time.
    volatile uint32_t source = 0;
}

// ---------------------------------------------------------------------------------- tier 1+
// Inclusion only. etask is header-only, so this must add exactly 0 bytes over tier 0.
#if BENCH_TIER >= 1
#include <etask/core/core.hpp>
#include <etools/meta/typelist.hpp>
#include <cstdint>

using namespace etask::core;
#endif

// ---------------------------------------------------------------------------------- tier 2+
// The task set. Declared from tier 2 up; which of them are instantiated is what the tiers vary.
#if BENCH_TIER >= 2
namespace {

    enum class task_id : std::uint8_t {
        i0 = 0x10, i1, i2, i3, i4, i5, i6, i7,
        i8 = 0x18, i9, i10, i11, i12, i13, i14, i15,
        i16 = 0x20, i17, i18, i19, i20, i21, i22, i23,
        i24 = 0x28, i25, i26, i27, i28, i29, i30, i31,
        p0 = 0x50, s0 = 0x60,
    };

    /// A fire-and-forget command. No vtable; the constructor is the whole task.
    template<task_id Uid>
    struct cmd : instant_task {
        static constexpr task_id uid = Uid;
        explicit cmd(etools::memory::buffer_view) { sink += static_cast<std::uint32_t>(Uid); }
    };

    /// A polled task: two virtuals plus a completion.
    template<task_id Uid>
    struct poll : polled_task<task_id> {
        static constexpr task_id uid = Uid;
        std::uint32_t left = 4;
        explicit poll(etools::memory::buffer_view) {}
        void on_execute() override { sink += source; --left; }
        bool is_finished() override { return left == 0; }
        outcome on_complete(completion_reason) override { return {}; }
    };

    /// A stateful task: the polled hooks plus pause/resume.
    template<task_id Uid>
    struct hold : stateful_task<task_id> {
        static constexpr task_id uid = Uid;
        std::uint32_t left = 4;
        explicit hold(etools::memory::buffer_view) {}
        void on_execute() override { sink += source; --left; }
        bool is_finished() override { return left == 0; }
        void on_pause() override { sink += 1; }
        void on_resume() override { sink += 2; }
        outcome on_complete(completion_reason) override { return {}; }
    };

} // namespace
#endif

// ------------------------------------------------------------- tier composition
//
// Each tier names one manager configuration. An empty tier list instantiates nothing for that
// tier - which is itself a measurable claim, so the tiers add one manager at a time.

#if BENCH_TIER == 2
// Tier 2: a manager holding exactly one instant command - the smallest live manager.
namespace { using instant_l  = etools::meta::typelist<cmd<task_id::i0>>;
            using polled_l   = etools::meta::typelist<>;
            using stateful_l = etools::meta::typelist<>; }

#elif BENCH_TIER == 3
// Tier 3: + a second instant command. Delta = marginal cost of one instant task.
namespace { using instant_l  = etools::meta::typelist<cmd<task_id::i0>, cmd<task_id::i1>>;
            using polled_l   = etools::meta::typelist<>;
            using stateful_l = etools::meta::typelist<>; }

#elif BENCH_TIER == 4
// Tier 4: + the polled tier. Delta = the whole polled manager: vector, bitset, dispatch_factory,
// and the virtual call machinery.
namespace { using instant_l  = etools::meta::typelist<cmd<task_id::i0>, cmd<task_id::i1>>;
            using polled_l   = etools::meta::typelist<poll<task_id::p0>>;
            using stateful_l = etools::meta::typelist<>; }

#elif BENCH_TIER >= 5
// Tier 5: + the stateful tier. All three managers live - the full framework.
// This is also the tier the task-count ladder sweeps, via BENCH_TASKS.
namespace {

    // The instant tier is what the count ladder grows: an instant task is the cheapest kind, so
    // the slope isolates registration cost rather than lifecycle cost.
    #if BENCH_TASKS >= 32
    using instant_l = etools::meta::typelist<
        cmd<task_id::i0>,  cmd<task_id::i1>,  cmd<task_id::i2>,  cmd<task_id::i3>,
        cmd<task_id::i4>,  cmd<task_id::i5>,  cmd<task_id::i6>,  cmd<task_id::i7>,
        cmd<task_id::i8>,  cmd<task_id::i9>,  cmd<task_id::i10>, cmd<task_id::i11>,
        cmd<task_id::i12>, cmd<task_id::i13>, cmd<task_id::i14>, cmd<task_id::i15>,
        cmd<task_id::i16>, cmd<task_id::i17>, cmd<task_id::i18>, cmd<task_id::i19>,
        cmd<task_id::i20>, cmd<task_id::i21>, cmd<task_id::i22>, cmd<task_id::i23>,
        cmd<task_id::i24>, cmd<task_id::i25>, cmd<task_id::i26>, cmd<task_id::i27>,
        cmd<task_id::i28>, cmd<task_id::i29>, cmd<task_id::i30>, cmd<task_id::i31>>;
    #elif BENCH_TASKS >= 16
    using instant_l = etools::meta::typelist<
        cmd<task_id::i0>,  cmd<task_id::i1>,  cmd<task_id::i2>,  cmd<task_id::i3>,
        cmd<task_id::i4>,  cmd<task_id::i5>,  cmd<task_id::i6>,  cmd<task_id::i7>,
        cmd<task_id::i8>,  cmd<task_id::i9>,  cmd<task_id::i10>, cmd<task_id::i11>,
        cmd<task_id::i12>, cmd<task_id::i13>, cmd<task_id::i14>, cmd<task_id::i15>>;
    #elif BENCH_TASKS >= 8
    using instant_l = etools::meta::typelist<
        cmd<task_id::i0>, cmd<task_id::i1>, cmd<task_id::i2>, cmd<task_id::i3>,
        cmd<task_id::i4>, cmd<task_id::i5>, cmd<task_id::i6>, cmd<task_id::i7>>;
    #elif BENCH_TASKS >= 4
    using instant_l = etools::meta::typelist<
        cmd<task_id::i0>, cmd<task_id::i1>, cmd<task_id::i2>, cmd<task_id::i3>>;
    #elif BENCH_TASKS >= 2
    using instant_l = etools::meta::typelist<cmd<task_id::i0>, cmd<task_id::i1>>;
    #else
    using instant_l = etools::meta::typelist<cmd<task_id::i0>>;
    #endif

    using polled_l   = etools::meta::typelist<poll<task_id::p0>>;
    using stateful_l = etools::meta::typelist<hold<task_id::s0>>;
}
#endif

// ---------------------------------------------------------------- the manager instance
#if BENCH_TIER >= 2
namespace {
    using manager_t = managers::task_manager_from_t<instant_l, polled_l, stateful_l>;
    manager_t manager{};
}
#endif

// ---------------------------------------------------------------------------------- tier 6+
// The internal channel: in-process origin for tasks this node starts itself.
#if BENCH_TIER >= 6
namespace { channels::internal_channel<manager_t> internal{manager}; }
#endif

// ---------------------------------------------------------------------------------- tier 7+
// The external channel, which pulls in the ecomm packet type and the eser codec behind it. This
// is the tier that measures the wire protocol rather than the task machinery.
#if BENCH_TIER >= 7
#include <ecomm/protocol/protocol.hpp>
#include <optional>

namespace {

    /// The same shape the WiFi harness uses: 32-byte network-addressed frame, no checksum (TCP
    /// already guarantees integrity, so a CRC here would measure ecomm's checksum rather than
    /// etask's channel). `network` topology carries sender/receiver ids, which external_channel
    /// needs to address a reply back to the PC.
    using packet_t = ecomm::protocol::packet<
        32,
        ecomm::protocol::topology::network,
        ecomm::protocol::no_sequence,
        ecomm::protocol::none>;

    /// Minimal transport: satisfies the Hub contract without depending on real hardware, so this
    /// tier measures the channel and packet layers rather than a WiFi stack.
    struct null_hub {
        bool send(const packet_t& p) { sink += std::to_integer<std::uint32_t>(p.payload[0]); return true; }
        template<typename P> std::optional<P> try_receive() { return std::nullopt; }
    };

    /// What `external_channel` is instantiated on, written by hand because this
    /// benchmark has no schema and so no `generated/links.hpp` to take it from.
    /// A generated link's `traits` has exactly these members; the shape is the
    /// contract, not the file it usually comes from.
    ///
    /// `carries` returns true unconditionally, matching what the generator emits
    /// for a link that declares no `subsystems:` - a per-uid allowlist would be
    /// measuring the allowlist rather than the channel.
    struct bench_link {
        using request_packet_t = packet_t;
        using reply_packet_t = packet_t;

        static constexpr std::uint64_t fingerprint =
            etask::core::protocol::no_fingerprint;

        /// The directive byte plus the uid; no task here takes arguments.
        static constexpr std::size_t request_payload_need =
            sizeof(std::byte) + sizeof(task_id);
        /// The uid plus the status byte; no task here returns a result.
        static constexpr std::size_t reply_payload_need =
            sizeof(task_id) + sizeof(std::byte);

        static constexpr bool carries(std::underlying_type_t<task_id>) noexcept
        {
            return true;
        }
    };

    null_hub hub{};
    channels::external_channel<bench_link, null_hub, manager_t> external{hub, manager};
}
#endif

// ---------------------------------------------------------------------------------- main
void setup()
{
    Serial.begin(115200);

#if BENCH_TIER >= 2
    // Exercising the manager keeps it (and every tier below) out of the linker's dead-code pass.
    // A manager that is only *constructed* can have most of its code stripped, which would report
    // the tier as far cheaper than it is.
    sink += static_cast<std::uint32_t>(
        manager.register_task(nullptr, 1, task_id::i0, etools::memory::buffer_view{nullptr, 0}));
    manager.update();
#endif

#if BENCH_TIER >= 6
    sink += static_cast<std::uint32_t>(
        internal.register_task(task_id::p0, etools::memory::buffer_view{nullptr, 0}));
#endif

#if BENCH_TIER >= 7
    external.update();

    // Register every uid the ladder declared, not just the two above. A task's
    // *unpacking adapter* is only given a vtable and a typeinfo if something
    // reaches its entry in the registry, so a sweep that registers one uid
    // leaves the rest as inlined constructors with no polymorphic footprint -
    // and the footprint is what this ladder exists to measure. Registering
    // through the whole uid space is the cheapest way to be sure none is
    // dead-stripped; the failures are counted rather than ignored so the
    // compiler cannot discard the calls.
    for (unsigned uid = 0; uid <= 0xFF; ++uid) {
        sink += static_cast<std::uint32_t>(
            internal.register_task(static_cast<task_id>(uid),
                                   etools::memory::buffer_view{nullptr, 0}));
        manager.update();
    }
#endif

    Serial.println(static_cast<unsigned>(sink));
}

void loop() {}
