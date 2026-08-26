// SPDX-License-Identifier: MIT
/**
* @file registry_traits.hpp
*
* @brief Shared uid-extraction metafunctions used by every manager.
*
* @ingroup etask_core etask::core::managers
*
* All three managers key their storage and dispatch on a task type's
* `static constexpr uid`, in two forms: the uid exactly as declared (so a
* strongly-typed enum stays one), and normalized to a raw integer (so it can
* index a table). Both live here rather than being repeated per manager, which
* also guarantees the three cannot drift in how they read a uid.
*
* @note Internal. Nothing outside `etask::core::managers` should name these.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-25
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_DETAIL_REGISTRY_TRAITS_HPP_
#define ETASK_CORE_MANAGERS_DETAIL_REGISTRY_TRAITS_HPP_
#include <etools/meta/info_gen.hpp>
#include <etools/meta/traits.hpp>
#include <etools/meta/utility.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <type_traits>

generate_has_static_member_variable(uid) ///< Compile-time check that a task declares `uid`.

namespace etask::core::managers::detail {

    /**
    * @struct uid_extractor
    *
    * @brief Exposes a task type's uid exactly as declared.
    *
    * Forwards `T::uid` without normalization, preserving its declared type
    * (e.g. a strongly-typed `enum class`) for APIs that traffic in the semantic
    * uid type rather than a raw integer.
    *
    * @tparam T A bare task type or a `capacity<Task, N>` tag; unwrapped before
    *           reading `uid`.
    */
    template<typename T>
    struct uid_extractor {
        static constexpr auto value = etools::factories::utils::as_capacity_t<T>::type::uid;
    };

    /**
    * @struct raw_uid_extractor
    *
    * @brief Normalizes a task type's uid to a raw integral value.
    *
    * Reads `T::uid`, strips cv-qualifiers, and - if it is an enumeration -
    * converts to its underlying integral type. The result is suitable as a table
    * key or array index.
    *
    * @tparam T Task type exposing a `static constexpr uid`.
    *
    * #### Provided aliases
    * - `uid_t` : the declared type of `T::uid`, cv-stripped
    * - `raw_t` : `uid_t` if integral, otherwise its underlying type
    *
    * #### Provided constants
    * - `value` : `static_cast<raw_t>(T::uid)`
    */
    template<typename T>
    struct raw_uid_extractor {
        /// @brief The declared type of `T::uid`, with cv-qualifiers removed.
        using uid_t = std::remove_cv_t<decltype(T::uid)>;

        /// @brief `uid_t` reduced to an integral type (its underlying type, if an enum).
        using raw_t = typename std::conditional_t<
            std::is_enum_v<uid_t>,
            std::underlying_type<uid_t>,        // trait (lazy)
            etools::meta::type_identity<uid_t>  // trait (lazy)
        >::type;

        static_assert(
            std::is_integral_v<raw_t>,
            "uid must be an integral type or an enum with an integral underlying type"
        );

        static constexpr auto value = static_cast<raw_t>(T::uid);
    };

    /**
    * @var is_capacity_v
    *
    * @brief Whether `T` is a `capacity<Task, N>` tag rather than a bare task type.
    *
    * `as_capacity_t` deliberately erases this distinction - it normalizes both
    * forms to the same shape, which is what the storage-owning managers want.
    * This asks the question it normalizes away, for the one manager that must
    * reject the tag outright (@ref instant_task_manager).
    *
    * @tparam T A pack element from a manager's task list.
    */
    template<typename T>
    inline constexpr bool is_capacity_v = false;

    /// @brief Specialization recognizing the tag itself. @see is_capacity_v
    template<typename Task, std::size_t N>
    inline constexpr bool is_capacity_v<etools::factories::utils::capacity<Task, N>> = true;

    /**
    * @typedef raw_uid_t
    *
    * @brief `UidT` normalized to a raw integral type.
    *
    * The same normalization @ref raw_uid_extractor applies, expressed over the
    * uid *type* rather than over a task type - for managers that need to name
    * the raw form in a signature.
    *
    * @tparam UidT A task uid type (an integral type or an enum over one).
    */
    template<typename UidT>
    using raw_uid_t = typename std::conditional_t<
        std::is_enum_v<UidT>,
        std::underlying_type<UidT>,
        etools::meta::type_identity<UidT>
    >::type;

} // namespace etask::core::managers::detail

#endif // ETASK_CORE_MANAGERS_DETAIL_REGISTRY_TRAITS_HPP_
