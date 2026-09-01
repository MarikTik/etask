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
#include "../sys/instant/context.hpp"
#include "../sys/oneshot/context.hpp"
#include "../sys/polled/context.hpp"
#include "../sys/stateful/context.hpp"
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
    * @brief The `context` of `instant`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::instant::context& instant() noexcept
    {
        return detail::tree().instant;
    }

    /**
    * @brief The `context` of `oneshot`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::oneshot::context& oneshot() noexcept
    {
        return detail::tree().oneshot;
    }

    /**
    * @brief The `context` of `polled`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::polled::context& polled() noexcept
    {
        return detail::tree().polled;
    }

    /**
    * @brief The `context` of `stateful`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::stateful::context& stateful() noexcept
    {
        return detail::tree().stateful;
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

    /// @brief `instant`. @see generated::scopes::instant
    template<> struct scope_binding<1> {
        [[nodiscard]] static sys::instant::context& get() noexcept
        { return generated::scopes::instant(); }
    };

    /// @brief `oneshot`. @see generated::scopes::oneshot
    template<> struct scope_binding<2> {
        [[nodiscard]] static sys::oneshot::context& get() noexcept
        { return generated::scopes::oneshot(); }
    };

    /// @brief `polled`. @see generated::scopes::polled
    template<> struct scope_binding<3> {
        [[nodiscard]] static sys::polled::context& get() noexcept
        { return generated::scopes::polled(); }
    };

    /// @brief `stateful`. @see generated::scopes::stateful
    template<> struct scope_binding<4> {
        [[nodiscard]] static sys::stateful::context& get() noexcept
        { return generated::scopes::stateful(); }
    };

} // namespace etask::core
#endif // GENERATED_SCOPES_HPP_
