// SPDX-License-Identifier: MIT
/**
* @file registered_task.hpp
*
* @brief Turns a task type into the type a manager actually stores.
*
* @ingroup etask_core etask::core::managers
*
* ## The mismatch this resolves
*
* A schema-generated task has a *native-typed* constructor:
*
* @code
* set_thrust(float level, context& ctx);
* @endcode
*
* but a task arrives over the wire as an opaque payload, and the registry
* constructs from exactly one `etools::memory::buffer_view`. The two do not
* meet, and because the registry's branch is SFINAE-guarded, a native-ctor task
* would simply never be constructible - registration failing with
* `task_unknown` and no indication why.
*
* @ref task_unpack_adapter is the bridge: it *is* the task, plus one constructor
* that unpacks the payload into the native argument types. This header decides,
* per task, whether that bridge is needed and which form of it to use - so a
* manager stores `registered_t<Task>` rather than `Task`, and nothing else in
* the framework has to think about it.
*
* ## Why the manager, and not the generated task list
*
* The task list says *what the tasks are*. How a manager builds one from wire
* bytes is the manager's own business, and naming the adapter in the generated
* list would leak a construction detail into a file that should only name task
* types. So the list stays clean and the wrapping happens here.
*
* ## What a task must declare
*
* Nothing, if it is constructible from a `buffer_view` already - it is stored
* as-is. Otherwise the generator gives the class two things the adapter needs
* and that cannot be recovered from the type:
*
* - `using params = etools::meta::typelist<Args...>` - the constructor's
*   parameter types, in wire order. A signature cannot be introspected in C++17,
*   and the wire order is the schema's contract, so it is declared.
* - `static constexpr auto scope = &some_accessor;` - for a task in a scope,
*   a nullary function returning its `context&`. Absent for a scopeless task.
*
* @note Internal. Nothing outside `etask::core::managers` should name these.
*
* @author Mark Tikhonov <mtik.philosopher@gmail.com>
*
* @date 2026-08-26
*
* @copyright
* MIT License
* Copyright (c) 2026 Mark Tikhonov
* See LICENSE file for details.
*/
#ifndef ETASK_CORE_MANAGERS_DETAIL_REGISTERED_TASK_HPP_
#define ETASK_CORE_MANAGERS_DETAIL_REGISTERED_TASK_HPP_
#include "../../task_unpack_adapter.hpp"
#include <etools/meta/typelist.hpp>
#include <etools/memory/buffer_view.hpp>
#include <etools/factories/utils/capacity.hpp>
#include <type_traits>

namespace etask::core::managers::detail {

    /**
    * @var declares_params_v
    *
    * @brief Whether `Task` names its constructor parameter types.
    *
    * A generated task with a native constructor declares
    * `using params = etools::meta::typelist<Args...>`; one without a
    * `buffer_view` constructor and without this cannot be built from a payload
    * at all, which @ref registered_task reports.
    *
    * @tparam Task A task type.
    */
    template<typename Task, typename = void>
    inline constexpr bool declares_params_v = false;

    /// @brief Populated case. @see declares_params_v
    template<typename Task>
    inline constexpr bool declares_params_v<Task, std::void_t<typename Task::params>> = true;

    /**
    * @var declares_scope_v
    *
    * @brief Whether `Task` names the scope it is injected with.
    *
    * A task inside a schema scope takes its `context&` as the last constructor
    * argument, and declares `static constexpr scope_index_t scope = N;` - an
    * index into `scope_binding`, which `generated/scopes.hpp` specializes - so
    * the adapter can supply it. A scopeless task declares nothing.
    *
    * @tparam Task A task type.
    */
    template<typename Task, typename = void>
    inline constexpr bool declares_scope_v = false;

    /// @brief Populated case. @see declares_scope_v
    template<typename Task>
    inline constexpr bool declares_scope_v<Task, std::void_t<decltype(Task::scope)>> = true;

    /**
    * @struct adapted
    *
    * @brief `task_unpack_adapter<Task, Args...>` for a task's declared params.
    *
    * Exists to unpack the `params` typelist into the adapter's parameter pack;
    * `typelist::apply` cannot be used directly because `Task` has to be the
    * adapter's *first* argument, ahead of the list's own types.
    *
    * @tparam Task   The task being wrapped.
    * @tparam Params The task's `params` typelist.
    */
    template<typename Task, typename Params>
    struct adapted;

    /// @brief The general case. @see adapted
    template<typename Task, typename... Args>
    struct adapted<Task, etools::meta::typelist<Args...>> {
        using type = task_unpack_adapter<Task, Args...>;
    };

    /**
    * @struct scope_adapted
    *
    * @brief `scoped_task_unpack_adapter<Task, Task::scope, Args...>` for a task
    *        that is injected with a scope.
    *
    * @tparam Task   The task being wrapped.
    * @tparam Params The task's `params` typelist (its parameters *before* the
    *                trailing `context&`, which the accessor supplies).
    */
    template<typename Task, typename Params>
    struct scope_adapted;

    /// @brief The general case. @see scope_adapted
    template<typename Task, typename... Args>
    struct scope_adapted<Task, etools::meta::typelist<Args...>> {
        using type = scoped_task_unpack_adapter<Task, Task::scope, Args...>;
    };

    /**
    * @struct registered_task
    *
    * @brief The type a manager stores for `Task`: the task itself, or the
    *        adapter that can build it from a payload.
    *
    * Three cases, in order:
    *
    * 1. `Task` is already constructible from a `buffer_view` - a hand-written
    *    task that takes the payload itself. Stored as-is; nothing is wrapped.
    * 2. `Task` declares `params` and a `scope` - wrapped in
    *    @ref scoped_task_unpack_adapter, which unpacks the payload and appends
    *    the scope reference.
    * 3. `Task` declares `params` alone - wrapped in @ref task_unpack_adapter.
    *
    * A task matching none of them is stored unchanged. That is not an error: a
    * task with a native constructor and no `params` simply cannot be reached
    * from the wire, which is perfectly sensible for one that is only ever
    * started in-process (`internal_channel::register_task(uid, args...)`, whose
    * caller already holds the typed arguments). Rejecting it here would forbid a
    * legitimate design; a wire request for such a uid fails to construct and is
    * reported as `task_unknown`, which is what it is.
    *
    * Wrapping never removes the native constructor - the adapters inherit it
    * with `using Task::Task` - so a wrapped task is still constructible both
    * ways, and the in-process path never pays for a payload round-trip.
    *
    * @tparam Task A bare task type (already unwrapped from any `capacity` tag).
    */
    template<typename Task, typename = void>
    struct registered_task {
        using type = Task;
    };

    /// @brief Case 1: already payload-constructible, so it is stored unchanged.
    template<typename Task>
    struct registered_task<
        Task,
        std::enable_if_t<std::is_constructible_v<Task, etools::memory::buffer_view>>>
    {
        using type = Task;
    };

    /// @brief Cases 2 and 3: wrap in the adapter its declarations call for.
    template<typename Task>
    struct registered_task<
        Task,
        std::enable_if_t<
            not std::is_constructible_v<Task, etools::memory::buffer_view>
            and declares_params_v<Task>>>
    {
        using type = typename std::conditional_t<
            declares_scope_v<Task>,
            scope_adapted<Task, typename Task::params>,
            adapted<Task, typename Task::params>>::type;
    };

    /**
    * @typedef registered_t
    *
    * @brief The stored type for a manager pack element, `capacity` tag preserved.
    *
    * Wraps the *underlying* task and re-applies the element's reserved slot
    * count, so `capacity<Task, 4>` becomes `capacity<adapter-of-Task, 4>` and a
    * bare task becomes the bare adapter. The registry keys on the adapter, which
    * inherits `Task::uid`, so uid routing is unchanged.
    *
    * @tparam T A bare task type or a `capacity<Task, N>` tag.
    */
    template<typename T>
    using registered_t = etools::factories::utils::capacity<
        typename registered_task<
            typename etools::factories::utils::as_capacity_t<T>::type>::type,
        etools::factories::utils::as_capacity_t<T>::count>;

} // namespace etask::core::managers::detail

#endif // ETASK_CORE_MANAGERS_DETAIL_REGISTERED_TASK_HPP_
