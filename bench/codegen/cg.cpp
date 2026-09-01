/**
* @file cg.cpp
*
* @brief Instruction-count comparisons: etask dispatch and tick, against hand-written equivalents.
*
* @ingroup etask_bench
*
* Compiled and disassembled by bench/scripts/codegen.sh. Every comparison is a pair of
* `extern "C"` functions doing the *same* work, reached two ways - so the instruction-count delta
* is attributable to the framework and nothing else.
*
* `extern "C"` matters twice over: it prevents name mangling (so the disassembly can be sliced by
* symbol) and it prevents the functions being inlined away into nothing, which would report every
* comparison as free.
*
* The work in every case is a single store to a volatile cell. That is deliberate: this file
* measures *dispatch*, and any real workload would dominate the count and hide the thing being
* compared. The runtime suite covers real workloads.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-27
*
* @copyright
* MIT License
* SPDX-License-Identifier: MIT
*/
#include <etask/core/core.hpp>
#include <etools/meta/typelist.hpp>
#include <etools/factories/dispatch_factory.hpp>
#include <cstdint>

using namespace etask::core;

namespace {
    /// The work: one volatile store. Identical on both sides of every comparison.
    volatile std::uint32_t cell = 0;

    enum class tid : std::uint8_t {
        t0 = 0, t1, t2, t3, t4, t5, t6, t7,
        t8, t9, t10, t11, t12, t13, t14, t15,
        p0 = 100,
    };

    // ------------------------------------------------------ instant tier: etask vs a switch

    template<tid Uid>
    struct cmd : instant_task {
        static constexpr tid uid = Uid;
        explicit cmd(etools::memory::buffer_view) { cell = static_cast<std::uint32_t>(Uid); }
    };

    using list4 = etools::meta::typelist<cmd<tid::t0>, cmd<tid::t1>, cmd<tid::t2>, cmd<tid::t3>>;

    using list16 = etools::meta::typelist<
        cmd<tid::t0>,  cmd<tid::t1>,  cmd<tid::t2>,  cmd<tid::t3>,
        cmd<tid::t4>,  cmd<tid::t5>,  cmd<tid::t6>,  cmd<tid::t7>,
        cmd<tid::t8>,  cmd<tid::t9>,  cmd<tid::t10>, cmd<tid::t11>,
        cmd<tid::t12>, cmd<tid::t13>, cmd<tid::t14>, cmd<tid::t15>>;

    managers::instant_task_manager<
        cmd<tid::t0>, cmd<tid::t1>, cmd<tid::t2>, cmd<tid::t3>> mgr4{};

    managers::instant_task_manager<
        cmd<tid::t0>,  cmd<tid::t1>,  cmd<tid::t2>,  cmd<tid::t3>,
        cmd<tid::t4>,  cmd<tid::t5>,  cmd<tid::t6>,  cmd<tid::t7>,
        cmd<tid::t8>,  cmd<tid::t9>,  cmd<tid::t10>, cmd<tid::t11>,
        cmd<tid::t12>, cmd<tid::t13>, cmd<tid::t14>, cmd<tid::t15>> mgr16{};

    // ------------------------------------------------------------ polled tier: tick comparison

    struct poll_one : polled_task<tid> {
        static constexpr tid uid = tid::p0;
        explicit poll_one(etools::memory::buffer_view) {}
        void on_execute() override { cell = 1; }
        bool is_finished() override { return false; }
        outcome on_complete(completion_reason) override { return {}; }
    };

    managers::polled_task_manager<poll_one> poll_mgr{};

    /// The hand-written reference for a tick: one indirect call through a table the compiler
    /// cannot fold into a direct call, which is the same constraint a virtual call works under.
    using handler_t = void (*)();
    void handler_impl() { cell = 1; }
    handler_t volatile handler_slot = &handler_impl;

    // ------------------------------------------- dispatch_factory: emplace vs a switch

    struct base_t {
        virtual ~base_t() = default;
        virtual void run() = 0;
    };

    template<std::uint8_t Key>
    struct leaf : base_t {
        static constexpr std::uint8_t key = Key;
        leaf() = default;
        void run() override { cell = Key; }
    };

    template<typename T>
    struct key_of { static constexpr auto value = T::key; };

    using factory_t = etools::factories::dispatch_factory<
        base_t, key_of,
        leaf<0>, leaf<1>, leaf<2>, leaf<3>, leaf<4>, leaf<5>, leaf<6>, leaf<7>>;

    factory_t factory{};

    /// Storage for the hand-written emplace reference: the same "construct in place, run it"
    /// shape the factory provides, written out by hand.
    alignas(8) unsigned char raw_storage[64];

} // namespace

// ============================================================== 1. instant dispatch, 4 tasks

extern "C" int hand_dispatch_4(std::uint8_t uid)
{
    switch (uid) {
        case 0: cell = 0; return 1;
        case 1: cell = 1; return 1;
        case 2: cell = 2; return 1;
        case 3: cell = 3; return 1;
    }
    return 0;
}

extern "C" int etask_dispatch_4(std::uint8_t uid)
{
    return static_cast<int>(
        mgr4.register_task(static_cast<tid>(uid), etools::memory::buffer_view{nullptr, 0}));
}

// ============================================================= 2. instant dispatch, 16 tasks

extern "C" int hand_dispatch_16(std::uint8_t uid)
{
    switch (uid) {
        case 0:  cell = 0;  return 1;
        case 1:  cell = 1;  return 1;
        case 2:  cell = 2;  return 1;
        case 3:  cell = 3;  return 1;
        case 4:  cell = 4;  return 1;
        case 5:  cell = 5;  return 1;
        case 6:  cell = 6;  return 1;
        case 7:  cell = 7;  return 1;
        case 8:  cell = 8;  return 1;
        case 9:  cell = 9;  return 1;
        case 10: cell = 10; return 1;
        case 11: cell = 11; return 1;
        case 12: cell = 12; return 1;
        case 13: cell = 13; return 1;
        case 14: cell = 14; return 1;
        case 15: cell = 15; return 1;
    }
    return 0;
}

extern "C" int etask_dispatch_16(std::uint8_t uid)
{
    return static_cast<int>(
        mgr16.register_task(static_cast<tid>(uid), etools::memory::buffer_view{nullptr, 0}));
}

// ================================================================== 3. the update() tick

/// Hand-written: check a flag, make one indirect call. What a project writes without a framework.
extern "C" void hand_tick()
{
    const handler_t fn = handler_slot;
    if (fn) fn();
}

/// etask: two virtual calls (is_finished, on_execute) plus the manager's per-tick bookkeeping
/// (garbage bitset reset, the vector walk, the erase-remove pass).
extern "C" void etask_tick()
{
    poll_mgr.update();
}

// ==================================================== 4. dispatch_factory::emplace vs a switch

extern "C" int hand_emplace(std::uint8_t key)
{
    // Construct the matching type in raw storage, run it, destroy it - by hand.
    base_t* p = nullptr;
    switch (key) {
        case 0: p = new (raw_storage) leaf<0>{}; break;
        case 1: p = new (raw_storage) leaf<1>{}; break;
        case 2: p = new (raw_storage) leaf<2>{}; break;
        case 3: p = new (raw_storage) leaf<3>{}; break;
        case 4: p = new (raw_storage) leaf<4>{}; break;
        case 5: p = new (raw_storage) leaf<5>{}; break;
        case 6: p = new (raw_storage) leaf<6>{}; break;
        case 7: p = new (raw_storage) leaf<7>{}; break;
        default: return 0;
    }
    p->run();
    p->~base_t();
    return 1;
}

extern "C" int etask_emplace(std::uint8_t key)
{
    auto handle = factory.emplace(key);
    if (!handle) return 0;
    handle->run();
    return 1;
}
