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

} // namespace generated::scopes
#endif // GENERATED_SCOPES_HPP_
