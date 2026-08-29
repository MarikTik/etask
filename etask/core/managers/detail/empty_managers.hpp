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
* of these rather than special-casing every call site, and - because the stand-in
* is an empty class held as a base (see @ref tier_storage) - an unused tier adds
* nothing to the manager's size.
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
#include <cstddef>
#include <type_traits>

namespace etask::core::managers {

    // Forward declarations: this header names the three managers only to alias
    // them, and each of their own headers includes this one.
    template<typename ...Tasks> class instant_task_manager;
    template<std::size_t Budget, typename ...Tasks> class polled_task_manager;
    template<std::size_t Budget, typename ...Tasks> class stateful_task_manager;

namespace detail {

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
        /// @brief Default-constructed; there is nothing to size or reserve.
        absent_tier() noexcept = default;

        /// @brief No tasks, so no demand on the payload.
        static constexpr std::size_t max_params_size = 0;

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
    * @struct tier_storage
    *
    * @brief Holds one sub-manager as a base class, so an absent tier is free.
    *
    * @ref task_manager needs three sub-managers, any of which may be an empty
    * @ref absent_tier. Held as *members*, three empty classes would still occupy
    * three distinct addresses and pad the manager out; `[[no_unique_address]]`
    * fixes that in C++20, but this project is C++17, where GCC and Clang accept
    * the attribute only as a non-standard extension - so a stricter toolchain
    * would silently grow the object.
    *
    * Empty **base** optimization has been guaranteed since C++98 and needs no
    * attribute, so each tier is *inherited* rather than held. The wrapper must
    * inherit from the manager too, not contain it: a wrapper holding an empty
    * class as a member is itself non-empty, and inheriting from that optimizes
    * nothing. `Index` keeps the three wrappers distinct types even when two
    * tiers are both `absent_tier`, which plain triple inheritance could not
    * express (a class cannot derive from the same base twice).
    *
    * @note Every tier is default-constructible: a manager's storage is sized by
    *       its `Budget` template parameter, so there is no runtime load hint to
    *       forward and no second specialization to keep in step.
    *
    * @tparam Index Distinguishes the three bases; carries no other meaning.
    * @tparam Manager The sub-manager type held here.
    */
    template<std::size_t Index, typename Manager>
    struct tier_storage : Manager {
        /// @brief The sub-manager, reached as a base.
        [[nodiscard]] Manager& tier() noexcept { return *this; }
    };

    /**
    * @typedef manager_for_t
    *
    * @brief `Manager<Tasks...>` for a populated list, @ref absent_tier for an
    *        empty one.
    *
    * `List::apply<Manager>` does the unpacking; the only thing left to decide is
    * whether to unpack at all, since a manager instantiated with no tasks would
    * reject itself.
    *
    * @tparam Manager The sub-manager template to instantiate.
    * @tparam List    Typelist of that tier's task types.
    */
    template<template<typename...> class Manager, typename List>
    using manager_for_t = std::conditional_t<
        List::is_empty(),
        absent_tier,
        typename List::template apply<Manager>>;

    /**
    * @struct list_capacity
    *
    * @brief Sum of the reserved slots across a *typelist* of tasks.
    *
    * @ref sum_of_capacities_v answers this for a parameter pack; the façade holds
    * typelists, and needs the same number to default a tier's budget with.
    *
    * @tparam List A tier's typelist of task types.
    */
    template<typename List>
    struct list_capacity;

    /// @brief The general case. @see list_capacity
    template<typename... Tasks>
    struct list_capacity<etools::meta::typelist<Tasks...>> {
        /// @brief The sum; zero for an empty list.
        static constexpr std::size_t value = sum_of_capacities_v<Tasks...>;
    };

    /**
    * @var default_budget_v
    *
    * @brief A tier's default budget: every task at its own cap simultaneously.
    *
    * The only bound derivable without knowing how the application behaves, and so
    * what a tier gets when the project has not measured and declared its real
    * peak.
    *
    * @tparam List A tier's typelist of task types.
    */
    template<typename List>
    inline constexpr std::size_t default_budget_v = list_capacity<List>::value;

    /**
    * @struct budgeted
    *
    * @brief Binds a budget to a managed-tier template, leaving a plain
    *        `template<typename...>` for a typelist to apply.
    *
    * The two managed managers take their budget as a leading non-type parameter,
    * which `typelist::apply` - which supplies types only - cannot pass. Currying
    * it here turns `Manager<Budget, Tasks...>` back into something shaped like
    * `Manager<Tasks...>` at the point of application.
    *
    * @tparam Manager The sub-manager template, taking a budget then a task pack.
    * @tparam Budget  The budget to bind.
    */
    template<template<std::size_t, typename...> class Manager, std::size_t Budget>
    struct budgeted {
        /// @brief The task pack, with `Budget` already supplied.
        template<typename... Tasks>
        using type = Manager<Budget, Tasks...>;
    };

    /**
    * @typedef managed_tier_t
    *
    * @brief `Manager<Budget, Tasks...>` for a populated list, @ref absent_tier for
    *        an empty one.
    *
    * The budgeted counterpart to @ref manager_for_t, for the two tiers that own
    * storage. A budget of zero selects the stand-in as surely as an empty list
    * does: a tier that may hold no live task cannot run one, and the managers
    * reject `Budget == 0` outright rather than instantiating something inert.
    *
    * @tparam Manager The sub-manager template to instantiate.
    * @tparam List    Typelist of that tier's task types.
    * @tparam Budget  Maximum concurrently live tasks for the tier.
    */
    template<template<std::size_t, typename...> class Manager, typename List, std::size_t Budget>
    using managed_tier_t = std::conditional_t<
        List::is_empty() or Budget == 0,
        absent_tier,
        typename List::template apply<budgeted<Manager, Budget>::template type>>;

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
    * @struct declares_uid
    *
    * @brief Predicate: does `Task` declare the uid this instantiation carries?
    *
    * Bound to a specific uid value through @ref uid_probe, so it can be handed to
    * `typelist::any_of` - which takes a one-parameter predicate template.
    *
    * @tparam RawUid The raw uid type.
    * @tparam Value  The uid value to test against.
    */
    template<typename RawUid, RawUid Value>
    struct uid_probe {
        /**
        * @brief The predicate itself: `Task`'s uid equals `Value`.
        * @tparam Task A task type from a tier's list.
        */
        template<typename Task>
        struct declares : std::bool_constant<
            static_cast<RawUid>(raw_uid_extractor<
                typename etools::factories::utils::as_capacity_t<Task>::type>::value) == Value> {};
    };

    /**
    * @brief Whether two tiers share no task uid between them.
    *
    * Walks `Left`'s tasks, asking `Right` - via `typelist::any_of` and the
    * @ref uid_probe predicate - whether anything there declares the same uid.
    *
    * @tparam Left  One tier's typelist.
    * @tparam Right The other's.
    * @return `true` if the two share no uid.
    */
    template<typename Left, typename Right>
    [[nodiscard]] constexpr bool no_shared_uid() noexcept;

    /// @brief Walks `Left`'s task uids. @see no_shared_uid
    template<typename Right, typename... LeftTasks>
    [[nodiscard]] constexpr bool none_shared(etools::meta::typelist<LeftTasks...>) noexcept {
        if constexpr (sizeof...(LeftTasks) == 0) {
            return true;
        }
        else {
            return not (Right::template any_of<
                uid_probe<
                    decltype(raw_uid_extractor<
                        typename etools::factories::utils::as_capacity_t<LeftTasks>::type>::value),
                    raw_uid_extractor<
                        typename etools::factories::utils::as_capacity_t<LeftTasks>::type>::value
                >::template declares>() or ...);
        }
    }

    template<typename Left, typename Right>
    [[nodiscard]] constexpr bool no_shared_uid() noexcept {
        return none_shared<Right>(Left{});
    }

    /**
    * @var tiers_are_disjoint_v
    *
    * @brief Whether no task **uid** is claimed by more than one of the three tiers.
    *
    * Not `typelist::disjoint`, which compares *types*: two distinct C++ classes
    * can each declare `uid = 5`, and that must be rejected too. Each sub-manager
    * enforces uniqueness within itself; only the façade can see across tiers, so
    * this catches a uid listed twice in different lists - which would otherwise
    * route to whichever tier was tested first, silently shadowing the other task.
    *
    * @tparam InstantTasks  Typelist of instant commands.
    * @tparam PolledTasks   Typelist of polled tasks.
    * @tparam StatefulTasks Typelist of stateful tasks.
    */
    template<typename InstantTasks, typename PolledTasks, typename StatefulTasks>
    inline constexpr bool tiers_are_disjoint_v =
        no_shared_uid<InstantTasks, PolledTasks>() and
        no_shared_uid<InstantTasks, StatefulTasks>() and
        no_shared_uid<PolledTasks, StatefulTasks>();

} // namespace detail
} // namespace etask::core::managers

#endif // ETASK_CORE_MANAGERS_DETAIL_EMPTY_MANAGERS_HPP_
