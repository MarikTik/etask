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
#include "../sys/mesh/context.hpp"
#include "../sys/mesh/s0/context.hpp"
#include "../sys/mesh/s0/n0/context.hpp"
#include "../sys/mesh/s0/n0/p0/context.hpp"
#include "../sys/mesh/s0/n0/p1/context.hpp"
#include "../sys/mesh/s0/n0/p2/context.hpp"
#include "../sys/mesh/s0/n1/context.hpp"
#include "../sys/mesh/s0/n1/p0/context.hpp"
#include "../sys/mesh/s0/n1/p1/context.hpp"
#include "../sys/mesh/s0/n1/p2/context.hpp"
#include "../sys/mesh/s0/n2/context.hpp"
#include "../sys/mesh/s0/n2/p0/context.hpp"
#include "../sys/mesh/s0/n2/p1/context.hpp"
#include "../sys/mesh/s0/n2/p2/context.hpp"
#include "../sys/mesh/s0/n3/context.hpp"
#include "../sys/mesh/s0/n3/p0/context.hpp"
#include "../sys/mesh/s0/n3/p1/context.hpp"
#include "../sys/mesh/s0/n3/p2/context.hpp"
#include "../sys/mesh/s1/context.hpp"
#include "../sys/mesh/s1/n0/context.hpp"
#include "../sys/mesh/s1/n0/p0/context.hpp"
#include "../sys/mesh/s1/n0/p1/context.hpp"
#include "../sys/mesh/s1/n0/p2/context.hpp"
#include "../sys/mesh/s1/n1/context.hpp"
#include "../sys/mesh/s1/n1/p0/context.hpp"
#include "../sys/mesh/s1/n1/p1/context.hpp"
#include "../sys/mesh/s1/n1/p2/context.hpp"
#include "../sys/mesh/s1/n2/context.hpp"
#include "../sys/mesh/s1/n2/p0/context.hpp"
#include "../sys/mesh/s1/n2/p1/context.hpp"
#include "../sys/mesh/s1/n2/p2/context.hpp"
#include "../sys/mesh/s1/n3/context.hpp"
#include "../sys/mesh/s1/n3/p0/context.hpp"
#include "../sys/mesh/s1/n3/p1/context.hpp"
#include "../sys/mesh/s1/n3/p2/context.hpp"
#include "../sys/mesh/s2/context.hpp"
#include "../sys/mesh/s2/n0/context.hpp"
#include "../sys/mesh/s2/n0/p0/context.hpp"
#include "../sys/mesh/s2/n0/p1/context.hpp"
#include "../sys/mesh/s2/n0/p2/context.hpp"
#include "../sys/mesh/s2/n1/context.hpp"
#include "../sys/mesh/s2/n1/p0/context.hpp"
#include "../sys/mesh/s2/n1/p1/context.hpp"
#include "../sys/mesh/s2/n1/p2/context.hpp"
#include "../sys/mesh/s2/n2/context.hpp"
#include "../sys/mesh/s2/n2/p0/context.hpp"
#include "../sys/mesh/s2/n2/p1/context.hpp"
#include "../sys/mesh/s2/n2/p2/context.hpp"
#include "../sys/mesh/s2/n3/context.hpp"
#include "../sys/mesh/s2/n3/p0/context.hpp"
#include "../sys/mesh/s2/n3/p1/context.hpp"
#include "../sys/mesh/s2/n3/p2/context.hpp"
#include "../sys/mesh/s3/context.hpp"
#include "../sys/mesh/s3/n0/context.hpp"
#include "../sys/mesh/s3/n0/p0/context.hpp"
#include "../sys/mesh/s3/n0/p1/context.hpp"
#include "../sys/mesh/s3/n0/p2/context.hpp"
#include "../sys/mesh/s3/n1/context.hpp"
#include "../sys/mesh/s3/n1/p0/context.hpp"
#include "../sys/mesh/s3/n1/p1/context.hpp"
#include "../sys/mesh/s3/n1/p2/context.hpp"
#include "../sys/mesh/s3/n2/context.hpp"
#include "../sys/mesh/s3/n2/p0/context.hpp"
#include "../sys/mesh/s3/n2/p1/context.hpp"
#include "../sys/mesh/s3/n2/p2/context.hpp"
#include "../sys/mesh/s3/n3/context.hpp"
#include "../sys/mesh/s3/n3/p0/context.hpp"
#include "../sys/mesh/s3/n3/p1/context.hpp"
#include "../sys/mesh/s3/n3/p2/context.hpp"
#include "../sys/mesh/s4/context.hpp"
#include "../sys/mesh/s4/n0/context.hpp"
#include "../sys/mesh/s4/n0/p0/context.hpp"
#include "../sys/mesh/s4/n0/p1/context.hpp"
#include "../sys/mesh/s4/n0/p2/context.hpp"
#include "../sys/mesh/s4/n1/context.hpp"
#include "../sys/mesh/s4/n1/p0/context.hpp"
#include "../sys/mesh/s4/n1/p1/context.hpp"
#include "../sys/mesh/s4/n1/p2/context.hpp"
#include "../sys/mesh/s4/n2/context.hpp"
#include "../sys/mesh/s4/n2/p0/context.hpp"
#include "../sys/mesh/s4/n2/p1/context.hpp"
#include "../sys/mesh/s4/n2/p2/context.hpp"
#include "../sys/mesh/s4/n3/context.hpp"
#include "../sys/mesh/s4/n3/p0/context.hpp"
#include "../sys/mesh/s4/n3/p1/context.hpp"
#include "../sys/mesh/s4/n3/p2/context.hpp"
#include "../sys/mesh/s5/context.hpp"
#include "../sys/mesh/s5/n0/context.hpp"
#include "../sys/mesh/s5/n0/p0/context.hpp"
#include "../sys/mesh/s5/n0/p1/context.hpp"
#include "../sys/mesh/s5/n0/p2/context.hpp"
#include "../sys/mesh/s5/n1/context.hpp"
#include "../sys/mesh/s5/n1/p0/context.hpp"
#include "../sys/mesh/s5/n1/p1/context.hpp"
#include "../sys/mesh/s5/n1/p2/context.hpp"
#include "../sys/mesh/s5/n2/context.hpp"
#include "../sys/mesh/s5/n2/p0/context.hpp"
#include "../sys/mesh/s5/n2/p1/context.hpp"
#include "../sys/mesh/s5/n2/p2/context.hpp"
#include "../sys/mesh/s5/n3/context.hpp"
#include "../sys/mesh/s5/n3/p0/context.hpp"
#include "../sys/mesh/s5/n3/p1/context.hpp"
#include "../sys/mesh/s5/n3/p2/context.hpp"
#include "../sys/bus/context.hpp"
#include "../sys/bus/link_state/context.hpp"
#include "../sys/bus/link/context.hpp"
#include "../sys/bus/reserve/context.hpp"
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
    * @brief The `context` of `mesh`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::context& mesh() noexcept
    {
        return detail::tree().mesh;
    }

    /**
    * @brief The `context` of `mesh.s0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::context& mesh_s0() noexcept
    {
        return detail::tree().mesh.s0;
    }

    /**
    * @brief The `context` of `mesh.s0.n0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n0::context& mesh_s0_n0() noexcept
    {
        return detail::tree().mesh.s0.n0;
    }

    /**
    * @brief The `context` of `mesh.s0.n0.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n0::p0::context& mesh_s0_n0_p0() noexcept
    {
        return detail::tree().mesh.s0.n0.p0;
    }

    /**
    * @brief The `context` of `mesh.s0.n0.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n0::p1::context& mesh_s0_n0_p1() noexcept
    {
        return detail::tree().mesh.s0.n0.p1;
    }

    /**
    * @brief The `context` of `mesh.s0.n0.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n0::p2::context& mesh_s0_n0_p2() noexcept
    {
        return detail::tree().mesh.s0.n0.p2;
    }

    /**
    * @brief The `context` of `mesh.s0.n1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n1::context& mesh_s0_n1() noexcept
    {
        return detail::tree().mesh.s0.n1;
    }

    /**
    * @brief The `context` of `mesh.s0.n1.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n1::p0::context& mesh_s0_n1_p0() noexcept
    {
        return detail::tree().mesh.s0.n1.p0;
    }

    /**
    * @brief The `context` of `mesh.s0.n1.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n1::p1::context& mesh_s0_n1_p1() noexcept
    {
        return detail::tree().mesh.s0.n1.p1;
    }

    /**
    * @brief The `context` of `mesh.s0.n1.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n1::p2::context& mesh_s0_n1_p2() noexcept
    {
        return detail::tree().mesh.s0.n1.p2;
    }

    /**
    * @brief The `context` of `mesh.s0.n2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n2::context& mesh_s0_n2() noexcept
    {
        return detail::tree().mesh.s0.n2;
    }

    /**
    * @brief The `context` of `mesh.s0.n2.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n2::p0::context& mesh_s0_n2_p0() noexcept
    {
        return detail::tree().mesh.s0.n2.p0;
    }

    /**
    * @brief The `context` of `mesh.s0.n2.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n2::p1::context& mesh_s0_n2_p1() noexcept
    {
        return detail::tree().mesh.s0.n2.p1;
    }

    /**
    * @brief The `context` of `mesh.s0.n2.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n2::p2::context& mesh_s0_n2_p2() noexcept
    {
        return detail::tree().mesh.s0.n2.p2;
    }

    /**
    * @brief The `context` of `mesh.s0.n3`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n3::context& mesh_s0_n3() noexcept
    {
        return detail::tree().mesh.s0.n3;
    }

    /**
    * @brief The `context` of `mesh.s0.n3.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n3::p0::context& mesh_s0_n3_p0() noexcept
    {
        return detail::tree().mesh.s0.n3.p0;
    }

    /**
    * @brief The `context` of `mesh.s0.n3.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n3::p1::context& mesh_s0_n3_p1() noexcept
    {
        return detail::tree().mesh.s0.n3.p1;
    }

    /**
    * @brief The `context` of `mesh.s0.n3.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s0::n3::p2::context& mesh_s0_n3_p2() noexcept
    {
        return detail::tree().mesh.s0.n3.p2;
    }

    /**
    * @brief The `context` of `mesh.s1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::context& mesh_s1() noexcept
    {
        return detail::tree().mesh.s1;
    }

    /**
    * @brief The `context` of `mesh.s1.n0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n0::context& mesh_s1_n0() noexcept
    {
        return detail::tree().mesh.s1.n0;
    }

    /**
    * @brief The `context` of `mesh.s1.n0.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n0::p0::context& mesh_s1_n0_p0() noexcept
    {
        return detail::tree().mesh.s1.n0.p0;
    }

    /**
    * @brief The `context` of `mesh.s1.n0.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n0::p1::context& mesh_s1_n0_p1() noexcept
    {
        return detail::tree().mesh.s1.n0.p1;
    }

    /**
    * @brief The `context` of `mesh.s1.n0.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n0::p2::context& mesh_s1_n0_p2() noexcept
    {
        return detail::tree().mesh.s1.n0.p2;
    }

    /**
    * @brief The `context` of `mesh.s1.n1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n1::context& mesh_s1_n1() noexcept
    {
        return detail::tree().mesh.s1.n1;
    }

    /**
    * @brief The `context` of `mesh.s1.n1.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n1::p0::context& mesh_s1_n1_p0() noexcept
    {
        return detail::tree().mesh.s1.n1.p0;
    }

    /**
    * @brief The `context` of `mesh.s1.n1.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n1::p1::context& mesh_s1_n1_p1() noexcept
    {
        return detail::tree().mesh.s1.n1.p1;
    }

    /**
    * @brief The `context` of `mesh.s1.n1.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n1::p2::context& mesh_s1_n1_p2() noexcept
    {
        return detail::tree().mesh.s1.n1.p2;
    }

    /**
    * @brief The `context` of `mesh.s1.n2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n2::context& mesh_s1_n2() noexcept
    {
        return detail::tree().mesh.s1.n2;
    }

    /**
    * @brief The `context` of `mesh.s1.n2.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n2::p0::context& mesh_s1_n2_p0() noexcept
    {
        return detail::tree().mesh.s1.n2.p0;
    }

    /**
    * @brief The `context` of `mesh.s1.n2.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n2::p1::context& mesh_s1_n2_p1() noexcept
    {
        return detail::tree().mesh.s1.n2.p1;
    }

    /**
    * @brief The `context` of `mesh.s1.n2.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n2::p2::context& mesh_s1_n2_p2() noexcept
    {
        return detail::tree().mesh.s1.n2.p2;
    }

    /**
    * @brief The `context` of `mesh.s1.n3`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n3::context& mesh_s1_n3() noexcept
    {
        return detail::tree().mesh.s1.n3;
    }

    /**
    * @brief The `context` of `mesh.s1.n3.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n3::p0::context& mesh_s1_n3_p0() noexcept
    {
        return detail::tree().mesh.s1.n3.p0;
    }

    /**
    * @brief The `context` of `mesh.s1.n3.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n3::p1::context& mesh_s1_n3_p1() noexcept
    {
        return detail::tree().mesh.s1.n3.p1;
    }

    /**
    * @brief The `context` of `mesh.s1.n3.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s1::n3::p2::context& mesh_s1_n3_p2() noexcept
    {
        return detail::tree().mesh.s1.n3.p2;
    }

    /**
    * @brief The `context` of `mesh.s2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::context& mesh_s2() noexcept
    {
        return detail::tree().mesh.s2;
    }

    /**
    * @brief The `context` of `mesh.s2.n0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n0::context& mesh_s2_n0() noexcept
    {
        return detail::tree().mesh.s2.n0;
    }

    /**
    * @brief The `context` of `mesh.s2.n0.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n0::p0::context& mesh_s2_n0_p0() noexcept
    {
        return detail::tree().mesh.s2.n0.p0;
    }

    /**
    * @brief The `context` of `mesh.s2.n0.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n0::p1::context& mesh_s2_n0_p1() noexcept
    {
        return detail::tree().mesh.s2.n0.p1;
    }

    /**
    * @brief The `context` of `mesh.s2.n0.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n0::p2::context& mesh_s2_n0_p2() noexcept
    {
        return detail::tree().mesh.s2.n0.p2;
    }

    /**
    * @brief The `context` of `mesh.s2.n1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n1::context& mesh_s2_n1() noexcept
    {
        return detail::tree().mesh.s2.n1;
    }

    /**
    * @brief The `context` of `mesh.s2.n1.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n1::p0::context& mesh_s2_n1_p0() noexcept
    {
        return detail::tree().mesh.s2.n1.p0;
    }

    /**
    * @brief The `context` of `mesh.s2.n1.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n1::p1::context& mesh_s2_n1_p1() noexcept
    {
        return detail::tree().mesh.s2.n1.p1;
    }

    /**
    * @brief The `context` of `mesh.s2.n1.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n1::p2::context& mesh_s2_n1_p2() noexcept
    {
        return detail::tree().mesh.s2.n1.p2;
    }

    /**
    * @brief The `context` of `mesh.s2.n2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n2::context& mesh_s2_n2() noexcept
    {
        return detail::tree().mesh.s2.n2;
    }

    /**
    * @brief The `context` of `mesh.s2.n2.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n2::p0::context& mesh_s2_n2_p0() noexcept
    {
        return detail::tree().mesh.s2.n2.p0;
    }

    /**
    * @brief The `context` of `mesh.s2.n2.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n2::p1::context& mesh_s2_n2_p1() noexcept
    {
        return detail::tree().mesh.s2.n2.p1;
    }

    /**
    * @brief The `context` of `mesh.s2.n2.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n2::p2::context& mesh_s2_n2_p2() noexcept
    {
        return detail::tree().mesh.s2.n2.p2;
    }

    /**
    * @brief The `context` of `mesh.s2.n3`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n3::context& mesh_s2_n3() noexcept
    {
        return detail::tree().mesh.s2.n3;
    }

    /**
    * @brief The `context` of `mesh.s2.n3.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n3::p0::context& mesh_s2_n3_p0() noexcept
    {
        return detail::tree().mesh.s2.n3.p0;
    }

    /**
    * @brief The `context` of `mesh.s2.n3.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n3::p1::context& mesh_s2_n3_p1() noexcept
    {
        return detail::tree().mesh.s2.n3.p1;
    }

    /**
    * @brief The `context` of `mesh.s2.n3.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s2::n3::p2::context& mesh_s2_n3_p2() noexcept
    {
        return detail::tree().mesh.s2.n3.p2;
    }

    /**
    * @brief The `context` of `mesh.s3`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::context& mesh_s3() noexcept
    {
        return detail::tree().mesh.s3;
    }

    /**
    * @brief The `context` of `mesh.s3.n0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n0::context& mesh_s3_n0() noexcept
    {
        return detail::tree().mesh.s3.n0;
    }

    /**
    * @brief The `context` of `mesh.s3.n0.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n0::p0::context& mesh_s3_n0_p0() noexcept
    {
        return detail::tree().mesh.s3.n0.p0;
    }

    /**
    * @brief The `context` of `mesh.s3.n0.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n0::p1::context& mesh_s3_n0_p1() noexcept
    {
        return detail::tree().mesh.s3.n0.p1;
    }

    /**
    * @brief The `context` of `mesh.s3.n0.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n0::p2::context& mesh_s3_n0_p2() noexcept
    {
        return detail::tree().mesh.s3.n0.p2;
    }

    /**
    * @brief The `context` of `mesh.s3.n1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n1::context& mesh_s3_n1() noexcept
    {
        return detail::tree().mesh.s3.n1;
    }

    /**
    * @brief The `context` of `mesh.s3.n1.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n1::p0::context& mesh_s3_n1_p0() noexcept
    {
        return detail::tree().mesh.s3.n1.p0;
    }

    /**
    * @brief The `context` of `mesh.s3.n1.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n1::p1::context& mesh_s3_n1_p1() noexcept
    {
        return detail::tree().mesh.s3.n1.p1;
    }

    /**
    * @brief The `context` of `mesh.s3.n1.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n1::p2::context& mesh_s3_n1_p2() noexcept
    {
        return detail::tree().mesh.s3.n1.p2;
    }

    /**
    * @brief The `context` of `mesh.s3.n2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n2::context& mesh_s3_n2() noexcept
    {
        return detail::tree().mesh.s3.n2;
    }

    /**
    * @brief The `context` of `mesh.s3.n2.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n2::p0::context& mesh_s3_n2_p0() noexcept
    {
        return detail::tree().mesh.s3.n2.p0;
    }

    /**
    * @brief The `context` of `mesh.s3.n2.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n2::p1::context& mesh_s3_n2_p1() noexcept
    {
        return detail::tree().mesh.s3.n2.p1;
    }

    /**
    * @brief The `context` of `mesh.s3.n2.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n2::p2::context& mesh_s3_n2_p2() noexcept
    {
        return detail::tree().mesh.s3.n2.p2;
    }

    /**
    * @brief The `context` of `mesh.s3.n3`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n3::context& mesh_s3_n3() noexcept
    {
        return detail::tree().mesh.s3.n3;
    }

    /**
    * @brief The `context` of `mesh.s3.n3.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n3::p0::context& mesh_s3_n3_p0() noexcept
    {
        return detail::tree().mesh.s3.n3.p0;
    }

    /**
    * @brief The `context` of `mesh.s3.n3.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n3::p1::context& mesh_s3_n3_p1() noexcept
    {
        return detail::tree().mesh.s3.n3.p1;
    }

    /**
    * @brief The `context` of `mesh.s3.n3.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s3::n3::p2::context& mesh_s3_n3_p2() noexcept
    {
        return detail::tree().mesh.s3.n3.p2;
    }

    /**
    * @brief The `context` of `mesh.s4`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::context& mesh_s4() noexcept
    {
        return detail::tree().mesh.s4;
    }

    /**
    * @brief The `context` of `mesh.s4.n0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n0::context& mesh_s4_n0() noexcept
    {
        return detail::tree().mesh.s4.n0;
    }

    /**
    * @brief The `context` of `mesh.s4.n0.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n0::p0::context& mesh_s4_n0_p0() noexcept
    {
        return detail::tree().mesh.s4.n0.p0;
    }

    /**
    * @brief The `context` of `mesh.s4.n0.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n0::p1::context& mesh_s4_n0_p1() noexcept
    {
        return detail::tree().mesh.s4.n0.p1;
    }

    /**
    * @brief The `context` of `mesh.s4.n0.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n0::p2::context& mesh_s4_n0_p2() noexcept
    {
        return detail::tree().mesh.s4.n0.p2;
    }

    /**
    * @brief The `context` of `mesh.s4.n1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n1::context& mesh_s4_n1() noexcept
    {
        return detail::tree().mesh.s4.n1;
    }

    /**
    * @brief The `context` of `mesh.s4.n1.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n1::p0::context& mesh_s4_n1_p0() noexcept
    {
        return detail::tree().mesh.s4.n1.p0;
    }

    /**
    * @brief The `context` of `mesh.s4.n1.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n1::p1::context& mesh_s4_n1_p1() noexcept
    {
        return detail::tree().mesh.s4.n1.p1;
    }

    /**
    * @brief The `context` of `mesh.s4.n1.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n1::p2::context& mesh_s4_n1_p2() noexcept
    {
        return detail::tree().mesh.s4.n1.p2;
    }

    /**
    * @brief The `context` of `mesh.s4.n2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n2::context& mesh_s4_n2() noexcept
    {
        return detail::tree().mesh.s4.n2;
    }

    /**
    * @brief The `context` of `mesh.s4.n2.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n2::p0::context& mesh_s4_n2_p0() noexcept
    {
        return detail::tree().mesh.s4.n2.p0;
    }

    /**
    * @brief The `context` of `mesh.s4.n2.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n2::p1::context& mesh_s4_n2_p1() noexcept
    {
        return detail::tree().mesh.s4.n2.p1;
    }

    /**
    * @brief The `context` of `mesh.s4.n2.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n2::p2::context& mesh_s4_n2_p2() noexcept
    {
        return detail::tree().mesh.s4.n2.p2;
    }

    /**
    * @brief The `context` of `mesh.s4.n3`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n3::context& mesh_s4_n3() noexcept
    {
        return detail::tree().mesh.s4.n3;
    }

    /**
    * @brief The `context` of `mesh.s4.n3.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n3::p0::context& mesh_s4_n3_p0() noexcept
    {
        return detail::tree().mesh.s4.n3.p0;
    }

    /**
    * @brief The `context` of `mesh.s4.n3.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n3::p1::context& mesh_s4_n3_p1() noexcept
    {
        return detail::tree().mesh.s4.n3.p1;
    }

    /**
    * @brief The `context` of `mesh.s4.n3.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s4::n3::p2::context& mesh_s4_n3_p2() noexcept
    {
        return detail::tree().mesh.s4.n3.p2;
    }

    /**
    * @brief The `context` of `mesh.s5`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::context& mesh_s5() noexcept
    {
        return detail::tree().mesh.s5;
    }

    /**
    * @brief The `context` of `mesh.s5.n0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n0::context& mesh_s5_n0() noexcept
    {
        return detail::tree().mesh.s5.n0;
    }

    /**
    * @brief The `context` of `mesh.s5.n0.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n0::p0::context& mesh_s5_n0_p0() noexcept
    {
        return detail::tree().mesh.s5.n0.p0;
    }

    /**
    * @brief The `context` of `mesh.s5.n0.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n0::p1::context& mesh_s5_n0_p1() noexcept
    {
        return detail::tree().mesh.s5.n0.p1;
    }

    /**
    * @brief The `context` of `mesh.s5.n0.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n0::p2::context& mesh_s5_n0_p2() noexcept
    {
        return detail::tree().mesh.s5.n0.p2;
    }

    /**
    * @brief The `context` of `mesh.s5.n1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n1::context& mesh_s5_n1() noexcept
    {
        return detail::tree().mesh.s5.n1;
    }

    /**
    * @brief The `context` of `mesh.s5.n1.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n1::p0::context& mesh_s5_n1_p0() noexcept
    {
        return detail::tree().mesh.s5.n1.p0;
    }

    /**
    * @brief The `context` of `mesh.s5.n1.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n1::p1::context& mesh_s5_n1_p1() noexcept
    {
        return detail::tree().mesh.s5.n1.p1;
    }

    /**
    * @brief The `context` of `mesh.s5.n1.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n1::p2::context& mesh_s5_n1_p2() noexcept
    {
        return detail::tree().mesh.s5.n1.p2;
    }

    /**
    * @brief The `context` of `mesh.s5.n2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n2::context& mesh_s5_n2() noexcept
    {
        return detail::tree().mesh.s5.n2;
    }

    /**
    * @brief The `context` of `mesh.s5.n2.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n2::p0::context& mesh_s5_n2_p0() noexcept
    {
        return detail::tree().mesh.s5.n2.p0;
    }

    /**
    * @brief The `context` of `mesh.s5.n2.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n2::p1::context& mesh_s5_n2_p1() noexcept
    {
        return detail::tree().mesh.s5.n2.p1;
    }

    /**
    * @brief The `context` of `mesh.s5.n2.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n2::p2::context& mesh_s5_n2_p2() noexcept
    {
        return detail::tree().mesh.s5.n2.p2;
    }

    /**
    * @brief The `context` of `mesh.s5.n3`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n3::context& mesh_s5_n3() noexcept
    {
        return detail::tree().mesh.s5.n3;
    }

    /**
    * @brief The `context` of `mesh.s5.n3.p0`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n3::p0::context& mesh_s5_n3_p0() noexcept
    {
        return detail::tree().mesh.s5.n3.p0;
    }

    /**
    * @brief The `context` of `mesh.s5.n3.p1`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n3::p1::context& mesh_s5_n3_p1() noexcept
    {
        return detail::tree().mesh.s5.n3.p1;
    }

    /**
    * @brief The `context` of `mesh.s5.n3.p2`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::mesh::s5::n3::p2::context& mesh_s5_n3_p2() noexcept
    {
        return detail::tree().mesh.s5.n3.p2;
    }

    /**
    * @brief The `context` of `bus`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::bus::context& bus() noexcept
    {
        return detail::tree().bus;
    }

    /**
    * @brief The `context` of `bus.link_state`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::bus::link_state::context& bus_link_state() noexcept
    {
        return detail::tree().bus.link_state;
    }

    /**
    * @brief The `context` of `bus.link`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::bus::link::context& bus_link() noexcept
    {
        return detail::tree().bus.link;
    }

    /**
    * @brief The `context` of `bus.reserve`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::bus::reserve::context& bus_reserve() noexcept
    {
        return detail::tree().bus.reserve;
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

    /// @brief `mesh`. @see generated::scopes::mesh
    template<> struct scope_binding<1> {
        [[nodiscard]] static sys::mesh::context& get() noexcept
        { return generated::scopes::mesh(); }
    };

    /// @brief `mesh.s0`. @see generated::scopes::mesh_s0
    template<> struct scope_binding<2> {
        [[nodiscard]] static sys::mesh::s0::context& get() noexcept
        { return generated::scopes::mesh_s0(); }
    };

    /// @brief `mesh.s0.n0`. @see generated::scopes::mesh_s0_n0
    template<> struct scope_binding<3> {
        [[nodiscard]] static sys::mesh::s0::n0::context& get() noexcept
        { return generated::scopes::mesh_s0_n0(); }
    };

    /// @brief `mesh.s0.n0.p0`. @see generated::scopes::mesh_s0_n0_p0
    template<> struct scope_binding<4> {
        [[nodiscard]] static sys::mesh::s0::n0::p0::context& get() noexcept
        { return generated::scopes::mesh_s0_n0_p0(); }
    };

    /// @brief `mesh.s0.n0.p1`. @see generated::scopes::mesh_s0_n0_p1
    template<> struct scope_binding<5> {
        [[nodiscard]] static sys::mesh::s0::n0::p1::context& get() noexcept
        { return generated::scopes::mesh_s0_n0_p1(); }
    };

    /// @brief `mesh.s0.n0.p2`. @see generated::scopes::mesh_s0_n0_p2
    template<> struct scope_binding<6> {
        [[nodiscard]] static sys::mesh::s0::n0::p2::context& get() noexcept
        { return generated::scopes::mesh_s0_n0_p2(); }
    };

    /// @brief `mesh.s0.n1`. @see generated::scopes::mesh_s0_n1
    template<> struct scope_binding<7> {
        [[nodiscard]] static sys::mesh::s0::n1::context& get() noexcept
        { return generated::scopes::mesh_s0_n1(); }
    };

    /// @brief `mesh.s0.n1.p0`. @see generated::scopes::mesh_s0_n1_p0
    template<> struct scope_binding<8> {
        [[nodiscard]] static sys::mesh::s0::n1::p0::context& get() noexcept
        { return generated::scopes::mesh_s0_n1_p0(); }
    };

    /// @brief `mesh.s0.n1.p1`. @see generated::scopes::mesh_s0_n1_p1
    template<> struct scope_binding<9> {
        [[nodiscard]] static sys::mesh::s0::n1::p1::context& get() noexcept
        { return generated::scopes::mesh_s0_n1_p1(); }
    };

    /// @brief `mesh.s0.n1.p2`. @see generated::scopes::mesh_s0_n1_p2
    template<> struct scope_binding<10> {
        [[nodiscard]] static sys::mesh::s0::n1::p2::context& get() noexcept
        { return generated::scopes::mesh_s0_n1_p2(); }
    };

    /// @brief `mesh.s0.n2`. @see generated::scopes::mesh_s0_n2
    template<> struct scope_binding<11> {
        [[nodiscard]] static sys::mesh::s0::n2::context& get() noexcept
        { return generated::scopes::mesh_s0_n2(); }
    };

    /// @brief `mesh.s0.n2.p0`. @see generated::scopes::mesh_s0_n2_p0
    template<> struct scope_binding<12> {
        [[nodiscard]] static sys::mesh::s0::n2::p0::context& get() noexcept
        { return generated::scopes::mesh_s0_n2_p0(); }
    };

    /// @brief `mesh.s0.n2.p1`. @see generated::scopes::mesh_s0_n2_p1
    template<> struct scope_binding<13> {
        [[nodiscard]] static sys::mesh::s0::n2::p1::context& get() noexcept
        { return generated::scopes::mesh_s0_n2_p1(); }
    };

    /// @brief `mesh.s0.n2.p2`. @see generated::scopes::mesh_s0_n2_p2
    template<> struct scope_binding<14> {
        [[nodiscard]] static sys::mesh::s0::n2::p2::context& get() noexcept
        { return generated::scopes::mesh_s0_n2_p2(); }
    };

    /// @brief `mesh.s0.n3`. @see generated::scopes::mesh_s0_n3
    template<> struct scope_binding<15> {
        [[nodiscard]] static sys::mesh::s0::n3::context& get() noexcept
        { return generated::scopes::mesh_s0_n3(); }
    };

    /// @brief `mesh.s0.n3.p0`. @see generated::scopes::mesh_s0_n3_p0
    template<> struct scope_binding<16> {
        [[nodiscard]] static sys::mesh::s0::n3::p0::context& get() noexcept
        { return generated::scopes::mesh_s0_n3_p0(); }
    };

    /// @brief `mesh.s0.n3.p1`. @see generated::scopes::mesh_s0_n3_p1
    template<> struct scope_binding<17> {
        [[nodiscard]] static sys::mesh::s0::n3::p1::context& get() noexcept
        { return generated::scopes::mesh_s0_n3_p1(); }
    };

    /// @brief `mesh.s0.n3.p2`. @see generated::scopes::mesh_s0_n3_p2
    template<> struct scope_binding<18> {
        [[nodiscard]] static sys::mesh::s0::n3::p2::context& get() noexcept
        { return generated::scopes::mesh_s0_n3_p2(); }
    };

    /// @brief `mesh.s1`. @see generated::scopes::mesh_s1
    template<> struct scope_binding<19> {
        [[nodiscard]] static sys::mesh::s1::context& get() noexcept
        { return generated::scopes::mesh_s1(); }
    };

    /// @brief `mesh.s1.n0`. @see generated::scopes::mesh_s1_n0
    template<> struct scope_binding<20> {
        [[nodiscard]] static sys::mesh::s1::n0::context& get() noexcept
        { return generated::scopes::mesh_s1_n0(); }
    };

    /// @brief `mesh.s1.n0.p0`. @see generated::scopes::mesh_s1_n0_p0
    template<> struct scope_binding<21> {
        [[nodiscard]] static sys::mesh::s1::n0::p0::context& get() noexcept
        { return generated::scopes::mesh_s1_n0_p0(); }
    };

    /// @brief `mesh.s1.n0.p1`. @see generated::scopes::mesh_s1_n0_p1
    template<> struct scope_binding<22> {
        [[nodiscard]] static sys::mesh::s1::n0::p1::context& get() noexcept
        { return generated::scopes::mesh_s1_n0_p1(); }
    };

    /// @brief `mesh.s1.n0.p2`. @see generated::scopes::mesh_s1_n0_p2
    template<> struct scope_binding<23> {
        [[nodiscard]] static sys::mesh::s1::n0::p2::context& get() noexcept
        { return generated::scopes::mesh_s1_n0_p2(); }
    };

    /// @brief `mesh.s1.n1`. @see generated::scopes::mesh_s1_n1
    template<> struct scope_binding<24> {
        [[nodiscard]] static sys::mesh::s1::n1::context& get() noexcept
        { return generated::scopes::mesh_s1_n1(); }
    };

    /// @brief `mesh.s1.n1.p0`. @see generated::scopes::mesh_s1_n1_p0
    template<> struct scope_binding<25> {
        [[nodiscard]] static sys::mesh::s1::n1::p0::context& get() noexcept
        { return generated::scopes::mesh_s1_n1_p0(); }
    };

    /// @brief `mesh.s1.n1.p1`. @see generated::scopes::mesh_s1_n1_p1
    template<> struct scope_binding<26> {
        [[nodiscard]] static sys::mesh::s1::n1::p1::context& get() noexcept
        { return generated::scopes::mesh_s1_n1_p1(); }
    };

    /// @brief `mesh.s1.n1.p2`. @see generated::scopes::mesh_s1_n1_p2
    template<> struct scope_binding<27> {
        [[nodiscard]] static sys::mesh::s1::n1::p2::context& get() noexcept
        { return generated::scopes::mesh_s1_n1_p2(); }
    };

    /// @brief `mesh.s1.n2`. @see generated::scopes::mesh_s1_n2
    template<> struct scope_binding<28> {
        [[nodiscard]] static sys::mesh::s1::n2::context& get() noexcept
        { return generated::scopes::mesh_s1_n2(); }
    };

    /// @brief `mesh.s1.n2.p0`. @see generated::scopes::mesh_s1_n2_p0
    template<> struct scope_binding<29> {
        [[nodiscard]] static sys::mesh::s1::n2::p0::context& get() noexcept
        { return generated::scopes::mesh_s1_n2_p0(); }
    };

    /// @brief `mesh.s1.n2.p1`. @see generated::scopes::mesh_s1_n2_p1
    template<> struct scope_binding<30> {
        [[nodiscard]] static sys::mesh::s1::n2::p1::context& get() noexcept
        { return generated::scopes::mesh_s1_n2_p1(); }
    };

    /// @brief `mesh.s1.n2.p2`. @see generated::scopes::mesh_s1_n2_p2
    template<> struct scope_binding<31> {
        [[nodiscard]] static sys::mesh::s1::n2::p2::context& get() noexcept
        { return generated::scopes::mesh_s1_n2_p2(); }
    };

    /// @brief `mesh.s1.n3`. @see generated::scopes::mesh_s1_n3
    template<> struct scope_binding<32> {
        [[nodiscard]] static sys::mesh::s1::n3::context& get() noexcept
        { return generated::scopes::mesh_s1_n3(); }
    };

    /// @brief `mesh.s1.n3.p0`. @see generated::scopes::mesh_s1_n3_p0
    template<> struct scope_binding<33> {
        [[nodiscard]] static sys::mesh::s1::n3::p0::context& get() noexcept
        { return generated::scopes::mesh_s1_n3_p0(); }
    };

    /// @brief `mesh.s1.n3.p1`. @see generated::scopes::mesh_s1_n3_p1
    template<> struct scope_binding<34> {
        [[nodiscard]] static sys::mesh::s1::n3::p1::context& get() noexcept
        { return generated::scopes::mesh_s1_n3_p1(); }
    };

    /// @brief `mesh.s1.n3.p2`. @see generated::scopes::mesh_s1_n3_p2
    template<> struct scope_binding<35> {
        [[nodiscard]] static sys::mesh::s1::n3::p2::context& get() noexcept
        { return generated::scopes::mesh_s1_n3_p2(); }
    };

    /// @brief `mesh.s2`. @see generated::scopes::mesh_s2
    template<> struct scope_binding<36> {
        [[nodiscard]] static sys::mesh::s2::context& get() noexcept
        { return generated::scopes::mesh_s2(); }
    };

    /// @brief `mesh.s2.n0`. @see generated::scopes::mesh_s2_n0
    template<> struct scope_binding<37> {
        [[nodiscard]] static sys::mesh::s2::n0::context& get() noexcept
        { return generated::scopes::mesh_s2_n0(); }
    };

    /// @brief `mesh.s2.n0.p0`. @see generated::scopes::mesh_s2_n0_p0
    template<> struct scope_binding<38> {
        [[nodiscard]] static sys::mesh::s2::n0::p0::context& get() noexcept
        { return generated::scopes::mesh_s2_n0_p0(); }
    };

    /// @brief `mesh.s2.n0.p1`. @see generated::scopes::mesh_s2_n0_p1
    template<> struct scope_binding<39> {
        [[nodiscard]] static sys::mesh::s2::n0::p1::context& get() noexcept
        { return generated::scopes::mesh_s2_n0_p1(); }
    };

    /// @brief `mesh.s2.n0.p2`. @see generated::scopes::mesh_s2_n0_p2
    template<> struct scope_binding<40> {
        [[nodiscard]] static sys::mesh::s2::n0::p2::context& get() noexcept
        { return generated::scopes::mesh_s2_n0_p2(); }
    };

    /// @brief `mesh.s2.n1`. @see generated::scopes::mesh_s2_n1
    template<> struct scope_binding<41> {
        [[nodiscard]] static sys::mesh::s2::n1::context& get() noexcept
        { return generated::scopes::mesh_s2_n1(); }
    };

    /// @brief `mesh.s2.n1.p0`. @see generated::scopes::mesh_s2_n1_p0
    template<> struct scope_binding<42> {
        [[nodiscard]] static sys::mesh::s2::n1::p0::context& get() noexcept
        { return generated::scopes::mesh_s2_n1_p0(); }
    };

    /// @brief `mesh.s2.n1.p1`. @see generated::scopes::mesh_s2_n1_p1
    template<> struct scope_binding<43> {
        [[nodiscard]] static sys::mesh::s2::n1::p1::context& get() noexcept
        { return generated::scopes::mesh_s2_n1_p1(); }
    };

    /// @brief `mesh.s2.n1.p2`. @see generated::scopes::mesh_s2_n1_p2
    template<> struct scope_binding<44> {
        [[nodiscard]] static sys::mesh::s2::n1::p2::context& get() noexcept
        { return generated::scopes::mesh_s2_n1_p2(); }
    };

    /// @brief `mesh.s2.n2`. @see generated::scopes::mesh_s2_n2
    template<> struct scope_binding<45> {
        [[nodiscard]] static sys::mesh::s2::n2::context& get() noexcept
        { return generated::scopes::mesh_s2_n2(); }
    };

    /// @brief `mesh.s2.n2.p0`. @see generated::scopes::mesh_s2_n2_p0
    template<> struct scope_binding<46> {
        [[nodiscard]] static sys::mesh::s2::n2::p0::context& get() noexcept
        { return generated::scopes::mesh_s2_n2_p0(); }
    };

    /// @brief `mesh.s2.n2.p1`. @see generated::scopes::mesh_s2_n2_p1
    template<> struct scope_binding<47> {
        [[nodiscard]] static sys::mesh::s2::n2::p1::context& get() noexcept
        { return generated::scopes::mesh_s2_n2_p1(); }
    };

    /// @brief `mesh.s2.n2.p2`. @see generated::scopes::mesh_s2_n2_p2
    template<> struct scope_binding<48> {
        [[nodiscard]] static sys::mesh::s2::n2::p2::context& get() noexcept
        { return generated::scopes::mesh_s2_n2_p2(); }
    };

    /// @brief `mesh.s2.n3`. @see generated::scopes::mesh_s2_n3
    template<> struct scope_binding<49> {
        [[nodiscard]] static sys::mesh::s2::n3::context& get() noexcept
        { return generated::scopes::mesh_s2_n3(); }
    };

    /// @brief `mesh.s2.n3.p0`. @see generated::scopes::mesh_s2_n3_p0
    template<> struct scope_binding<50> {
        [[nodiscard]] static sys::mesh::s2::n3::p0::context& get() noexcept
        { return generated::scopes::mesh_s2_n3_p0(); }
    };

    /// @brief `mesh.s2.n3.p1`. @see generated::scopes::mesh_s2_n3_p1
    template<> struct scope_binding<51> {
        [[nodiscard]] static sys::mesh::s2::n3::p1::context& get() noexcept
        { return generated::scopes::mesh_s2_n3_p1(); }
    };

    /// @brief `mesh.s2.n3.p2`. @see generated::scopes::mesh_s2_n3_p2
    template<> struct scope_binding<52> {
        [[nodiscard]] static sys::mesh::s2::n3::p2::context& get() noexcept
        { return generated::scopes::mesh_s2_n3_p2(); }
    };

    /// @brief `mesh.s3`. @see generated::scopes::mesh_s3
    template<> struct scope_binding<53> {
        [[nodiscard]] static sys::mesh::s3::context& get() noexcept
        { return generated::scopes::mesh_s3(); }
    };

    /// @brief `mesh.s3.n0`. @see generated::scopes::mesh_s3_n0
    template<> struct scope_binding<54> {
        [[nodiscard]] static sys::mesh::s3::n0::context& get() noexcept
        { return generated::scopes::mesh_s3_n0(); }
    };

    /// @brief `mesh.s3.n0.p0`. @see generated::scopes::mesh_s3_n0_p0
    template<> struct scope_binding<55> {
        [[nodiscard]] static sys::mesh::s3::n0::p0::context& get() noexcept
        { return generated::scopes::mesh_s3_n0_p0(); }
    };

    /// @brief `mesh.s3.n0.p1`. @see generated::scopes::mesh_s3_n0_p1
    template<> struct scope_binding<56> {
        [[nodiscard]] static sys::mesh::s3::n0::p1::context& get() noexcept
        { return generated::scopes::mesh_s3_n0_p1(); }
    };

    /// @brief `mesh.s3.n0.p2`. @see generated::scopes::mesh_s3_n0_p2
    template<> struct scope_binding<57> {
        [[nodiscard]] static sys::mesh::s3::n0::p2::context& get() noexcept
        { return generated::scopes::mesh_s3_n0_p2(); }
    };

    /// @brief `mesh.s3.n1`. @see generated::scopes::mesh_s3_n1
    template<> struct scope_binding<58> {
        [[nodiscard]] static sys::mesh::s3::n1::context& get() noexcept
        { return generated::scopes::mesh_s3_n1(); }
    };

    /// @brief `mesh.s3.n1.p0`. @see generated::scopes::mesh_s3_n1_p0
    template<> struct scope_binding<59> {
        [[nodiscard]] static sys::mesh::s3::n1::p0::context& get() noexcept
        { return generated::scopes::mesh_s3_n1_p0(); }
    };

    /// @brief `mesh.s3.n1.p1`. @see generated::scopes::mesh_s3_n1_p1
    template<> struct scope_binding<60> {
        [[nodiscard]] static sys::mesh::s3::n1::p1::context& get() noexcept
        { return generated::scopes::mesh_s3_n1_p1(); }
    };

    /// @brief `mesh.s3.n1.p2`. @see generated::scopes::mesh_s3_n1_p2
    template<> struct scope_binding<61> {
        [[nodiscard]] static sys::mesh::s3::n1::p2::context& get() noexcept
        { return generated::scopes::mesh_s3_n1_p2(); }
    };

    /// @brief `mesh.s3.n2`. @see generated::scopes::mesh_s3_n2
    template<> struct scope_binding<62> {
        [[nodiscard]] static sys::mesh::s3::n2::context& get() noexcept
        { return generated::scopes::mesh_s3_n2(); }
    };

    /// @brief `mesh.s3.n2.p0`. @see generated::scopes::mesh_s3_n2_p0
    template<> struct scope_binding<63> {
        [[nodiscard]] static sys::mesh::s3::n2::p0::context& get() noexcept
        { return generated::scopes::mesh_s3_n2_p0(); }
    };

    /// @brief `mesh.s3.n2.p1`. @see generated::scopes::mesh_s3_n2_p1
    template<> struct scope_binding<64> {
        [[nodiscard]] static sys::mesh::s3::n2::p1::context& get() noexcept
        { return generated::scopes::mesh_s3_n2_p1(); }
    };

    /// @brief `mesh.s3.n2.p2`. @see generated::scopes::mesh_s3_n2_p2
    template<> struct scope_binding<65> {
        [[nodiscard]] static sys::mesh::s3::n2::p2::context& get() noexcept
        { return generated::scopes::mesh_s3_n2_p2(); }
    };

    /// @brief `mesh.s3.n3`. @see generated::scopes::mesh_s3_n3
    template<> struct scope_binding<66> {
        [[nodiscard]] static sys::mesh::s3::n3::context& get() noexcept
        { return generated::scopes::mesh_s3_n3(); }
    };

    /// @brief `mesh.s3.n3.p0`. @see generated::scopes::mesh_s3_n3_p0
    template<> struct scope_binding<67> {
        [[nodiscard]] static sys::mesh::s3::n3::p0::context& get() noexcept
        { return generated::scopes::mesh_s3_n3_p0(); }
    };

    /// @brief `mesh.s3.n3.p1`. @see generated::scopes::mesh_s3_n3_p1
    template<> struct scope_binding<68> {
        [[nodiscard]] static sys::mesh::s3::n3::p1::context& get() noexcept
        { return generated::scopes::mesh_s3_n3_p1(); }
    };

    /// @brief `mesh.s3.n3.p2`. @see generated::scopes::mesh_s3_n3_p2
    template<> struct scope_binding<69> {
        [[nodiscard]] static sys::mesh::s3::n3::p2::context& get() noexcept
        { return generated::scopes::mesh_s3_n3_p2(); }
    };

    /// @brief `mesh.s4`. @see generated::scopes::mesh_s4
    template<> struct scope_binding<70> {
        [[nodiscard]] static sys::mesh::s4::context& get() noexcept
        { return generated::scopes::mesh_s4(); }
    };

    /// @brief `mesh.s4.n0`. @see generated::scopes::mesh_s4_n0
    template<> struct scope_binding<71> {
        [[nodiscard]] static sys::mesh::s4::n0::context& get() noexcept
        { return generated::scopes::mesh_s4_n0(); }
    };

    /// @brief `mesh.s4.n0.p0`. @see generated::scopes::mesh_s4_n0_p0
    template<> struct scope_binding<72> {
        [[nodiscard]] static sys::mesh::s4::n0::p0::context& get() noexcept
        { return generated::scopes::mesh_s4_n0_p0(); }
    };

    /// @brief `mesh.s4.n0.p1`. @see generated::scopes::mesh_s4_n0_p1
    template<> struct scope_binding<73> {
        [[nodiscard]] static sys::mesh::s4::n0::p1::context& get() noexcept
        { return generated::scopes::mesh_s4_n0_p1(); }
    };

    /// @brief `mesh.s4.n0.p2`. @see generated::scopes::mesh_s4_n0_p2
    template<> struct scope_binding<74> {
        [[nodiscard]] static sys::mesh::s4::n0::p2::context& get() noexcept
        { return generated::scopes::mesh_s4_n0_p2(); }
    };

    /// @brief `mesh.s4.n1`. @see generated::scopes::mesh_s4_n1
    template<> struct scope_binding<75> {
        [[nodiscard]] static sys::mesh::s4::n1::context& get() noexcept
        { return generated::scopes::mesh_s4_n1(); }
    };

    /// @brief `mesh.s4.n1.p0`. @see generated::scopes::mesh_s4_n1_p0
    template<> struct scope_binding<76> {
        [[nodiscard]] static sys::mesh::s4::n1::p0::context& get() noexcept
        { return generated::scopes::mesh_s4_n1_p0(); }
    };

    /// @brief `mesh.s4.n1.p1`. @see generated::scopes::mesh_s4_n1_p1
    template<> struct scope_binding<77> {
        [[nodiscard]] static sys::mesh::s4::n1::p1::context& get() noexcept
        { return generated::scopes::mesh_s4_n1_p1(); }
    };

    /// @brief `mesh.s4.n1.p2`. @see generated::scopes::mesh_s4_n1_p2
    template<> struct scope_binding<78> {
        [[nodiscard]] static sys::mesh::s4::n1::p2::context& get() noexcept
        { return generated::scopes::mesh_s4_n1_p2(); }
    };

    /// @brief `mesh.s4.n2`. @see generated::scopes::mesh_s4_n2
    template<> struct scope_binding<79> {
        [[nodiscard]] static sys::mesh::s4::n2::context& get() noexcept
        { return generated::scopes::mesh_s4_n2(); }
    };

    /// @brief `mesh.s4.n2.p0`. @see generated::scopes::mesh_s4_n2_p0
    template<> struct scope_binding<80> {
        [[nodiscard]] static sys::mesh::s4::n2::p0::context& get() noexcept
        { return generated::scopes::mesh_s4_n2_p0(); }
    };

    /// @brief `mesh.s4.n2.p1`. @see generated::scopes::mesh_s4_n2_p1
    template<> struct scope_binding<81> {
        [[nodiscard]] static sys::mesh::s4::n2::p1::context& get() noexcept
        { return generated::scopes::mesh_s4_n2_p1(); }
    };

    /// @brief `mesh.s4.n2.p2`. @see generated::scopes::mesh_s4_n2_p2
    template<> struct scope_binding<82> {
        [[nodiscard]] static sys::mesh::s4::n2::p2::context& get() noexcept
        { return generated::scopes::mesh_s4_n2_p2(); }
    };

    /// @brief `mesh.s4.n3`. @see generated::scopes::mesh_s4_n3
    template<> struct scope_binding<83> {
        [[nodiscard]] static sys::mesh::s4::n3::context& get() noexcept
        { return generated::scopes::mesh_s4_n3(); }
    };

    /// @brief `mesh.s4.n3.p0`. @see generated::scopes::mesh_s4_n3_p0
    template<> struct scope_binding<84> {
        [[nodiscard]] static sys::mesh::s4::n3::p0::context& get() noexcept
        { return generated::scopes::mesh_s4_n3_p0(); }
    };

    /// @brief `mesh.s4.n3.p1`. @see generated::scopes::mesh_s4_n3_p1
    template<> struct scope_binding<85> {
        [[nodiscard]] static sys::mesh::s4::n3::p1::context& get() noexcept
        { return generated::scopes::mesh_s4_n3_p1(); }
    };

    /// @brief `mesh.s4.n3.p2`. @see generated::scopes::mesh_s4_n3_p2
    template<> struct scope_binding<86> {
        [[nodiscard]] static sys::mesh::s4::n3::p2::context& get() noexcept
        { return generated::scopes::mesh_s4_n3_p2(); }
    };

    /// @brief `mesh.s5`. @see generated::scopes::mesh_s5
    template<> struct scope_binding<87> {
        [[nodiscard]] static sys::mesh::s5::context& get() noexcept
        { return generated::scopes::mesh_s5(); }
    };

    /// @brief `mesh.s5.n0`. @see generated::scopes::mesh_s5_n0
    template<> struct scope_binding<88> {
        [[nodiscard]] static sys::mesh::s5::n0::context& get() noexcept
        { return generated::scopes::mesh_s5_n0(); }
    };

    /// @brief `mesh.s5.n0.p0`. @see generated::scopes::mesh_s5_n0_p0
    template<> struct scope_binding<89> {
        [[nodiscard]] static sys::mesh::s5::n0::p0::context& get() noexcept
        { return generated::scopes::mesh_s5_n0_p0(); }
    };

    /// @brief `mesh.s5.n0.p1`. @see generated::scopes::mesh_s5_n0_p1
    template<> struct scope_binding<90> {
        [[nodiscard]] static sys::mesh::s5::n0::p1::context& get() noexcept
        { return generated::scopes::mesh_s5_n0_p1(); }
    };

    /// @brief `mesh.s5.n0.p2`. @see generated::scopes::mesh_s5_n0_p2
    template<> struct scope_binding<91> {
        [[nodiscard]] static sys::mesh::s5::n0::p2::context& get() noexcept
        { return generated::scopes::mesh_s5_n0_p2(); }
    };

    /// @brief `mesh.s5.n1`. @see generated::scopes::mesh_s5_n1
    template<> struct scope_binding<92> {
        [[nodiscard]] static sys::mesh::s5::n1::context& get() noexcept
        { return generated::scopes::mesh_s5_n1(); }
    };

    /// @brief `mesh.s5.n1.p0`. @see generated::scopes::mesh_s5_n1_p0
    template<> struct scope_binding<93> {
        [[nodiscard]] static sys::mesh::s5::n1::p0::context& get() noexcept
        { return generated::scopes::mesh_s5_n1_p0(); }
    };

    /// @brief `mesh.s5.n1.p1`. @see generated::scopes::mesh_s5_n1_p1
    template<> struct scope_binding<94> {
        [[nodiscard]] static sys::mesh::s5::n1::p1::context& get() noexcept
        { return generated::scopes::mesh_s5_n1_p1(); }
    };

    /// @brief `mesh.s5.n1.p2`. @see generated::scopes::mesh_s5_n1_p2
    template<> struct scope_binding<95> {
        [[nodiscard]] static sys::mesh::s5::n1::p2::context& get() noexcept
        { return generated::scopes::mesh_s5_n1_p2(); }
    };

    /// @brief `mesh.s5.n2`. @see generated::scopes::mesh_s5_n2
    template<> struct scope_binding<96> {
        [[nodiscard]] static sys::mesh::s5::n2::context& get() noexcept
        { return generated::scopes::mesh_s5_n2(); }
    };

    /// @brief `mesh.s5.n2.p0`. @see generated::scopes::mesh_s5_n2_p0
    template<> struct scope_binding<97> {
        [[nodiscard]] static sys::mesh::s5::n2::p0::context& get() noexcept
        { return generated::scopes::mesh_s5_n2_p0(); }
    };

    /// @brief `mesh.s5.n2.p1`. @see generated::scopes::mesh_s5_n2_p1
    template<> struct scope_binding<98> {
        [[nodiscard]] static sys::mesh::s5::n2::p1::context& get() noexcept
        { return generated::scopes::mesh_s5_n2_p1(); }
    };

    /// @brief `mesh.s5.n2.p2`. @see generated::scopes::mesh_s5_n2_p2
    template<> struct scope_binding<99> {
        [[nodiscard]] static sys::mesh::s5::n2::p2::context& get() noexcept
        { return generated::scopes::mesh_s5_n2_p2(); }
    };

    /// @brief `mesh.s5.n3`. @see generated::scopes::mesh_s5_n3
    template<> struct scope_binding<100> {
        [[nodiscard]] static sys::mesh::s5::n3::context& get() noexcept
        { return generated::scopes::mesh_s5_n3(); }
    };

    /// @brief `mesh.s5.n3.p0`. @see generated::scopes::mesh_s5_n3_p0
    template<> struct scope_binding<101> {
        [[nodiscard]] static sys::mesh::s5::n3::p0::context& get() noexcept
        { return generated::scopes::mesh_s5_n3_p0(); }
    };

    /// @brief `mesh.s5.n3.p1`. @see generated::scopes::mesh_s5_n3_p1
    template<> struct scope_binding<102> {
        [[nodiscard]] static sys::mesh::s5::n3::p1::context& get() noexcept
        { return generated::scopes::mesh_s5_n3_p1(); }
    };

    /// @brief `mesh.s5.n3.p2`. @see generated::scopes::mesh_s5_n3_p2
    template<> struct scope_binding<103> {
        [[nodiscard]] static sys::mesh::s5::n3::p2::context& get() noexcept
        { return generated::scopes::mesh_s5_n3_p2(); }
    };

    /// @brief `bus`. @see generated::scopes::bus
    template<> struct scope_binding<104> {
        [[nodiscard]] static sys::bus::context& get() noexcept
        { return generated::scopes::bus(); }
    };

    /// @brief `bus.link_state`. @see generated::scopes::bus_link_state
    template<> struct scope_binding<105> {
        [[nodiscard]] static sys::bus::link_state::context& get() noexcept
        { return generated::scopes::bus_link_state(); }
    };

    /// @brief `bus.link`. @see generated::scopes::bus_link
    template<> struct scope_binding<106> {
        [[nodiscard]] static sys::bus::link::context& get() noexcept
        { return generated::scopes::bus_link(); }
    };

    /// @brief `bus.reserve`. @see generated::scopes::bus_reserve
    template<> struct scope_binding<107> {
        [[nodiscard]] static sys::bus::reserve::context& get() noexcept
        { return generated::scopes::bus_reserve(); }
    };

} // namespace etask::core
#endif // GENERATED_SCOPES_HPP_
