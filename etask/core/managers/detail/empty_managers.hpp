// SPDX-License-Identifier: MIT
/**
* @file empty_managers.hpp
*
* @brief Lets @ref task_manager hold a tier that has no tasks, at no cost.
*
* @ingroup etask_core etask::core::managers
*
* A real sub-manager cannot be instantiated with an empty task pack - it would
* have no uid type to deduce and nothing to dispatch to, and each one rejects
* that outright. But a project legitimately may have no tasks in a tier: a robot
* built entirely from fire-and-forget commands has nothing to poll, and one with
* nothing to suspend has nothing stateful.
*
* So an empty tier selects an **inert stand-in** instead: same entry points,
* every one answering "not mine", no storage, no code. The façade then holds one
* of these rather than special-casing every call site, and - combined with
* `[[no_unique_address]]` - an unused tier adds nothing to the manager's size.
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
#ifndef ETASK_CORE_MANAGERS_DETAIL_EMPTY_MANAGERS_HPP_
#define ETASK_CORE_MANAGERS_DETAIL_EMPTY_MANAGERS_HPP_
#include "registry_traits.hpp"
#include <etools/meta/typelist.hpp>
#include <array>
#include <cstddef>
#include <type_traits>

namespace etask::core::managers {

    // Forward declarations: this header names the three managers only to alias
    // them, and each of their own headers includes this one.
    template<typename ...Tasks> class instant_task_manager;
    template<typename ...Tasks> class polled_task_manager;
    template<typename ...Tasks> class stateful_task_manager;

namespace detail {

    /**
    * @var is_empty_list_v
    *
    * @brief Whether `List` is a typelist with no types in it.
    *
    * @tparam List An `etools::meta::typelist`.
    */
    template<typename List>
    inline constexpr bool is_empty_list_v = false;

    /// @brief The empty case. @see is_empty_list_v
    template<>
    inline constexpr bool is_empty_list_v<etools::meta::typelist<>> = true;

    /**
    * @class absent_tier
    *
    * @brief The stand-in for a tier with no tasks: answers every query with "not
    *        mine", holds nothing, does nothing.
    *
    * Every entry point the façade might route here exists, so the façade's code
    * is the same shape whether a tier is populated or not - but each is a
    * constant `false` or a no-op the optimizer removes entirely. It declares no
    * `task_uid_t`, which is what keeps an absent tier out of the project's uid
    * type deduction (see @ref common_uid_t).
    */
    class absent_tier {
    public:
        /// @brief Constructed with the façade's task-load hint, which it ignores.
        explicit absent_tier(std::size_t = 0) noexcept {}

        /**
        * @brief Never owns anything.
        * @return Always `false`.
        */
        template<typename RawUid>
        [[nodiscard]] static constexpr bool owns(RawUid) noexcept { return false; }

        /// @brief Nothing to drive.
        void update() noexcept {}
    };

    /**
    * @typedef instant_manager_for_t
    *
    * @brief `instant_task_manager<Tasks...>` for a populated list, @ref absent_tier
    *        for an empty one.
    *
    * @tparam List Typelist of instant commands.
    */
    template<typename List>
    struct instant_manager_for { using type = absent_tier; };

    /// @brief Populated case. @see instant_manager_for
    template<typename... Tasks>
    struct instant_manager_for<etools::meta::typelist<Tasks...>> {
        using type = std::conditional_t<
            sizeof...(Tasks) == 0, absent_tier, instant_task_manager<Tasks...>>;
    };

    /// @brief Alias for `instant_manager_for<List>::type`.
    template<typename List>
    using instant_manager_for_t = typename instant_manager_for<List>::type;

    /**
    * @typedef polled_manager_for_t
    *
    * @brief `polled_task_manager<Tasks...>` for a populated list, @ref absent_tier
    *        for an empty one.
    *
    * @tparam List Typelist of polled tasks.
    */
    template<typename List>
    struct polled_manager_for { using type = absent_tier; };

    /// @brief Populated case. @see polled_manager_for
    template<typename... Tasks>
    struct polled_manager_for<etools::meta::typelist<Tasks...>> {
        using type = std::conditional_t<
            sizeof...(Tasks) == 0, absent_tier, polled_task_manager<Tasks...>>;
    };

    /// @brief Alias for `polled_manager_for<List>::type`.
    template<typename List>
    using polled_manager_for_t = typename polled_manager_for<List>::type;

    /**
    * @typedef stateful_manager_for_t
    *
    * @brief `stateful_task_manager<Tasks...>` for a populated list,
    *        @ref absent_tier for an empty one.
    *
    * @tparam List Typelist of stateful tasks.
    */
    template<typename List>
    struct stateful_manager_for { using type = absent_tier; };

    /// @brief Populated case. @see stateful_manager_for
    template<typename... Tasks>
    struct stateful_manager_for<etools::meta::typelist<Tasks...>> {
        using type = std::conditional_t<
            sizeof...(Tasks) == 0, absent_tier, stateful_task_manager<Tasks...>>;
    };

    /// @brief Alias for `stateful_manager_for<List>::type`.
    template<typename List>
    using stateful_manager_for_t = typename stateful_manager_for<List>::type;

    /**
    * @struct tier_uid
    *
    * @brief A tier's `task_uid_t`, or nothing at all for an absent one.
    *
    * @tparam Manager A sub-manager type, possibly @ref absent_tier.
    */
    template<typename Manager, typename = void>
    struct tier_uid {};

    /// @brief Populated case: the manager names its own uid type. @see tier_uid
    template<typename Manager>
    struct tier_uid<Manager, std::void_t<typename Manager::task_uid_t>> {
        using type = typename Manager::task_uid_t;
    };

    /**
    * @var has_uid_v
    *
    * @brief Whether `Manager` names a `task_uid_t` - i.e. is a populated tier.
    *
    * @tparam Manager A sub-manager type, possibly @ref absent_tier.
    */
    template<typename Manager, typename = void>
    inline constexpr bool has_uid_v = false;

    /// @brief Populated case. @see has_uid_v
    template<typename Manager>
    inline constexpr bool has_uid_v<Manager, std::void_t<typename Manager::task_uid_t>> = true;

    /**
    * @struct first_uid
    *
    * @brief The uid type of the first populated tier, skipping absent ones.
    *
    * @tparam Managers The sub-manager types, in order.
    */
    template<typename... Managers>
    struct first_uid;

    /**
    * @brief A populated head ends the search; otherwise recurse into the tail.
    *
    * `std::conditional_t` picks the *metafunction* to evaluate, and only the
    * chosen branch's `::type` is instantiated - so recursing past an absent tier
    * never asks it for a uid it does not have.
    *
    * @see first_uid
    */
    template<typename Head, typename... Tail>
    struct first_uid<Head, Tail...>
        : std::conditional_t<has_uid_v<Head>, tier_uid<Head>, first_uid<Tail...>> {};

    /**
    * @brief Terminal case: every tier was absent.
    *
    * Unreachable in practice - @ref task_manager rejects three empty tiers with a
    * clearer message before this is ever instantiated.
    */
    template<>
    struct first_uid<> {};

    /**
    * @typedef common_uid_t
    *
    * @brief The project's task uid type, from whichever tiers are populated.
    *
    * Absent tiers contribute nothing. Every populated tier must agree: one
    * project has one uid space, and a mismatch means two tiers were generated
    * from different schemas.
    *
    * @tparam Managers The three sub-manager types.
    */
    template<typename... Managers>
    using common_uid_t = typename first_uid<Managers...>::type;

    /**
    * @struct tier_uids
    *
    * @brief Membership queries over the uids a typelist's tasks declare.
    *
    * @tparam List A typelist of task types (bare or `capacity`-tagged).
    */
    template<typename List>
    struct tier_uids;

    /// @brief The general case. @see tier_uids
    template<typename... Tasks>
    struct tier_uids<etools::meta::typelist<Tasks...>> {
        /**
        * @brief Whether `raw` is declared by any task in this list.
        *
        * @tparam RawUid The raw uid type.
        * @param raw The uid to look for.
        * @return `true` if some task in the list declares it.
        */
        template<typename RawUid>
        static constexpr bool contains([[maybe_unused]] RawUid raw) noexcept {
            if constexpr (sizeof...(Tasks) == 0)
                return false;
            else
                return ((static_cast<RawUid>(raw_uid_extractor<
                    typename etools::factories::utils::as_capacity_t<Tasks>::type>::value) == raw) or ...);
        }
    };

    /**
    * @brief Whether two tiers share any uid between them.
    *
    * @tparam Left  One typelist of task types.
    * @tparam Right The other.
    * @return `true` if some uid appears in both.
    */
    template<typename Left, typename Right>
    constexpr bool tiers_overlap() noexcept;

    /// @brief Walks `Left`'s uids, asking `Right` about each. @see tiers_overlap
    template<typename Right, typename... LeftTasks>
    constexpr bool overlaps_any(etools::meta::typelist<LeftTasks...>) noexcept {
        if constexpr (sizeof...(LeftTasks) == 0)
            return false;
        else
            return (tier_uids<Right>::contains(
                raw_uid_extractor<
                    typename etools::factories::utils::as_capacity_t<LeftTasks>::type>::value) or ...);
    }

    template<typename Left, typename Right>
    constexpr bool tiers_overlap() noexcept {
        return overlaps_any<Right>(Left{});
    }

    /**
    * @var tiers_are_disjoint_v
    *
    * @brief Whether no uid is claimed by more than one of the three tiers.
    *
    * Each sub-manager enforces uniqueness within itself; only the façade can see
    * across tiers, so this is the check that catches a uid listed twice in
    * different lists - which would otherwise route to whichever tier was tested
    * first, silently shadowing the other task.
    *
    * @tparam InstantTasks  Typelist of instant commands.
    * @tparam PolledTasks   Typelist of polled tasks.
    * @tparam StatefulTasks Typelist of stateful tasks.
    */
    template<typename InstantTasks, typename PolledTasks, typename StatefulTasks>
    inline constexpr bool tiers_are_disjoint_v =
        not tiers_overlap<InstantTasks, PolledTasks>() and
        not tiers_overlap<InstantTasks, StatefulTasks>() and
        not tiers_overlap<PolledTasks, StatefulTasks>();

} // namespace detail
} // namespace etask::core::managers

#endif // ETASK_CORE_MANAGERS_DETAIL_EMPTY_MANAGERS_HPP_
