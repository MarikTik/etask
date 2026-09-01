/**
* @file scopes.hpp
*
* @brief One accessor per scope, over the project's context tree.
*
* A task that belongs to a scope is constructed with that scope's `context&`.
* A task arriving over the wire has no call site to hand one in, so the
* unpacking adapter binds the scope through the accessor named here.
*
* The context tree itself is owned by this file and deliberately cannot be
* named from outside it: a root you can reach is a root you can duplicate,
* alias, or pass the wrong branch of. Your scope's context reaches you the
* one way it should - as your task's constructor argument.
*
* What lives *inside* each context is entirely yours; see the `context.hpp`
* in each scope directory.
*
* @warning GENERATED - DO NOT EDIT. Regenerated in full from the schema
*          on every generate; hand edits are overwritten. Regenerate via the
*          CMake `etask-generate` target, or `etask generate`.
*/
#ifndef GENERATED_SCOPES_HPP_
#define GENERATED_SCOPES_HPP_
#include "../sys/context.hpp"
#include "../sys/nothing/context.hpp"
#include "../sys/scalars/context.hpp"
#include "../sys/wide/context.hpp"
#include "../sys/keyed/context.hpp"
#include <etask/core/task_unpack_adapter.hpp>

namespace generated::detail {

    /**
    * @brief The project's one context tree.
    *
    * Every scope's context is a member of its parent's, so this single
    * `sys::context` transitively owns all of them.
    *
    * A function-local static, so it is constructed on **first use** - the
    * first task registration - rather than before `main`. Contexts hold
    * hardware handles, and constructing those at static-init time is the one
    * ordering hazard this framework otherwise has no way to hit.
    *
    * @note Internal. It is in `detail` because nothing outside should be able
    *       to name it: a reachable tree is one that can be duplicated or
    *       partially aliased. Tasks receive their own scope's context, which
    *       is the only access anything needs.
    *
    * @return The tree, for the accessors in `generated::scopes` to index into.
    */
    [[nodiscard]] inline sys::context& tree() noexcept
    {
        static sys::context instance;
        return instance;
    }

} // namespace generated::detail

namespace generated::scopes {

    /**
    * @brief The `context` of `the top-level scope`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::context& system() noexcept
    {
        return detail::tree();
    }

    /**
    * @brief The `context` of `nothing`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::nothing::context& nothing() noexcept
    {
        return detail::tree().nothing;
    }

    /**
    * @brief The `context` of `scalars`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::scalars::context& scalars() noexcept
    {
        return detail::tree().scalars;
    }

    /**
    * @brief The `context` of `wide`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::wide::context& wide() noexcept
    {
        return detail::tree().wide;
    }

    /**
    * @brief The `context` of `keyed`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::keyed::context& keyed() noexcept
    {
        return detail::tree().keyed;
    }

} // namespace generated::scopes

/**
* @brief Binds each scope index to its accessor.
*
* A task declares `static constexpr etask::core::scope_index_t scope = N;`
* and the unpacking adapter resolves N here. An index rather than the
* accessor itself because that value ends up inside the adapter's mangled
* type name, and a function pointer mangles as the entire function - tens
* of bytes of typeinfo string per task, which on a microcontroller is flash.
*
* Each specialization inlines to the same member offset the accessor does,
* so this costs nothing at runtime.
*/
namespace etask::core {

    /// @brief `the top-level scope`. @see generated::scopes::system
    template<> struct scope_binding<0> {
        [[nodiscard]] static sys::context& get() noexcept
        { return generated::scopes::system(); }
    };

    /// @brief `nothing`. @see generated::scopes::nothing
    template<> struct scope_binding<1> {
        [[nodiscard]] static sys::nothing::context& get() noexcept
        { return generated::scopes::nothing(); }
    };

    /// @brief `scalars`. @see generated::scopes::scalars
    template<> struct scope_binding<2> {
        [[nodiscard]] static sys::scalars::context& get() noexcept
        { return generated::scopes::scalars(); }
    };

    /// @brief `wide`. @see generated::scopes::wide
    template<> struct scope_binding<3> {
        [[nodiscard]] static sys::wide::context& get() noexcept
        { return generated::scopes::wide(); }
    };

    /// @brief `keyed`. @see generated::scopes::keyed
    template<> struct scope_binding<4> {
        [[nodiscard]] static sys::keyed::context& get() noexcept
        { return generated::scopes::keyed(); }
    };

} // namespace etask::core
#endif // GENERATED_SCOPES_HPP_
