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
#include "../sys/rotors/context.hpp"
#include "../sys/rotors/fl/context.hpp"
#include "../sys/rotors/fr/context.hpp"
#include "../sys/rotors/rl/context.hpp"
#include "../sys/rotors/rr/context.hpp"
#include "../sys/sensors/context.hpp"
#include "../sys/sensors/imu/context.hpp"
#include "../sys/sensors/baro/context.hpp"
#include "../sys/sensors/gps/context.hpp"
#include "../sys/nav/context.hpp"
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
    * @brief The `context` of `rotors`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::rotors::context& rotors() noexcept
    {
        return detail::tree().rotors;
    }

    /**
    * @brief The `context` of `rotors.fl`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::rotors::fl::context& rotors_fl() noexcept
    {
        return detail::tree().rotors.fl;
    }

    /**
    * @brief The `context` of `rotors.fr`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::rotors::fr::context& rotors_fr() noexcept
    {
        return detail::tree().rotors.fr;
    }

    /**
    * @brief The `context` of `rotors.rl`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::rotors::rl::context& rotors_rl() noexcept
    {
        return detail::tree().rotors.rl;
    }

    /**
    * @brief The `context` of `rotors.rr`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::rotors::rr::context& rotors_rr() noexcept
    {
        return detail::tree().rotors.rr;
    }

    /**
    * @brief The `context` of `sensors`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::sensors::context& sensors() noexcept
    {
        return detail::tree().sensors;
    }

    /**
    * @brief The `context` of `sensors.imu`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::sensors::imu::context& sensors_imu() noexcept
    {
        return detail::tree().sensors.imu;
    }

    /**
    * @brief The `context` of `sensors.baro`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::sensors::baro::context& sensors_baro() noexcept
    {
        return detail::tree().sensors.baro;
    }

    /**
    * @brief The `context` of `sensors.gps`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::sensors::gps::context& sensors_gps() noexcept
    {
        return detail::tree().sensors.gps;
    }

    /**
    * @brief The `context` of `nav`.
    *
    * Bound as the scope argument of every task in it (see
    * `etask::core::scoped_task_unpack_adapter`). Inlines to a member offset
    * into the one context tree - there is no lookup and no indirection.
    */
    [[nodiscard]] inline sys::nav::context& nav() noexcept
    {
        return detail::tree().nav;
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

    /// @brief `rotors`. @see generated::scopes::rotors
    template<> struct scope_binding<1> {
        [[nodiscard]] static sys::rotors::context& get() noexcept
        { return generated::scopes::rotors(); }
    };

    /// @brief `rotors.fl`. @see generated::scopes::rotors_fl
    template<> struct scope_binding<2> {
        [[nodiscard]] static sys::rotors::fl::context& get() noexcept
        { return generated::scopes::rotors_fl(); }
    };

    /// @brief `rotors.fr`. @see generated::scopes::rotors_fr
    template<> struct scope_binding<3> {
        [[nodiscard]] static sys::rotors::fr::context& get() noexcept
        { return generated::scopes::rotors_fr(); }
    };

    /// @brief `rotors.rl`. @see generated::scopes::rotors_rl
    template<> struct scope_binding<4> {
        [[nodiscard]] static sys::rotors::rl::context& get() noexcept
        { return generated::scopes::rotors_rl(); }
    };

    /// @brief `rotors.rr`. @see generated::scopes::rotors_rr
    template<> struct scope_binding<5> {
        [[nodiscard]] static sys::rotors::rr::context& get() noexcept
        { return generated::scopes::rotors_rr(); }
    };

    /// @brief `sensors`. @see generated::scopes::sensors
    template<> struct scope_binding<6> {
        [[nodiscard]] static sys::sensors::context& get() noexcept
        { return generated::scopes::sensors(); }
    };

    /// @brief `sensors.imu`. @see generated::scopes::sensors_imu
    template<> struct scope_binding<7> {
        [[nodiscard]] static sys::sensors::imu::context& get() noexcept
        { return generated::scopes::sensors_imu(); }
    };

    /// @brief `sensors.baro`. @see generated::scopes::sensors_baro
    template<> struct scope_binding<8> {
        [[nodiscard]] static sys::sensors::baro::context& get() noexcept
        { return generated::scopes::sensors_baro(); }
    };

    /// @brief `sensors.gps`. @see generated::scopes::sensors_gps
    template<> struct scope_binding<9> {
        [[nodiscard]] static sys::sensors::gps::context& get() noexcept
        { return generated::scopes::sensors_gps(); }
    };

    /// @brief `nav`. @see generated::scopes::nav
    template<> struct scope_binding<10> {
        [[nodiscard]] static sys::nav::context& get() noexcept
        { return generated::scopes::nav(); }
    };

} // namespace etask::core
#endif // GENERATED_SCOPES_HPP_
