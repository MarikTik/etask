// tests/test_scope_binding.cpp
// SPDX-License-Identifier: MIT
//
// A task names the scope it is injected with by *index*, resolved through
// `scope_binding<N>`. The index exists so that the adapter's mangled type name
// does not contain the accessor's - a function-pointer template parameter
// mangles as the whole function, which is 32 bytes of typeinfo string per task.
//
// What is tested here is that the indirection is transparent: the adapter reaches
// the right context, and the resolution leaves nothing behind at runtime.
//
// The *negative* cases - an index with no binding, and an index bound to another
// scope - are `static_assert`s, so their failure is a compile error and cannot be
// expressed as a runtime test. They are exercised by compiling a deliberately
// mis-generated project; see `scripts/measure_rtti.py` for the harness shape.

#include <gtest/gtest.h>

#include <cstdint>
#include <type_traits>

#include <etask/core/task_unpack_adapter.hpp>
#include <etask/core/tasks/polled_task.hpp>
#include <etools/memory/buffer_view.hpp>
#include <etools/meta/typelist.hpp>

namespace {

    enum class task_key : std::uint8_t { spin = 1 };

    /// Two contexts of *identical shape*, as two instances of one abstract scope
    /// would produce. Distinct types all the same, which is what keeps a
    /// mis-bound index from being a silent mis-binding rather than a loud one.
    struct left_context { int calls = 0; };
    struct right_context { int calls = 0; };

    left_context& left_instance() noexcept
    {
        static left_context instance;
        return instance;
    }

    right_context& right_instance() noexcept
    {
        static right_context instance;
        return instance;
    }

} // namespace

// The bindings a generated `scopes.hpp` would emit, by hand so this test does
// not depend on the generator.
namespace etask::core {

    template<> struct scope_binding<0> {
        [[nodiscard]] static left_context& get() noexcept { return left_instance(); }
    };

    template<> struct scope_binding<1> {
        [[nodiscard]] static right_context& get() noexcept { return right_instance(); }
    };

} // namespace etask::core

namespace {

    /// A task in the `left` scope: it takes `left_context&`, so only index 0 can
    /// legally bind it.
    class spin : public etask::core::polled_task<task_key> {
    public:
        static constexpr task_key uid = task_key::spin;
        using params = etools::meta::typelist<std::uint8_t>;
        static constexpr etask::core::scope_index_t scope = 0;

        spin(std::uint8_t duty, left_context& ctx) : _duty{duty}, _ctx{&ctx}
        {
            ++_ctx->calls;
        }

        void on_execute() override {}
        bool is_finished() override { return true; }

        [[nodiscard]] std::uint8_t duty() const noexcept { return _duty; }
        [[nodiscard]] const left_context* context() const noexcept { return _ctx; }

    private:
        std::uint8_t _duty;
        left_context* _ctx;
    };

    using adapter_t = etask::core::scoped_task_unpack_adapter<spin, spin::scope, std::uint8_t>;

} // namespace

// ------------------------------------------------------------- the indirection

TEST(ScopeBinding, ResolvesToTheScopeTheIndexNames)
{
    EXPECT_EQ(&etask::core::scope_binding<0>::get(), &left_instance());
    EXPECT_EQ(&etask::core::scope_binding<1>::get(), &right_instance());
}

TEST(ScopeBinding, TwoScopesOfTheSameShapeStayDistinctTypes)
{
    // The reason a mis-bound index is a compile error rather than a silent
    // mis-binding: nominal typing, not layout.
    static_assert(not std::is_same_v<left_context, right_context>);
    static_assert(sizeof(left_context) == sizeof(right_context));
    static_assert(not std::is_constructible_v<spin, std::uint8_t, right_context&>,
                  "a task must not accept another scope's context");
}

TEST(ScopeBinding, TheIndexIsAnIntegerNotAPointer)
{
    // The whole point of the change: an integer template argument mangles to a
    // few bytes where a function pointer mangles as the entire function.
    static_assert(std::is_integral_v<decltype(spin::scope)>);
    static_assert(std::is_same_v<etask::core::scope_index_t, std::uint16_t>);
}

// ------------------------------------------------------- the adapter's behavior

TEST(ScopeBinding, TheAdapterBuildsTheTaskWithItsOwnContext)
{
    const int before = left_instance().calls;

    // The payload as the wire delivers it: raw bytes, one for the uint8 param.
    std::byte payload[1]{std::byte{42}};

    const adapter_t task{etools::memory::buffer_view{payload, sizeof(payload)}};

    EXPECT_EQ(task.duty(), 42) << "the payload must reach the constructor";
    EXPECT_EQ(task.context(), &left_instance()) << "and so must the bound scope";
    EXPECT_EQ(left_instance().calls, before + 1);
}

TEST(ScopeBinding, TheAdapterIsStillTheTask)
{
    // The manager stores the adapter and drives it through `task<...>`, so the
    // indirection must not have disturbed the inheritance the factory checks.
    static_assert(std::is_base_of_v<spin, adapter_t>);
    static_assert(std::is_base_of_v<etask::core::polled_task<task_key>, adapter_t>);
    static_assert(adapter_t::uid == task_key::spin, "uid must be inherited");
}

TEST(ScopeBinding, TheAdapterAddsNothingToTheObject)
{
    // Resolving a binding is a compile-time lookup; if it were a stored pointer
    // the adapter would be larger than the task it wraps.
    EXPECT_EQ(sizeof(adapter_t), sizeof(spin));
}

TEST(ScopeBinding, TheNativeConstructorSurvives)
{
    // The in-process path hands typed arguments straight in, and wrapping must
    // not take that away - `using Task::Task` is what keeps it.
    static_assert(std::is_constructible_v<adapter_t, std::uint8_t, left_context&>);
}
